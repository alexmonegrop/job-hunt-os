# Setup

End-to-end installation walkthrough. This is for a single-user setup; for multi-user see [`MULTI-USER.md`](MULTI-USER.md).

## Prerequisites

- **Claude Code** (or another agent compatible with the `.claude/` rules + skills system) installed and working.
- **Python 3.10+** with `pip` (required for resume-tailor, job-search, etc.).
- **Docker Desktop** running (required for the NocoDB stack and the LinkedIn MCP).
- **Git** installed.
- A GitHub account (for forking / templating this repo).

## Step 1: Get the repo

Use as a template (recommended):
```bash
gh repo create my-job-hunt --template <your-org>/job-hunt-os --private
cd my-job-hunt
```

Or fork via the GitHub UI.

## Step 2: Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | What | How |
|----------|------|-----|
| `NOCODB_URL` | NocoDB instance URL | Default `http://localhost:8080` (self-hosted via `infrastructure/docker-compose.yml`) |
| `NOCODB_API_TOKEN` | API token | Once NocoDB is up: log in → Account → Tokens → create new |
| `NOCODB_BASE_ID` | Base id for the JobHunt base | Set automatically by `tools/setup/init-nocodb.py`; leave blank initially |
| `NOCODB_MCP_PREFIX` | Tool prefix used by the agent | Default `mcp__nocodb__` |
| `JOB_HUNT_USER` | Active user slug | Set to your slug (e.g., `jane-doe`). For demo, use `jane-demo` |
| `OPENROUTER_API_KEY` | Optional | For mock-interview / recruiter-review tools; skip if you don't use them |
| `GITHUB_PAT` | Optional | For session-start git pull / session-end git push using PAT-in-URL pattern |

Never commit `.env` — it's gitignored.

## Step 3: Configure `config/*.yaml`

```bash
cp config/user-profile.example.yaml  config/user-profile.yaml
cp config/fit-score.example.yaml     config/fit-score.yaml
cp config/industries.example.yaml    config/industries.yaml
cp config/regions.example.yaml       config/regions.yaml
```

Edit each:

- **`user-profile.yaml`** — name, slug, location, target roles, target regions, target industries, excluded companies, languages, credibility anchors, value props, credentials, work authorisation, resume variants. See [`CUSTOMIZE.md`](CUSTOMIZE.md) for what each field drives.
- **`fit-score.yaml`** — raw scoring criteria, penalties, bonuses, thresholds. The defaults are sane; customise penalties to match your gap analysis.
- **`industries.yaml`** — your canonical industry vocabulary (used as the database `industry` dropdown).
- **`regions.yaml`** — region presets (cities, languages, flagship buyers, job boards, regional dynamics).

These files are gitignored — your real config never gets pushed.

## Step 4: Bring up the data backend

```bash
cd infrastructure
cp .env.example .env                      # set POSTGRES_PASSWORD (e.g. `openssl rand -hex 32`)
docker compose up -d                      # postgres + nocodb
```

Wait ~30s for the NocoDB healthcheck. Then choose **one** of the two paths below.

### Option A — One-shot (recommended for local dev)

Skip the UI entirely. Step 5 runs admin signup + token minting via API:

```bash
python tools/setup/init-nocodb.py --auto-bootstrap
```

The script signs up `admin@local.test` with a freshly-generated 32-byte URL-safe password (overridable via `--admin-email` / `--admin-password`, or `NOCODB_ADMIN_EMAIL` / `NOCODB_ADMIN_PASSWORD` in `.env`), mints a 40-char PAT, and writes all three back to `.env`. If an admin already exists it falls back to signin — re-running is idempotent.

### Option B — Manual UI

If you want to set your own admin email or click around first, do it via the UI at `http://localhost:8080`:

1. **Create the admin user** (any email/password — local-only).
2. **Account → Tokens → + New** → copy the token into the root `.env` as `NOCODB_API_TOKEN`.

Then run `python tools/setup/init-nocodb.py` (no flag).

Either way, `tools/setup/init-nocodb.py` auto-creates the JobHunt base by reading `POSTGRES_PASSWORD` from `infrastructure/.env` — no UI plumbing needed.

> **"Forbidden host name or IP address"** if you ever rebuild the data source manually means NocoDB is enforcing SSRF protection against internal hostnames. The shipped `docker-compose.yml` sets `NC_ALLOW_LOCAL_EXTERNAL_DBS=true` to permit the Docker-internal `postgres` host; the auto-create flow needs this too. If you removed it, add it back and recreate the nocodb container (`docker compose up -d --no-deps nocodb`).

