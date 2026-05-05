# Setup

End-to-end installation walkthrough. This is for a single-user setup; for multi-user see [`MULTI-USER.md`](MULTI-USER.md).

## Prerequisites

- **Claude Code** (or another agent compatible with the `.claude/` rules + skills system) installed and working.
- **Python 3.10+** with `pip` (Phase 4 — required for resume-tailor, job-search, etc.).
- **Docker Desktop** running (Phase 4 — required for the NocoDB stack and the LinkedIn MCP).
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
| `NOCODB_URL` | NocoDB instance URL | Default `http://localhost:8080` (self-hosted via `infrastructure/docker-compose.yml` in Phase 4) |
| `NOCODB_API_TOKEN` | API token | Once NocoDB is up: log in → Account → Tokens → create new |
| `NOCODB_BASE_ID` | Base id for the JobHunt base | Set by `tools/setup/init-nocodb.py` (Phase 4); leave blank for now |
| `NOCODB_MCP_PREFIX` | Tool prefix used by the agent | Default `mcp__nocodb__` |
| `JOB_HUNT_USER` | Active user slug | Set to your slug (e.g., `jane-doe`). For demo, use `jane-demo` |
| `OPENROUTER_API_KEY` | Optional | For mock-interview / recruiter-review tools (Phase 4); skip for now |
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

## Step 4: Bring up the data backend (Phase 4)

> ⏳ The Docker Compose stack is in the deferred Phase 4. For now, you can either:
> - **Wait** for the Phase 4 release.
> - **Use a NocoDB cloud instance** at https://nocodb.com (free tier).
> - **Build the schema manually** by importing `infrastructure/init-db/02-jobhunt-schema.sql` (Phase 4) into a Postgres instance and pointing NocoDB at it.

Once Phase 4 lands:
```bash
cd infrastructure
cp .env.example .env       # fill in DB passwords
docker compose up -d
# Visit http://localhost:8080, create your admin user, generate an API token.
```

## Step 5: Initialise the schema (Phase 4)

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
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-nocodb"],
          "env": {
            "NOCODB_BASE_URL": "http://localhost:8080",
            "NOCODB_API_TOKEN": "<your token>"
          }
        },
        "context7": {
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-context7"]
        },
        "playwright": {
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-playwright"]
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

## Step 7: First-run health check (Phase 4)

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
| `/job-search` Python errors | `python-jobspy` not installed | `pip install python-jobspy` (Phase 4) |
| Resume tailoring fails quality gate | JD not specific enough OR overrides incomplete | Open `applications/jobs/{company}-{job-slug}.yaml`, add more text_overrides, regenerate |
| `bulk_insert` returns "fetch failed" | MCP transient error | Retry once after 2 sec; if still failing, see `01-database-standards.md` Rule 9 |

## Next Steps

- Read [`AGENTS.md`](../AGENTS.md) — the canonical AI-agent onboarding doc.
- Read [`CUSTOMIZE.md`](CUSTOMIZE.md) — what each config knob actually controls.
- Read [`ARCHITECTURE.md`](ARCHITECTURE.md) — the four-layer model + data flow.
- Read [`EXAMPLES.md`](EXAMPLES.md) — narrative walkthroughs.
