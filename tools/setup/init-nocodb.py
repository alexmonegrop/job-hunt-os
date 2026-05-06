"""init-nocodb.py — discover NocoDB base id + link-field ids and write to .env.

Run after `docker compose up -d` and after NocoDB has discovered the postgres
`jobhunt` database as a Data Source. This script does NOT create the schema —
the schema is created by `infrastructure/init-db/02-jobhunt-schema.sql` when
postgres first boots.

What it does:
  1. Reads NOCODB_URL and NOCODB_API_TOKEN from the project .env.
  2. Queries the NocoDB v2 meta API to find the base containing the
     job-hunt-os tables (target_companies, target_contacts, etc.).
  3. Queries each table's columns to find the LinkToAnotherRecord field ids
     used for FK linking via the v3 Link API (see
     .claude/rules/01-database-standards.md Rule 8).
  4. Writes NOCODB_BASE_ID and link-field ids back to the .env at the
     repo root.

Manual prerequisites:
  - `docker compose up -d` has run successfully.
  - You have logged into NocoDB at http://localhost:8080 and created an
    admin user.
  - You have generated an API token at Account -> Tokens and pasted it into
    the project .env as NOCODB_API_TOKEN.
  - You have added the postgres `jobhunt` database as a Data Source inside
    NocoDB (Settings -> Data Sources -> + New). Connection details:
      host: postgres (or localhost if running outside the Docker network)
      port: 5432
      user: jobhunt
      password: <POSTGRES_PASSWORD from infrastructure/.env>
      database: jobhunt
  - NocoDB has discovered all 7 tables.

Usage:
  python tools/setup/init-nocodb.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

try:
    import requests
except ImportError:
    sys.exit(
        "Missing dependency: requests. Install with `pip install requests`."
    )

EXPECTED_TABLES = {
    "users",
    "target_companies",
    "target_contacts",
    "sales_pipeline",
    "interactions",
    "job_postings",
    "applications",
}

# Link fields the v3 Link API needs (see .claude/rules/01-database-standards.md).
# Mapping: env-var name -> (source table, target table)
LINK_FIELDS = {
    "NOCODB_LINK_JOB_POSTINGS_TO_TARGET_COMPANIES":
        ("job_postings", "target_companies"),
    "NOCODB_LINK_APPLICATIONS_TO_TARGET_COMPANIES":
        ("applications", "target_companies"),
    "NOCODB_LINK_APPLICATIONS_TO_JOB_POSTINGS":
        ("applications", "job_postings"),
}


def repo_root() -> Path:
    """Walk up from this file to find the repo root (the dir containing .env.example)."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / ".env.example").exists():
            return parent
    sys.exit("Could not locate repo root (no .env.example in any parent dir).")


