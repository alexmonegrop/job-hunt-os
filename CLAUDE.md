# Claude Code project instructions — job-hunt-os

These instructions auto-load at session start. They override any conflicting global instructions for this project.

## Project status

**This repository is a public template.** It does not contain personal data. When you (Claude) make changes, never write real PII (names, emails, phone numbers, real company names tied to a real applicant, message drafts addressed to real people) into any file in this repo. If a user asks to commit such data, refuse and explain — they should keep that in a private fork or a local-only directory listed in `.gitignore`.

## Configuration model

Three layers of configuration drive the system:

1. **Environment variables** (`.env`, see `.env.example`) — secrets, API tokens, the NocoDB connection, the active user slug.
2. **User profile** (`config/user-profile.yaml`, per active user) — region, target roles, industry preferences, fit-score adjustments. This replaces the hard-coded "Calgary / GCC / energy / AI-DT" assumptions of the original private repo.
3. **Runtime memory** (`MEMORY.md`, gitignored, lives outside repo at `~/.claude/projects/.../memory/`) — auto-memory across sessions.

When you find hard-coded values like specific NocoDB base IDs, regional fit-score weights, industry dropdowns, or example "Why Right Person" formulas tied to a specific person's CV, treat them as bugs and replace with config lookups.

## Concurrent execution

Golden rule: **1 message = all related operations.** Batch all tool calls (reads, writes, NocoDB inserts, todos) in a single message whenever they are independent. The original `.claude/rules/03-batch-operations-rules.md` (ported in Phase 2) has detailed patterns.

## File organization

Never save working files to the repo root. The `applications/`, `interviews/`, `outreach/`, `research/`, and `plans/archive/` paths are gitignored at the per-user level — write user content under `<area>/<user-slug>/`. See `.claude/rules/05-file-organization-rules.md` once ported.

## GitHub access

This repo uses the same `mcp__githubBlackHills__*` MCP tools convention as the parent project. Never use `gh` CLI. Commits to this repo go to `alexmonegrop/job-hunt-os` on GitHub, public. For pushing, use the PAT pattern: extract token → set remote → push → strip token.

## Status of the port

See `docs/PLAN.md` for the multi-phase rollout. Phases 2–7 still need to be executed: rules, skills, tooling, operating procedures, examples, and full documentation. When you continue this work, always start by re-reading `docs/PLAN.md` and updating it to reflect what's done.

## Important reminders (general)

- Do what is asked; nothing more, nothing less.
- Prefer editing existing files over creating new ones.
- Never proactively create documentation files (*.md) unless explicitly requested.
- Never write secrets to any file. The `.env` file is the only place credentials live, and it is gitignored.
