# Bootstrap Prompt — Paste Into a Fresh Claude Code Session

Use this when setting up job-hunt-os on a new machine and you'd rather have
the agent walk you through it conversationally than follow `docs/SETUP.md`
manually. Paste everything below the line as the first message in a new
Claude Code session, with the working directory set to the cloned repo.

> No real credentials are in this prompt. The agent will ask for your own
> values where needed.

---

You are setting up the job-hunt-os system on this machine. Follow the steps
in `tools/bootstrap/BOOTSTRAP.md` in order. Do not skip steps. Ask the user
to provide values where the doc has placeholders.

## Step 1: Pre-flight checks
Run and report what's installed:
- `git --version`
- `python --version` (or `python3 --version`)
- `node --version`, `npx --version`
- `docker --version`, `docker info` (is Docker Desktop running?)

Required: Git, Python 3.10+, Node.js 18+. Optional: Docker, Microsoft Word.
If Git, Python, or Node is missing, tell the user what to install and STOP.

## Step 2: Clone (if needed)
If the user is in the cloned repo already, skip to Step 3.
Otherwise, ask them where to put the project (default
`~/claude-work-folder/job-hunt-os`) and clone:
```bash
git clone https://github.com/<your-org>/job-hunt-os.git ~/claude-work-folder/job-hunt-os
cd ~/claude-work-folder/job-hunt-os
```

Configure git identity (ask the user for name + email):
```bash
git config user.name "<their name>"
git config user.email "<their email>"
```

## Step 3: `.env` files
```bash
cp .env.example .env
cp infrastructure/.env.example infrastructure/.env
```

Generate a postgres password:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `infrastructure/.env` and replace `POSTGRES_PASSWORD` with the
generated value.

In the project `.env`, ask the user for:
- `JOB_HUNT_USER` — their slug (e.g., `jane-doe`)
- `NOCODB_URL` — default `http://localhost:8080`

Leave `NOCODB_API_TOKEN`, `NOCODB_BASE_ID`, and link-field IDs blank for
now — they're filled in after the data stack is up.

## Step 4: Python dependencies
```bash
python -m pip install python-docx pyyaml docx2pdf python-jobspy fpdf2 requests openai-whisper
```

Verify:
```bash
python -c "import docx, yaml, fpdf, requests; print('OK')"
```

## Step 5: Bring up the data stack
```bash
cd infrastructure
docker compose up -d
```

Wait ~30 seconds, then run `docker compose ps`. Both `postgres` and `nocodb`
should be healthy / running.

Tell the user to:
1. Visit `http://localhost:8080`.
2. Create a NocoDB admin user (any email + password — local only).
3. Add the postgres database as a Data Source: host `postgres`, port `5432`,
   user `jobhunt`, password from `infrastructure/.env`, database `jobhunt`.
4. NocoDB will discover all 7 tables.
5. Account → Tokens → create an API token.
6. Paste the token into the project `.env` `NOCODB_API_TOKEN`.

Wait for confirmation before continuing.

## Step 6: Discover schema IDs
```bash
cd ..   # back to repo root
python tools/setup/init-nocodb.py
```

This writes `NOCODB_BASE_ID` and 3 link-field IDs back to `.env`. If it
fails, the data source probably hasn't been added to NocoDB yet — ask the
user to revisit Step 5.

## Step 7: MCPs in `~/.claude.json`
Read `~/.claude.json` (or `C:\Users\<user>\.claude.json` on Windows). If it
exists, **merge** the new project entry — do NOT overwrite other projects.
If it doesn't exist, create it.

Get the absolute project path with `pwd` from the repo root. Use forward
slashes in the JSON key.

Add this project entry under `"projects"`:
```json
"<absolute path with forward slashes>": {
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
```

Substitute the actual `NOCODB_URL` and `NOCODB_API_TOKEN` values from the
user's `.env`.

If the user wants the LinkedIn MCP, add this entry to `mcpServers`:
```json
"linkedin": {
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "--rm", "-i", "--network", "host",
    "-v", "<user home, forward slashes>/.linkedin-mcp:/home/pwuser/.linkedin-mcp",
    "stickerdaniel/linkedin-mcp-server:latest"
  ]
}
```
Substitute `<user home, forward slashes>` with the user's home dir
(e.g., `C:/Users/jane` or `/home/jane`).

If the user wants the GitHub MCP (with their **own** PAT with `repo` scope):
```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<their PAT>" }
}
```

Install Playwright's chromium:
```bash
npx playwright install chromium
```

## Step 8: Health check
```bash
python tools/setup/first-run.py
```

If anything reports FAIL, address it before continuing. WARNs are usually
fine to proceed past.

## Step 9: Restart Claude Code
Tell the user to:
1. Close ALL Chrome / Chromium windows (check Task Manager / `pgrep -f chrome`).
2. Exit this session (`/exit` or Ctrl+C).
3. Open a new terminal, `cd` to `job-hunt-os/`, run `claude`.

MCP servers only load at startup — this restart is mandatory.

## Step 10: Verify and onboard
After restart, the user runs `/session-start`. Confirm MCP status table
shows NocoDB + Context7 + Playwright as Connected.

Then they select **"Onboard new user"** from the action menu (or run
`/onboard-user`). The full onboarding flow:
1. Intake — name, email, target roles, resume files
2. Initial job search — find 15-25 real postings in their target market
3. Role profiles — synthesise what the market demands
4. Resume extraction — parse resume(s) into structured YAML
5. Gap analysis — compare experience vs market
6. Interview — fill gaps the resume doesn't cover
7. Finalise — populate the database, save all data, ready to apply

Total time after bootstrap: ~60-90 minutes.

---

For troubleshooting specific issues, read `tools/bootstrap/BOOTSTRAP.md`.