def load_env(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        sys.exit(
            f"Missing .env at {env_path}. "
            "Copy .env.example to .env and fill in NOCODB_URL and NOCODB_API_TOKEN."
        )
    env: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def write_env_var(env_path: Path, key: str, value: str) -> None:
    """Update or append a key=value line in .env, preserving order and comments."""
    lines = env_path.read_text(encoding="utf-8").splitlines()
    new_line = f"{key}={value}"
    found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            lines[i] = new_line
            found = True
            break
    if not found:
        lines.append(new_line)
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def api_get(url: str, token: str) -> dict:
    r = requests.get(url, headers={"xc-token": token}, timeout=30)
    r.raise_for_status()
    return r.json()


def list_all_bases(nocodb_url: str, token: str) -> list[dict]:
    """Enumerate every base the token can see.

    NocoDB 2026.x is workspace-scoped: `/api/v2/meta/bases` returns 403 with a
    PAT, so we walk workspaces and concatenate their bases. Older versions
    expose the flat `/api/v2/meta/bases` endpoint — try it first and fall back.
    """
    base_url = nocodb_url.rstrip("/")
    try:
        payload = api_get(f"{base_url}/api/v2/meta/bases", token)
        flat = payload.get("list", payload) if isinstance(payload, dict) else payload
        if flat:
            return flat
    except requests.HTTPError:
        pass

    ws_payload = api_get(f"{base_url}/api/v2/meta/workspaces", token)
    workspaces = ws_payload.get("list", ws_payload) if isinstance(ws_payload, dict) else ws_payload
    bases: list[dict] = []
    for ws in workspaces:
        ws_id = ws.get("id")
        if not ws_id:
            continue
        try:
            payload = api_get(f"{base_url}/api/v2/meta/workspaces/{ws_id}/bases", token)
        except requests.HTTPError:
            continue
        ws_bases = payload.get("list", payload) if isinstance(payload, dict) else payload
        for b in ws_bases:
            b.setdefault("fk_workspace_id", ws_id)
        bases.extend(ws_bases)
    return bases


def base_has_jobhunt_tables(nocodb_url: str, token: str, base_id: str) -> bool:
    tables_url = f"{nocodb_url.rstrip('/')}/api/v2/meta/bases/{base_id}/tables"
    try:
        payload = api_get(tables_url, token)
    except requests.HTTPError:
        return False
    tables = payload.get("list", payload) if isinstance(payload, dict) else payload
    names = {t.get("table_name") or t.get("title") for t in tables}
    return EXPECTED_TABLES.issubset({n for n in names if n})


def create_jobhunt_base(nocodb_url: str, token: str, workspace_id: str,
                        pg_host: str, pg_port: str, pg_user: str,
                        pg_password: str, pg_database: str) -> str:
    """Create the JobHunt base + postgres source via API.

    Used as a fallback when the user hasn't connected the database manually
    yet. Returns the new base id.
    """
    url = f"{nocodb_url.rstrip('/')}/api/v2/meta/workspaces/{workspace_id}/bases"
    body = {
        "title": "JobHunt",
        "type": "database",
        "external": True,
        "sources": [{
            "alias": "jobhunt",
            "type": "pg",
            "config": {
                "client": "pg",
                "connection": {
                    "host": pg_host, "port": pg_port,
                    "user": pg_user, "password": pg_password,
                    "database": pg_database,
                },
                "searchPath": ["public"],
            },
            "inflection_column": "none",
            "inflection_table": "none",
        }],
    }
    r = requests.post(url, json=body, headers={"xc-token": token}, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def find_jobhunt_base(nocodb_url: str, token: str,
                      pg_creds: dict | None = None) -> str:
    """Find (or auto-create) the base containing the 7 jobhunt tables."""
    bases = list_all_bases(nocodb_url, token)
    for base in bases:
        base_id = base.get("id") or base.get("base_id")
        if base_id and base_has_jobhunt_tables(nocodb_url, token, base_id):
            return base_id

    # No matching base. If we have postgres credentials, auto-create one.
    if pg_creds:
        ws_id = next(
            (b.get("fk_workspace_id") for b in bases if b.get("fk_workspace_id")),
            None,
        )
        if not ws_id:
            ws_payload = api_get(f"{nocodb_url.rstrip('/')}/api/v2/meta/workspaces", token)
            ws_list = ws_payload.get("list", ws_payload) if isinstance(ws_payload, dict) else ws_payload
            ws_id = ws_list[0]["id"] if ws_list else None
        if ws_id:
            print(f"  No matching base found - creating one in workspace {ws_id}...")
            new_id = create_jobhunt_base(nocodb_url, token, ws_id, **pg_creds)
            if base_has_jobhunt_tables(nocodb_url, token, new_id):
                return new_id

    sys.exit(
        "Could not find or create a NocoDB base containing all 7 expected "
        "tables: " + ", ".join(sorted(EXPECTED_TABLES))
        + ". Verify the postgres `jobhunt` database is reachable and the schema loaded."
    )


def list_tables(nocodb_url: str, token: str, base_id: str) -> list[dict]:
    url = f"{nocodb_url.rstrip('/')}/api/v2/meta/bases/{base_id}/tables"
    payload = api_get(url, token)
    return payload.get("list", payload) if isinstance(payload, dict) else payload


def get_table_info(nocodb_url: str, token: str, table_id: str) -> dict:
    url = f"{nocodb_url.rstrip('/')}/api/v2/meta/tables/{table_id}"
    return api_get(url, token)


def find_link_field_id(table_info: dict, target_table_name: str) -> str | None:
    """Find the LinkToAnotherRecord field id pointing at target_table_name."""
    for col in table_info.get("columns", []):
        if col.get("uidt") not in ("LinkToAnotherRecord", "Links"):
            continue
        col_options = col.get("colOptions") or {}
        related_id = col_options.get("fk_related_model_id")
        # If we can see the related table id, look it up by name.
        # Otherwise try matching on the column title.
        title = (col.get("title") or "").lower()
        if target_table_name.replace("_", "").lower() in title.replace("_", "").lower():
            return col.get("id")
        # Fallback: store the related model id; resolved below.
    return None


def main() -> int:
    root = repo_root()
    env_path = root / ".env"
    env = load_env(env_path)

    nocodb_url = env.get("NOCODB_URL", "http://localhost:8080")
    token = env.get("NOCODB_API_TOKEN", "").strip()
    if not token:
        sys.exit(
            "NOCODB_API_TOKEN is empty in .env. "
            "Generate a token in NocoDB at Account -> Tokens and paste it in."
        )

    print(f"Connecting to NocoDB at {nocodb_url}...")

    # Optional postgres creds — used to auto-create the JobHunt base if no
    # base with the 7 expected tables exists yet. Read from infrastructure/.env
    # since that's where POSTGRES_PASSWORD lives.
    pg_creds: dict | None = None
    infra_env_path = root / "infrastructure" / ".env"
    if infra_env_path.exists():
        infra_env = load_env(infra_env_path)
        pg_password = infra_env.get("POSTGRES_PASSWORD", "")
        if pg_password:
            pg_creds = {
                "pg_host": "postgres",  # NocoDB resolves this via the docker network
                "pg_port": "5432",
                "pg_user": "jobhunt",
                "pg_password": pg_password,
                "pg_database": "jobhunt",
            }

    try:
        base_id = find_jobhunt_base(nocodb_url, token, pg_creds=pg_creds)
    except requests.HTTPError as e:
        sys.exit(f"NocoDB API error: {e}")

    print(f"Found job-hunt-os base: {base_id}")
    write_env_var(env_path, "NOCODB_BASE_ID", base_id)

    tables = list_tables(nocodb_url, token, base_id)
    name_to_id = {t.get("table_name") or t.get("title"): t.get("id") for t in tables}

    found: dict[str, str] = {}
    for env_var, (source, target) in LINK_FIELDS.items():
        source_id = name_to_id.get(source)
        if not source_id:
            print(f"  WARN: source table {source!r} not found")
            continue
        info = get_table_info(nocodb_url, token, source_id)
        link_id = find_link_field_id(info, target)
        if link_id:
            found[env_var] = link_id
            print(f"  {env_var} = {link_id}")
            write_env_var(env_path, env_var, link_id)
        else:
            print(
                f"  WARN: could not find LinkToAnotherRecord field on "
                f"{source!r} pointing at {target!r}"
            )

    print(f"\nWrote {1 + len(found)} value(s) to {env_path}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
