# Setup

> ⏳ Stub — full walkthrough lands in Phase 7. See [`docs/PLAN.md`](PLAN.md).

## Quick outline (subject to change)

1. **Prerequisites** — Docker Desktop, Python 3.11+, [Claude Code](https://docs.claude.com/en/docs/claude-code), an OpenRouter account (for the mock-interview tool), a GitHub PAT.
2. **Clone or template-instantiate** this repo.
3. **Bring up data backend**: `cd infrastructure && cp .env.example .env && docker compose up -d` → visit `http://localhost:8080` to create your NocoDB admin user → generate an API token.
4. **Initialise schema**: `python tools/setup/init-nocodb.py` (creates 8 tables, returns base ID + link-field IDs).
5. **Configure environment**: copy `.env.example` → `.env`; paste in NocoDB token + base ID, OpenRouter key, GitHub PAT.
6. **Configure user profile**: copy `config/user-profile.example.yaml` → `config/user-profile.yaml`; fill in your name, region, target roles, industries.
7. **Install MCPs**: `python tools/setup/first-run.py` (offers to add NocoDB MCP, Context7, optional LinkedIn MCP).
8. **Open in Claude Code**: `claude` → `/onboard-user` → ingest your resume → confirm extracted data.
9. **First skill run**: `/job-search` or `/cold-outreach`.
