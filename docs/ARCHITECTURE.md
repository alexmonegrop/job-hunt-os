# Architecture

> ⏳ Stub — full architecture write-up lands in Phase 7. See [`docs/PLAN.md`](PLAN.md).

## Four-layer model

1. **Rules** (`.claude/rules/*.md`) — auto-loaded into every Claude Code session. Non-negotiable standards (database hygiene, message quality, batch ops, file org, application protocol, resume tailoring).
2. **Skills** (`.claude/skills/*/SKILL.md`) — invokable workflows triggered by `/skill-name`. Each skill orchestrates a multi-step task (e.g., `/cold-outreach` = research company → select contacts → draft messages → save to filesystem → log to NocoDB).
3. **Operating procedures** (`operating-procedures/*.md`) — long-form methodology docs that skills point to for detailed explanations. The "why" behind the "what".
4. **Tools** (`tools/`) — CLI utilities that skills shell out to (Python scripts for resume tailoring, job search, mock interviewing).

## Configuration model

Three layers:
- **`.env`** — secrets, API keys, NocoDB connection, active user.
- **`config/*.yaml`** — user profile, fit-score weights, industries, regions.
- **`MEMORY.md`** (gitignored, lives at `~/.claude/projects/.../memory/`) — persistent auto-memory across Claude Code sessions.

## Data flow

```
[Claude Code session]
       ↓ invokes skill
[Skill: SKILL.md]
       ↓ reads
[Rules + Operating procedures + Config]
       ↓ shells out to
[Tools (Python CLIs)]
       ↓ reads/writes via MCP
[NocoDB tables: users, target_companies, target_contacts, sales_pipeline,
 interactions, job_postings, applications]
       ↓ side-effects on
[Filesystem: applications/, interviews/, outreach/, research/, plans/]
```

## Tables

8 NocoDB tables (initialised by `tools/setup/init-nocodb.py`):
- `users` — multi-user support (optional; defaults to a single `default` user).
- `target_companies` — companies in your hunt (with `why_strong_fit` and `recent_signals`).
- `target_contacts` — people inside those companies.
- `sales_pipeline` — outreach pipeline stages per contact.
- `interactions` — log of every message, meeting, follow-up.
- `job_postings` — discovered jobs, scored, with status.
- `applications` — submitted applications.
- `Features` — internal feature flags (optional).

The full schema lives in `infrastructure/init-db/02-jobhunt-schema.sql`.
