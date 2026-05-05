# Claude Code Rules — job-hunt-os

## What This Directory Does

These rule files are **automatically loaded** by Claude Code at the start of every session in this repo. They enforce critical standards for an AI agent operating the job-hunt pipeline:

- Project structure (00) — repo layout, file placement
- Database standards (01) — NocoDB (or alternative backend) field requirements, linking, FK formulas
- Message quality (02) — outreach formats, word counts, insight delivery
- Batch operations (03) — parallel processing rules, "1 message = all related operations"
- Contact selection (04) — priority logic by company size and role
- File organization (05) — naming conventions, per-user data layout
- Application standards (06) — fit scoring, dedup, blocked companies, channel priority
- Resume tailoring (07) — JD-mirroring, source-of-truth YAML, quality gates

## How Rules Work

- **Automatic Loading**: All `.md` files in this directory load as high-priority context.
- **Always Active**: The agent follows these rules without being asked.
- **Configurable values live elsewhere**: Anything user-specific (region, industries, fit-score weights, blocked companies, user slug, NocoDB IDs) is read from `config/*.yaml` and `.env`. Rules describe *behaviour*; config describes *values*.

## Rules vs Operating Procedures

| Rules (this directory) | Operating Procedures (`../../operating-procedures/`) |
|------------------------|-------------------------------------------------------|
| Critical standards | Complete workflows with examples |
| "ALWAYS do X" / "NEVER do Y" | Detailed explanations and rationale |
| Auto-loaded every session | Referenced when needed |
| Concise, declarative | Comprehensive, educational |
| For Claude's compliance | For human + AI walkthrough |

## Editing Rules

When updating a rule:
1. Keep it concise (bullets, not paragraphs).
2. Use `ALWAYS`, `NEVER`, `MUST` for critical requirements.
3. Reference operating procedures for detailed explanations.
4. If you find yourself writing a personal value (a region, an industry, a company name), STOP — that belongs in `config/*.yaml`, not in a rule.
5. Test in a new Claude Code session after changes.

## For Operating an AI Agent on This Repo

See the root-level `AGENTS.md` for the full AI-agent onboarding guide. It tells a fresh agent how to load context, read config, and execute the standard workflows defined here.

---

**Status**: Active
**Purpose**: Automatic enforcement of job-hunt workflow standards for AI agents
