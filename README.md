# job-hunt-os

**An agentic job hunt operating system for [Claude Code](https://docs.claude.com/en/docs/claude-code).**

Fork this template, plug in your resume, and run a structured pipeline of cold outreach, networking follow-ups, job discovery, resume tailoring, and application tracking — all coordinated by Claude.

> ⚠️ **Status: scaffold (Phase 1 of 7).** This repo currently contains the structure, plan, and skeleton config only. The agent rules, skills, tooling, and operating procedures are being ported in over subsequent phases. See [`docs/PLAN.md`](docs/PLAN.md) for the rollout.

---

## What you get (when fully ported)

- **Rule files** that auto-load into Claude Code at session start, enforcing standards for database hygiene, message quality, batch operations, contact selection, file organization, application protocol, and resume tailoring.
- **Skills** (`/cold-outreach`, `/job-search`, `/apply`, `/resume-tailor`, `/meeting-prep`, `/warm-followup`, `/application-tracker`, `/onboard-user`, `/session-start`, `/session-end`, etc.) — invoke as slash commands.
- **Tools**:
  - `tools/resume-tailor/` — score achievements against a JD, rewrite bullets, generate `.docx` + `.pdf` with a quality gate.
  - `tools/job-search/` — multi-board discovery (LinkedIn, Indeed, Glassdoor, Bayt, GulfTalent, NaukriGulf) via [JobSpy](https://github.com/Bunsly/JobSpy) + Playwright + WebSearch.
  - `tools/interview/` — LLM-driven mock interview with role-specific recruiter feedback.
  - `tools/bootstrap/` — onboard additional users to a shared system.
  - `tools/setup/` — initialise a fresh NocoDB schema, install MCPs, verify environment.
- **Operating procedures** — long-form methodology docs for outreach, contact population, direct application, resume tailoring, and meeting prep.
- **Infrastructure**: Docker Compose stack for self-hosted [NocoDB](https://www.nocodb.com/) + [n8n](https://n8n.io/), with optional [Caddy](https://caddyserver.com/) and [Tailscale](https://tailscale.com/) for remote access.

## Who is this for

- Job seekers who use Claude Code and want a pipeline-driven hunt instead of ad-hoc applications.
- People comfortable self-hosting Docker on their machine (NocoDB stack).
- Anyone who wants a working example of a multi-skill, rule-driven agentic system.

## Quickstart (post-MVP)

```bash
# 1. Use this template (or clone)
gh repo create my-job-hunt --template alexmonegrop/job-hunt-os --private

# 2. Bring up the data backend
cd my-job-hunt/infrastructure
cp .env.example .env  # fill in NOCODB_*, OPENROUTER_API_KEY, etc.
docker compose up -d

# 3. Initialise the schema and install Claude Code MCPs
python tools/setup/init-nocodb.py
python tools/setup/first-run.py

# 4. Open the project in Claude Code and run /onboard-user
claude
> /onboard-user
```

Full setup walkthrough: [`docs/SETUP.md`](docs/SETUP.md). Customisation guide: [`docs/CUSTOMIZE.md`](docs/CUSTOMIZE.md).

## Architecture in one paragraph

Rules (`.claude/rules/*.md`) auto-load at session start and define non-negotiable standards. Skills (`.claude/skills/*/SKILL.md`) are invokable workflows. Operating procedures (`operating-procedures/*.md`) are long-form methodology references the skills point to. Tools (`tools/`) are CLI utilities the skills shell out to. Configuration (`config/*.yaml`) holds your region, target roles, fit-score weighting, industry vocabulary — making the same agent useful in any market. Data lives in NocoDB; the schema is initialised from `infrastructure/init-db/`.

More: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## License

[MIT](LICENSE). Use, fork, modify, redistribute. No warranty.

## Origin

Extracted from a real, working private job-hunt repo that ran a successful 12-month pipeline (~110 applications, ~500 networked contacts, multiple offers received and one role accepted). The public template strips all personal data, contact lists, message archives, and employer-specific artifacts; only the methodology, tooling, and rules remain.

## Contributing

PRs welcome — see [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md). The system is opinionated by design; if your workflow diverges, fork freely.
