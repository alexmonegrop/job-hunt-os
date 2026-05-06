# New-Machine Bootstrap

Self-contained instructions to set up a fresh machine to run job-hunt-os.
Run this **before** `/onboard-user` — it handles environment setup, repo
cloning (if not already done), MCP configuration, and dependency installation.
Once complete, it hands off to the onboarding skill for person-specific setup.

For the canonical full setup walkthrough, see `docs/SETUP.md`. This bootstrap
doc adds two extras:
- `bootstrap-prompt.md` — a paste-ready Claude Code prompt that walks the
  agent through the same setup steps interactively.
- A condensed step-by-step troubleshooting reference.

## When to Use This

- You've just cloned the template onto a new machine.
- You want Claude Code to do the setup work conversationally (vs reading
  `docs/SETUP.md` and running steps yourself).
- You're onboarding someone else's machine to the same shared infrastructure
  (multi-user case — see `docs/MULTI-USER.md`).

## Phases

### Phase 1 — Pre-flight checks (~2 min)

```bash
git --version
python --version    # or python3 --version
node --version
npx --version
docker --version
```

Required: Git, Python 3.10+, Node.js 18+. Optional: Docker (for NocoDB stack
+ LinkedIn MCP), Microsoft Word (for `docx2pdf` resume PDF generation —
LibreOffice is a fallback).

Also check Docker is actually running:
```bash
docker info
```

### Phase 2 — Clone the repo (~2 min)

```bash
mkdir -p ~/claude-work-folder
cd ~/claude-work-folder

# Public template - no PAT needed
git clone https://github.com/<your-org>/job-hunt-os.git
cd job-hunt-os

ls .claude/skills/
# Should show: apply, cold-outreach, contact-population, meeting-prep, etc.
```

If you forked the template into your own private repo, clone via your own
PAT using the documented "set token → clone → strip token" pattern in
`docs/SETUP.md`.

Configure git identity (repo-local):
```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

### Phase 3 — Configure `.env` files (~3 min)

```bash
cp .env.example .env
cp infrastructure/.env.example infrastructure/.env
```

Edit each. Generate a postgres password with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Required values:
| File | Variable | What |
|------|----------|------|
| `.env` | `JOB_HUNT_USER` | Your slug (e.g., `jane-doe`) |
| `.env` | `NOCODB_URL` | `http://localhost:8080` (default) |
| `.env` | `NOCODB_API_TOKEN` | Generated in NocoDB UI after Phase 5 |
| `infrastructure/.env` | `POSTGRES_PASSWORD` | Strong generated password |

Leave `NOCODB_BASE_ID` and link-field IDs blank — they're filled in by
`tools/setup/init-nocodb.py` after the schema is up.

### Phase 4 — Install Python dependencies (~2 min)

```bash
pip install python-docx pyyaml docx2pdf python-jobspy fpdf2 requests openai-whisper
```

On Windows, if `pip` isn't found:
```bash
python -m pip install python-docx pyyaml docx2pdf python-jobspy fpdf2 requests openai-whisper
```

Verify:
```bash
python -c "import docx, yaml, fpdf, requests; print('Core deps OK')"
```

`docx2pdf` uses Microsoft Word via COM automation on Windows. If Word isn't
installed, the system still works — `tools/resume-tailor/generate-pdf.py`
falls back to LibreOffice, or you can convert `.docx` to PDF manually.

### Phase 5 — Bring up the data stack (~5 min)

```bash
cd infrastructure
docker compose up -d

# Wait ~30 seconds for postgres + nocodb to be healthy:
docker compose ps
```

Visit `http://localhost:8080`:
1. Create a NocoDB admin user (any email + password you like — local only).
2. Add the postgres `jobhunt` database as a Data Source:
   - Account → Data Sources → + New
   - Host: `postgres` (the service name on the docker network)
   - Port: `5432`
   - User: `jobhunt`
   - Password: from `infrastructure/.env` `POSTGRES_PASSWORD`
   - Database: `jobhunt`
3. NocoDB will discover the 7 tables.
4. Account → Tokens → create a new API token.
5. Paste the token into the project `.env` `NOCODB_API_TOKEN`.

### Phase 6 — Discover schema IDs (~1 min)

```bash
cd ..   # back to repo root
python tools/setup/init-nocodb.py
```

This script:
- Reads `NOCODB_URL` + `NOCODB_API_TOKEN` from `.env`.
- Finds the base containing the 7 job-hunt tables.
- Discovers the LinkToAnotherRecord field IDs needed for the v3 Link API.
- Writes `NOCODB_BASE_ID` + 3 link-field IDs back to `.env`.

### Phase 7 — Configure MCPs in `~/.claude.json` (~3 min)

Edit `~/.claude.json` (or `C:\Users\<user>\.claude.json` on Windows).

> Use forward slashes in the path key, even on Windows.
> Get your absolute path: `cd ~/claude-work-folder/job-hunt-os && pwd`.

