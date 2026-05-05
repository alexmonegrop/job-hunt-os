"""first-run.py — sanity-check the local environment before first session.

Verifies:
  - .env exists with required keys.
  - infrastructure/.env exists with required keys.
  - Docker is running and reachable.
  - The postgres + nocodb containers are up (or warns if not).
  - NocoDB is reachable on its configured URL.
  - ~/.claude.json exists and has at least one job-hunt-os MCP entry.
  - Chrome is not running (Playwright requires it closed at startup).
  - Required Python packages are importable (pyyaml, requests).

Does NOT modify anything. Read-only health check.

Usage:
  python tools/setup/first-run.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_ROOT_ENV = ["NOCODB_URL", "NOCODB_API_TOKEN", "JOB_HUNT_USER"]
REQUIRED_INFRA_ENV = ["POSTGRES_PASSWORD"]

OK = "OK"
WARN = "WARN"
FAIL = "FAIL"


def repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / ".env.example").exists():
            return parent
    sys.exit("Could not locate repo root (no .env.example in any parent dir).")


def parse_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def check_env(root: Path) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    env_path = root / ".env"
    infra_env_path = root / "infrastructure" / ".env"

    if not env_path.exists():
        out.append(("Project .env", FAIL, "Missing - copy .env.example to .env"))
    else:
        env = parse_env(env_path)
        missing = [k for k in REQUIRED_ROOT_ENV if not env.get(k)]
        if missing:
            out.append(("Project .env", WARN, f"Missing values: {', '.join(missing)}"))
        else:
            out.append(("Project .env", OK, f"All {len(REQUIRED_ROOT_ENV)} required keys set"))

    if not infra_env_path.exists():
        out.append(("infrastructure/.env", WARN, "Missing - copy infrastructure/.env.example to infrastructure/.env"))
    else:
        env = parse_env(infra_env_path)
        missing = [k for k in REQUIRED_INFRA_ENV if not env.get(k) or "CHANGE_ME" in env.get(k, "")]
        if missing:
            out.append(("infrastructure/.env", WARN, f"Missing or default values: {', '.join(missing)}"))
        else:
            out.append(("infrastructure/.env", OK, "All required keys set"))
    return out


def check_docker() -> tuple[str, str, str]:
    if not shutil.which("docker"):
        return ("Docker", FAIL, "`docker` not on PATH - install Docker Desktop")
    try:
        r = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return ("Docker", FAIL, "Docker installed but daemon not responding (start Docker Desktop)")
        return ("Docker", OK, f"Server version: {r.stdout.strip()}")
    except subprocess.TimeoutExpired:
        return ("Docker", FAIL, "Docker daemon hung (timeout)")
    except OSError as e:
        return ("Docker", FAIL, f"Error: {e}")


def check_compose_services(root: Path) -> tuple[str, str, str]:
    if not shutil.which("docker"):
        return ("Compose stack", WARN, "Docker not available; skipping")
    try:
        r = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True, text=True, timeout=10,
            cwd=str(root / "infrastructure"),
        )
    except OSError as e:
        return ("Compose stack", WARN, f"Could not run `docker compose ps`: {e}")
    if r.returncode != 0:
        return ("Compose stack", WARN, "Stack not up - run `docker compose up -d` in infrastructure/")
    out = r.stdout.strip()
    if not out:
        return ("Compose stack", WARN, "No containers running - run `docker compose up -d`")
    services = []
    # `compose ps --format json` outputs newline-delimited JSON in newer Compose,
    # or a single JSON array in older Compose. Handle both.
    try:
        try:
            parsed = json.loads(out)
            if isinstance(parsed, list):
                services = [s.get("Service") or s.get("Name") for s in parsed]
            else:
                services = [parsed.get("Service") or parsed.get("Name")]
        except json.JSONDecodeError:
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                services.append(obj.get("Service") or obj.get("Name"))
    except json.JSONDecodeError:
        return ("Compose stack", WARN, f"Could not parse compose output")
    services = [s for s in services if s]
    return ("Compose stack", OK, f"Running: {', '.join(services)}")


def check_nocodb(env: dict[str, str]) -> tuple[str, str, str]:
    url = env.get("NOCODB_URL", "http://localhost:8080").rstrip("/")
    try:
        import requests
    except ImportError:
        return ("NocoDB reachable", WARN, "Cannot test — install `requests`")
    try:
        r = requests.get(f"{url}/api/v1/health", timeout=5)
        if r.status_code == 200:
            return ("NocoDB reachable", OK, f"{url} responding")
        return ("NocoDB reachable", WARN, f"{url} returned HTTP {r.status_code}")
    except requests.RequestException as e:
        return ("NocoDB reachable", WARN, f"{url}: {e}")


def check_claude_json() -> tuple[str, str, str]:
    home = Path.home()
    cfg_path = home / ".claude.json"
    if not cfg_path.exists():
        return ("~/.claude.json", WARN, "Not found - Claude Code MCPs need configuration")
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return ("~/.claude.json", FAIL, f"Could not parse JSON: {e}")
    projects = cfg.get("projects", {})
    job_hunt_keys = [k for k in projects if "job-hunt-os" in k.replace("\\", "/")]
    if not job_hunt_keys:
        return ("~/.claude.json", WARN, "No job-hunt-os entry - add MCPs (see docs/SETUP.md)")
    mcps = []
    for k in job_hunt_keys:
        mcps += list(projects[k].get("mcpServers", {}).keys())
    if not mcps:
        return ("~/.claude.json", WARN, "Project entry exists but no MCPs configured")
    return ("~/.claude.json", OK, f"MCPs: {', '.join(mcps)}")


def check_chrome_closed() -> tuple[str, str, str]:
    """Warn if Chrome is running — Playwright registers tools at Claude Code startup
    and needs Chrome closed for clean registration."""
    is_windows = sys.platform == "win32"
    try:
        if is_windows:
            r = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            running = "chrome.exe" in r.stdout.lower()
        else:
            r = subprocess.run(
                ["pgrep", "-f", "chrome|chromium"],
                capture_output=True, text=True, timeout=5,
            )
            running = bool(r.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        return ("Chrome closed", WARN, "Could not check - close Chrome before launching Claude Code")
    if running:
        return ("Chrome closed", WARN, "Chrome is running - close it before launching Claude Code (Playwright)")
    return ("Chrome closed", OK, "")


def check_python_packages() -> tuple[str, str, str]:
    required = ["yaml", "requests"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        names = {"yaml": "pyyaml", "requests": "requests"}
        pip_names = [names.get(m, m) for m in missing]
        return ("Python deps", WARN, f"Missing: {', '.join(pip_names)} - `pip install {' '.join(pip_names)}`")
    return ("Python deps", OK, f"All required packages importable")


def render(rows: list[tuple[str, str, str]]) -> None:
    width_check = max(len(r[0]) for r in rows)
    width_status = max(len(r[1]) for r in rows)
    print()
    for check, status, detail in rows:
        marker = {OK: "[ OK ]", WARN: "[WARN]", FAIL: "[FAIL]"}.get(status, status)
        print(f"  {marker}  {check:<{width_check}}  {detail}")
    print()
    fails = sum(1 for r in rows if r[1] == FAIL)
    warns = sum(1 for r in rows if r[1] == WARN)
    if fails:
        print(f"{fails} FAIL, {warns} WARN. Address FAILs before continuing.")
    elif warns:
        print(f"All required checks passed. {warns} WARN - address before running skills that need them.")
    else:
        print("All checks passed. You're ready to run /onboard-user in Claude Code.")


def main() -> int:
    root = repo_root()
    rows: list[tuple[str, str, str]] = []

    rows += check_env(root)

    rows.append(check_docker())
    rows.append(check_compose_services(root))

    env = parse_env(root / ".env")
    rows.append(check_nocodb(env))

    rows.append(check_claude_json())
    rows.append(check_chrome_closed())
    rows.append(check_python_packages())

    render(rows)
    return 0 if not any(r[1] == FAIL for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
