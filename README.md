# job-hunt-os

**An agentic job-hunt operating system for [Claude Code](https://docs.claude.com/en/docs/claude-code) (or any compatible AI-agent tool).**

Fork this template, plug in your resume, and run a structured pipeline of cold outreach, networking follow-ups, job discovery, resume tailoring, and application tracking — all coordinated by an AI agent.

> Status: **v1 template complete.** Rules, skills, operating procedures, configuration, Python tooling, Docker infrastructure, demo data, and documentation are all in place — see [`docs/PLAN.md`](docs/PLAN.md) for the rollout history.

> AI agents picking up this repo: read **[`AGENTS.md`](AGENTS.md)** first. It's the canonical onboarding doc for the AI operator.

---

## What you get

- **Auto-loaded rules** (`.claude/rules/`) — 9 rule files defining database hygiene, message quality, batch operations, contact selection, file organisation, application protocol, and resume tailoring. The agent follows these without being asked.
- **Invokable skills** (`.claude/skills/`) — 13 slash commands:
  - `/cold-outreach`, `/contact-population`, `/meeting-prep`, `/company-deep-dive`, `/warm-followup`
  - `/job-search`, `/resume-tailor`, `/apply`, `/application-tracker`
  - `/onboard-user`, `/session-start`, `/session-checkpoint`, `/session-end`
- **Operating procedures** (`operating-procedures/`) — 9 long-form methodology docs covering outreach (v4), meeting prep (v4), resume tailoring, direct application, contact population, insight development, message examples, application-speed lessons, and video-transcription analysis.
- **Configurable everything** (`config/*.yaml`) — your region, target roles, industries, fit-score weights, and excluded companies live in YAML. Same agent, any market.
- **A bundled demo user** ("Jane Demo") with a full fictional dataset and an end-to-end walkthrough at [`plans/EXAMPLES/jane-demo-walkthrough.md`](plans/EXAMPLES/jane-demo-walkthrough.md).
- **Reference templates** for the master-experience YAML and cover letters.
- **Tools** (`tools/`) — Python CLIs for resume tailoring (with quality gate), JobSpy job discovery, mock-interview LLM, NocoDB schema initialisation, and onboarding bootstrap.
- **Infrastructure** (`infrastructure/`) — Docker Compose stack for self-hosted NocoDB + Postgres (Caddy reverse proxy as an opt-in profile), with seed schema.
- **Employer-extension example** (`tools/employer-extension-example/`) — a documented pattern for extending the system per-employer.

---

## Who this is for

- Job seekers who use Claude Code (or compatible) and want a pipeline-driven hunt instead of ad-hoc applications.
- People comfortable self-hosting Docker on their machine (NocoDB stack).
- Anyone who wants a working example of a multi-skill, rule-driven agentic system.

---

## Quickstart

```bash
# 1. Use this template (or fork)
gh repo create my-job-hunt --template <your-org>/job-hunt-os --private

# 2. Bring up the data backend
cd my-job-hunt/infrastructure && cp .env.example .env && docker compose up -d

# 3. Initialise the schema and install Claude Code MCPs
python tools/setup/init-nocodb.py
python tools/setup/first-run.py

# 4. Customise config
cd my-job-hunt
cp config/user-profile.example.yaml config/user-profile.yaml
cp config/fit-score.example.yaml config/fit-score.yaml
cp config/industries.example.yaml config/industries.yaml
cp config/regions.example.yaml config/regions.yaml
# Edit each to match your situation.

# 5. Set the active user
cp .env.example .env
# Edit .env: set JOB_HUNT_USER, NOCODB_*, etc.

# 6. Open in Claude Code and run /onboard-user
claude
> /onboard-user
```

Full setup walkthrough: [`docs/SETUP.md`](docs/SETUP.md).
Customisation guide: [`docs/CUSTOMIZE.md`](docs/CUSTOMIZE.md).
Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Walkthrough: [`docs/EXAMPLES.md`](docs/EXAMPLES.md).

---

## Architecture in one paragraph

Rules (`.claude/rules/*.md`) auto-load at session start and define non-negotiable standards. Skills (`.claude/skills/*/SKILL.md`) are invokable workflows. Operating procedures (`operating-procedures/*.md`) are long-form methodology references the skills point to. Tools (`tools/`) are CLI utilities the skills shell out to. Configuration (`config/*.yaml` + `.env`) holds your region, target roles, fit-score weighting, industry vocabulary, and credentials — making the same agent useful in any market. Data lives in NocoDB by default; per-user content lives under `applications/{slug}/`, `interviews/{slug}/`, `outreach/{slug}/`, `research/{slug}/`, all gitignored at the user level.

More: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## License

[MIT](LICENSE). Use, fork, modify, redistribute. No warranty.

## Origin

Extracted from a real, working private job-hunt repo that ran a successful 12-month pipeline (~110 applications, ~500 networked contacts, multiple offers received and one role accepted). The public template strips all personal data, contact lists, message archives, and employer-specific artefacts; only the methodology, tooling structure, and rules remain.

## Contributing

PRs welcome — see [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md). The system is opinionated by design; if your workflow diverges, fork freely.
