# Claude Code project instructions — job-hunt-os

These instructions auto-load at session start when working on the **template repo itself** (i.e., maintaining or extending `job-hunt-os`). They override any conflicting global instructions for this project.

> If you're an AI agent that has just been pointed at this repo to **operate the job-hunt pipeline** (rather than maintain the template), read **`AGENTS.md`** first instead of this file.

## Project status

**This repository is a public template.** It does not contain personal data. When making changes:

- **Never write real PII** (names, emails, phone numbers, real company names tied to a real applicant, message drafts addressed to real people) into any tracked file in this repo.
- If a user asks to commit such data, refuse and explain — they should keep that in a private fork or a local-only directory listed in `.gitignore`.
- The bundled fictional demo user is **Jane Demo** (`slug: jane-demo`). Use her data shape as the canonical reference for what fictional content looks like.

## Configuration model

Three layers of configuration drive the system:

1. **Environment variables** (`.env`, see `.env.example`) — secrets, API tokens, the NocoDB connection, the active user slug, MCP tool prefix.
2. **User profile** (`config/user-profile.yaml`, per active user — gitignored) — region, target roles, target industries, excluded companies, credibility anchors, value props, credentials. This replaces the original private repo's hardcoded assumptions about region / industry / role.
3. **Runtime memory** (`MEMORY.md`, gitignored, lives outside repo at `~/.claude/projects/<hash>/memory/`) — auto-memory across sessions.

When you find hardcoded values in rules / skills / procedures (specific NocoDB base IDs, regional fit-score weights, industry vocabulary, example "Why Right Person" formulas tied to a specific person's CV), treat them as bugs and replace with config lookups.

## Concurrent execution

Golden rule: **1 message = all related operations.** Batch all tool calls (reads, writes, database inserts, todos) in a single message whenever they are independent. See `.claude/rules/03-batch-operations-rules.md` for the full patterns.

## File organization

Never save working files to the repo root. The `applications/`, `interviews/`, `outreach/`, `research/`, and `plans/archive/` paths are gitignored at the per-user level — write user content under `<area>/<user-slug>/`. See `.claude/rules/05-file-organization-rules.md`.

## GitHub access

For pushing this repo to GitHub:
- Use whichever GitHub MCP your environment has configured, OR fall back to `git push` over HTTPS with a PAT.
- The repo lives at `alexmonegrop/job-hunt-os` on GitHub (public).
- For PAT-based pushing, use the documented pattern: extract token → set remote → push → strip token. **NEVER leave a PAT in the remote URL.** See `docs/SETUP.md` and the `session-end` skill for the exact command.
- Don't use `gh` CLI if your environment authenticates a different account — use a configured MCP, or git directly with PAT-in-URL.

## Status of the port

See `docs/PLAN.md` for the full rollout history.

**Current state (as of v1 release)**: All 7 phases complete. The v1 template ships with rules, skills, operating procedures, configuration, Python tooling (resume tailor + quality gate, job search, interview/transcription, NocoDB bootstrap), Docker infrastructure (postgres + NocoDB), demo data (Jane Demo), and full documentation.

When you continue this work, always start by re-reading `docs/PLAN.md` and updating it to reflect what's done. The validation gates at the end of each phase are not optional.

## When extending the template

Read `docs/EXTEND.md` first. It covers:
- Adding new rules, skills, tools, operating procedures.
- Adding new database backends.
- Adding employer extensions (the namespaced per-employer pattern).
- The fork-vs-PR decision.

## Important reminders (general)

- **Do what is asked; nothing more, nothing less.**
- **Prefer editing existing files over creating new ones.**
- **Never proactively create documentation files (`*.md`) unless explicitly requested.** This repo has the right docs already; don't add more without a clear need.
- **Never write secrets to any file.** The `.env` file is the only place credentials live, and it is gitignored.
- **Never commit a real `li_at` cookie, PAT, or password.** They live in `.env` (gitignored) or `~/.claude.json` (local).
- **Sanitise everything.** If a rule, skill, or doc still contains a real person's name or company, that's a bug — fix it before committing.
- **Forbidden-token grep before every commit** that touches rules / skills / procedures / docs (excluding `docs/PLAN.md` and `docs/MIGRATION-FROM-PRIVATE-FORK.md`, which are migration meta-docs that intentionally reference the deprecated tokens).

## See also

- `AGENTS.md` — for AI agents operating the job-hunt pipeline (not maintaining the template).
- `docs/PLAN.md` — multi-phase rollout history.
- `docs/EXTEND.md` — how to extend the template.
- `docs/CONTRIBUTING.md` — PR conventions.
- `docs/MIGRATION-FROM-PRIVATE-FORK.md` — for maintainers of a private fork.