If `~/.claude.json` doesn't exist, create it:
```json
{
  "projects": {
    "<absolute path to job-hunt-os, forward slashes>": {
      "mcpServers": {
        "nocodb": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@andrewlwn77/nocodb-mcp"],
          "env": {
            "NOCODB_BASE_URL": "<NOCODB_URL from .env>",
            "NOCODB_API_TOKEN": "<NOCODB_API_TOKEN from .env>"
          }
        },
        "context7": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@upstash/context7-mcp@latest"],
          "env": {}
        },
        "playwright": {
          "type": "stdio",
          "command": "npx",
          "args": ["@playwright/mcp@latest", "--allow-unrestricted-file-access"],
          "env": {}
        }
      }
    }
  }
}
```

If `~/.claude.json` exists with other project entries, **merge** — don't
overwrite. Add your project key under `projects` and write back.

#### Optional MCPs

LinkedIn (requires Docker running, **your own** session cookie):
```json
"linkedin": {
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "--rm", "-i", "--network", "host",
    "-v", "<your home dir, forward slashes>/.linkedin-mcp:/home/pwuser/.linkedin-mcp",
    "stickerdaniel/linkedin-mcp-server:latest"
  ]
}
```

GitHub (your own PAT with `repo` scope):
```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<your PAT>" }
}
```

Hunter.io (optional contact enrichment, your own key):
```json
"hunter": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://mcp.hunter.io/sse", "--header", "Authorization:Bearer ${HUNTER_API_KEY}"],
  "env": { "HUNTER_API_KEY": "<your Hunter.io API key>" }
}
```

Install Playwright's chromium:
```bash
npx playwright install chromium
```

### Phase 8 — Health check (~1 min)

```bash
python tools/setup/first-run.py
```

Reports a status table for `.env` files, Docker, compose stack, NocoDB
reachability, MCP config, Chrome state, Python deps. Address any FAILs
before continuing.

### Phase 9 — Restart Claude Code (~1 min)

MCP servers register at startup only. Restart is mandatory.

1. Close ALL Chrome / Chromium windows (Playwright tools require a clean
   browser state at startup — check Task Manager / `pgrep -f chrome`).
2. Exit Claude Code (`/exit` or Ctrl+C).
3. Open a fresh terminal, `cd` to `job-hunt-os/`, run `claude`.

### Phase 10 — `/session-start` and onboard

In the fresh Claude Code session:
```
/session-start
```

Expected MCP status:

| Service | Expected |
|---------|----------|
| NocoDB | Connected |
| Context7 | Connected |
| Playwright | Available |
| LinkedIn | Connected (if Docker running + cookie configured) |
| Git | Synced |

Then select **"Onboard new user"** from the action menu, or run:
```
/onboard-user
```

This runs the 8-phase onboarding (intake → job search → role profiles →
resume extraction → gap analysis → interview → finalise). See the
`onboard-user` skill for details.

Total bootstrap time: ~15-20 min. Onboarding adds ~60-90 min on top.

## Troubleshooting

### Docker errors
- **`docker info` fails**: start Docker Desktop and wait for the daemon icon to settle.
- **Port 8080 already in use**: edit `infrastructure/.env` `NOCODB_HOST_PORT=8081` and retry.
- **Postgres healthcheck fails**: check `docker compose logs postgres` — usually a password mismatch between `infrastructure/.env` and a previous volume.
- **Schema didn't init**: `docker compose down -v` to wipe the volume, then `up -d` again. The init SQL runs once per fresh volume only.

### MCP tools don't appear in Claude Code
- Close ALL Chrome / Chromium instances (check Task Manager / `pgrep`).
- Restart Claude Code from a fresh terminal.
- MCPs only register at session startup; they cannot be hot-loaded.

### NocoDB "fetch failed"
- Test with curl using your token:
  ```bash
  curl -H "xc-token: <token>" "<NOCODB_URL>/api/v2/meta/bases"
  ```
- If curl works but MCP fails: remove and re-add the MCP entry in `~/.claude.json`, restart Claude Code.

### `docx2pdf` fails
- Requires MS Word on Windows (COM automation).
- Without Word: install LibreOffice (free) — `tools/resume-tailor/generate-pdf.py` auto-detects it.
- Last resort: open `.docx` manually and Save As PDF.

### Windows: Python not found
- Try `python` instead of `python3` (Windows installer registers as `python`).
- Or install from Microsoft Store: search for `Python 3.12`.

### Windows: forward slashes in `~/.claude.json`
- Always use `C:/Users/jane/...` — never `C:\Users\jane\...`.

### Git push fails with 401
- Your PAT may be expired. Regenerate at github.com/settings/tokens with `repo` scope.
- See `docs/SETUP.md` for the safe "set token → push → strip token" pattern.

## Security Notes

- The repo and this doc contain **no real credentials**. All tokens you see
  are placeholders (`<your PAT>`, `<your API key>`).
- `.env` and `infrastructure/.env` are gitignored — your real values stay
  local. Never commit them.
- `~/.claude.json` lives in your home directory, not the repo. Do not check
  it into any repo.
- Your LinkedIn `li_at` cookie is **personal** — never share it. Each user
  must use their own (using someone else's gets accounts flagged).
- If you suspect a token has been leaked: rotate it immediately at the
  provider, then update `.env` + `~/.claude.json` + restart Claude Code.

---

**For the conversational version of these steps**: see `bootstrap-prompt.md`
in this directory — it's a paste-ready Claude Code prompt.