Alternative deployments if you don't want to run Docker locally:
- **NocoDB cloud** at https://nocodb.com (free tier).
- **Manual schema import**: load `infrastructure/init-db/02-jobhunt-schema.sql` into your own Postgres and point NocoDB at it.

## Step 5: Initialise the schema

```bash
python tools/setup/init-nocodb.py
```

This:
- Creates 7 tables (`users`, `target_companies`, `target_contacts`, `sales_pipeline`, `interactions`, `job_postings`, `applications`).
- Discovers the link-field IDs (used for the v3 Link API per `01-database-standards.md` Rule 8).
- Writes `NOCODB_BASE_ID` and the link-field IDs back into your `.env`.

## Step 6: Configure MCP servers (Claude Code)

Edit `~/.claude.json` and add an entry under `projects > <path-to-job-hunt-os> > mcpServers`. Minimum:

```json
{
  "projects": {
    "<absolute path to job-hunt-os>": {
      "mcpServers": {
        "nocodb": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@andrewlwn77/nocodb-mcp"],
          "env": {
            "NOCODB_BASE_URL": "http://localhost:8080",
            "NOCODB_API_TOKEN": "<your token>"
          }
        },
        "context7": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@upstash/context7-mcp"]
        },
        "playwright": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@playwright/mcp@latest"]
        }
      }
    }
  }
}
```

Optional:
- **LinkedIn MCP** — for contact research and job-id discovery. Requires Docker. Each user MUST use their own `li_at` cookie.
- **GitHub MCP** — for managing PRs and issues programmatically.

How to get a LinkedIn `li_at` cookie:
1. Log in to LinkedIn in Chrome.
2. DevTools (F12) → Application → Cookies → `linkedin.com`.
3. Copy the `li_at` value (it's a long opaque string).

Add to `~/.claude.json`:
```json
"linkedin": {
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "LINKEDIN_SESSION_COOKIE=<your li_at>",
    "ghcr.io/anthropic/mcp-linkedin:latest"
  ]
}
```

## Step 7: First-run health check

```bash
python tools/setup/first-run.py
```

This checks: Docker running, Chrome closed (Playwright needs a clean launch), MCPs configured, `.env` valid, schema initialised. It offers to install missing pieces.

## Step 8: Open in Claude Code

```bash
cd <path-to-job-hunt-os>
claude
```

In the session, run:
```
/session-start
```

You should see a status table showing which MCPs are connected. If anything is red, troubleshoot per the table below.

Then run:
```
/onboard-user
```

This walks you through 8 phases of onboarding (intake → job search → role profiles → resume extraction → gap analysis → interview → finalise). At the end your profile is fully populated and you're ready for `/job-search` or `/cold-outreach`.

## Step 9: Try the Jane Demo

Before plugging in your real data, you can run through the bundled walkthrough:
```
JOB_HUNT_USER=jane-demo claude
> Read plans/EXAMPLES/jane-demo-walkthrough.md
```

It shows what a typical session looks like end-to-end.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `/session-start` shows NocoDB DISCONNECTED | API token wrong or server down | Check `NOCODB_API_TOKEN` in `.env`; verify NocoDB is running |
| `/session-start` shows LinkedIn DISCONNECTED | Docker not running, or `li_at` expired | Start Docker, refresh `li_at` cookie |
| Playwright tools not registered | Chrome was open when Claude Code launched | Close all Chrome instances, restart Claude Code |
| `git push` fails with 401 | PAT expired or scope wrong | Regenerate PAT (scope: `repo`); see PAT-in-URL pattern in `session-end` skill |
| `/job-search` Python errors | `python-jobspy` not installed | `pip install python-jobspy` |
| Resume tailoring fails quality gate | JD not specific enough OR overrides incomplete | Open `applications/jobs/{company}-{job-slug}.yaml`, add more text_overrides, regenerate |
| `bulk_insert` returns "fetch failed" | MCP transient error | Retry once after 2 sec; if still failing, see `01-database-standards.md` Rule 9 |

## Next Steps

- Read [`AGENTS.md`](../AGENTS.md) — the canonical AI-agent onboarding doc.
- Read [`CUSTOMIZE.md`](CUSTOMIZE.md) — what each config knob actually controls.
- Read [`ARCHITECTURE.md`](ARCHITECTURE.md) — the four-layer model + data flow.
- Read [`EXAMPLES.md`](EXAMPLES.md) — narrative walkthroughs.
