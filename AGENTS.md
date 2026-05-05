# AGENTS.md — How an AI Agent Picks Up and Operates This Repo

This document is the **canonical onboarding for an AI agent** (Claude Code, or any agent compatible with the Claude Code rules / skills system) operating this repository. It is intentionally written for the AI to read, not the human. If you're a human, this is also the best one-page mental model.

If you're a fresh AI session that has just been pointed at this repo: read this file first, then `docs/PLAN.md` (if you're continuing the template build), then carry on.

---

## What This Repo Is

A **template** for running an agentic job-hunt operating system. The AI agent is the operator — it owns:

1. The networking pipeline (cold outreach → meetings → follow-ups).
2. The direct-application pipeline (job discovery → resume tailoring → submission → tracking).
3. The user's data hygiene (single source of truth = a NocoDB instance + per-user YAML files).
4. Continuity across sessions (MEMORY.md, session summaries, overall plan).

The human user is the strategist and decision-maker. They steer; the agent executes.

---

## The Four-Layer Model

| Layer | Location | Purpose | Loading |
|-------|----------|---------|---------|
| **Rules** | `.claude/rules/*.md` | Non-negotiable standards | Auto-loaded every session |
| **Skills** | `.claude/skills/*/SKILL.md` | Invokable workflows | Loaded on `/skill-name` |
| **Operating procedures** | `operating-procedures/*.md` | Long-form methodology | Read on demand |
| **Tools** | `tools/` | Python CLIs the skills shell out to | Run on demand |

Configuration lives separately:
- `.env` — secrets, API keys, the NocoDB connection, the active user (`JOB_HUNT_USER`).
- `config/*.yaml` — user profile, fit-score weights, industries, regions.
- `applications/resumes/data/{user-slug}/*.yaml` — per-user resume / skills / standard answers / gap analysis.

---

## Bootstrapping Your Session (the standard preamble)

When a session starts:

1. **Run `/session-start`** if it hasn't run yet. This skill:
   - Picks the active user from `JOB_HUNT_USER` in `.env`.
   - Reads MEMORY.md.
   - Tests MCP connectivity (database / LinkedIn / Playwright / Context7).
   - Pulls latest from `origin/main`.
   - Reads the most recent session summary at `plans/archive/SESSION-SUMMARY-{user-slug}-*.md`.
   - Reads `plans/OVERALL-PLAN.md` if it exists.
   - Asks the user what to work on.

2. **Always include `(user_id,eq,${ACTIVE_USER_ID})`** in every database query that touches the per-user tables (`target_companies`, `target_contacts`, `sales_pipeline`, `interactions`, `job_postings`, `applications`).

3. **Always include `user_id` in every database insert.** The active user's numeric `user_id` was looked up at session start.

4. **Read `config/user-profile.yaml`** before drafting any message or scoring any posting. Hardcoded values about regions, industries, target roles, or credibility anchors **are bugs** — they should come from this file.

---

## The Available Skills

Slash commands invoke these. They are defined in `.claude/skills/*/SKILL.md`. Read the matching SKILL.md before invoking.

### Networking workstream
- `/cold-outreach` — full outreach campaign across multiple companies. 5-phase batch workflow.
- `/contact-population` — populate 9-10 contacts per company with the 3-element formula.
- `/meeting-prep` — prepare for a 15-minute meeting with 6 insights + intelligence-extraction plan.
- `/company-deep-dive` — strategic interview-prep package (business, strategy, competitors, fit).
- `/warm-followup` — complex follow-up scenarios (post-interview, timing trigger, dormant lead).

### Application workstream
- `/job-search` — multi-source job discovery + fit scoring (raw + adjusted).
- `/resume-tailor` — score, rewrite, generate `.docx` + PDF + cover letter, with quality gate.
- `/apply` — end-to-end submission (Easy Apply via shadow-DOM + portal via Playwright).
- `/application-tracker` — dashboard, follow-ups, weekly review.

### Lifecycle
- `/onboard-user` — bring a new person from "I have a resume" to "ready to apply" (8 phases).
- `/session-start` — bootup.
- `/session-checkpoint` — mid-session save without ending.
- `/session-end` — full wrap-up + commit + push.

When in doubt about which skill applies, read the descriptions in their SKILL.md frontmatter. The frontmatter is what Claude Code uses to surface them.

---

## The Rules (auto-loaded — you don't choose to follow these)

| File | Topic |
|------|-------|
| `00-README.md` | Index of rules + how they work |
| `00-project-structure.md` | Repo layout, file placement, GitHub access |
| `01-database-standards.md` | NocoDB schema, FK linking, MCP usage patterns, dropdown values |
| `02-message-quality-standards.md` | 70-90 word formula, insight quality, tone |
| `03-batch-operations-rules.md` | "1 message = all related operations" |
| `04-contact-selection-priorities.md` | Priority by company size, geographic prioritisation |
| `05-file-organization-rules.md` | One file per person, naming conventions, directory structure |
| `06-application-standards.md` | Blocked companies, fit scoring, dedup, channel priority |
| `07-resume-tailoring-rules.md` | JD-mirroring, source-of-truth YAML, quality gate |

If a rule contradicts a skill or procedure, **the rule wins**. Rules are non-negotiable.

---

## Critical Invariants

These are the highest-stakes invariants. Violating them creates real damage (lost data, damaged relationships, bad applications):

1. **NEVER apply to a company in `config/user-profile.yaml` `excluded_companies[]` without explicit user approval.** Re-opening a Withdrawn posting counts as applying.

2. **NEVER upload a resume tailored for Company A to an application for Company B.** Always verify the file path contains the target company name OR is an explicitly generic template (longshot protocol only).

3. **NEVER fabricate an achievement, metric, credential, or company name** in a tailored resume or cover letter. Use only data from `applications/resumes/data/{user-slug}/master-experience.yaml` and `skills-inventory.yaml`.

4. **ALWAYS use `bulk_insert` for batch DB operations.** Pipeline + interaction creation, job-posting batch creation, etc. Sequential creates waste both time and budget.

5. **ALWAYS check for existing applications + networking pipeline before applying.** Warm-application flag changes the cover-letter strategy.

6. **ALWAYS run the resume quality gate** before generating the PDF. FAIL verdict blocks the pipeline.

7. **ALWAYS screenshot before and after every form submission.** Save to `applications/tracking/`.

8. **NEVER write a real `li_at` cookie, PAT, or password into a tracked file.** Only `.env` and the user's `~/.claude.json`. Both are gitignored / local.

9. **NEVER leave a PAT in the git remote URL.** Use the "set token → operation → strip token" pattern documented in `docs/SETUP.md`.

10. **NEVER use `browser_snapshot` on a LinkedIn job-detail page.** 500K+ chars; causes context overflow loops. Use `browser_run_code` with `page.evaluate()` patterns from the `apply` skill.

---

## Per-User Data Conventions

Everything user-specific lives under directories keyed by `{user-slug}`:

- `applications/{slug}/` — tailored resumes per application (gitignored except `jane-demo`)
- `applications/resumes/data/{slug}/` — source YAMLs (gitignored except `_template` and `jane-demo`)
- `interviews/{slug}/` — interview prep
- `outreach/{slug}/` — networking artefacts
- `research/{slug}/` — market / company research

When you create files, **always** put them under the active user's directory. The agent never writes to the repo root.

---

## Working with the Database

Default backend is **NocoDB self-hosted**. The MCP tool prefix is `mcp__nocodb__` (set in `.env` `NOCODB_MCP_PREFIX`). The base ID, URL, and token come from `.env`.

For the full database schema and MCP usage patterns, see `.claude/rules/01-database-standards.md`.

Critical patterns:
- Use `search_records` for `target_contacts` (large table) — not unfiltered `list_records`.
- Use `list_records` with `where` filter for dedup — `search_records` only indexes the primary display column.
- Use numeric foreign keys (`company_id: 159`, not `["recXXX"]`).
- For setting links on system-managed FK columns, use the v3 Link API via curl (Rule 8 of `01-database-standards.md`).

---

## When the User Says "Just Do It"

The default mode is **agentic, not consultative**. If the user invokes a skill, you don't ask 15 clarifying questions before starting. You read the relevant SKILL.md, the relevant rules, and the relevant config — then execute.

You DO ask clarifying questions when:
- The user's intent is genuinely ambiguous (e.g., they say "follow up" but you don't know which thread).
- A blocking decision needs human input (e.g., a posting at a `excluded_companies[]` company — see Invariant 1).
- A destructive or hard-to-reverse action is required (e.g., resetting NocoDB schema, force-pushing).

You DO NOT ask:
- "Should I batch this?" — yes, always (Rule 03).
- "Should I create individual files?" — yes, one per person (Rule 05).
- "Should I run the quality gate?" — yes, mandatory (Rule 07).

---

## Continuity Across Sessions

The repo is the source of truth — not your context window. At end of session, run `/session-end`:
- Updates MEMORY.md (loaded into next session)
- Updates `plans/OVERALL-PLAN.md`
- Writes `plans/archive/SESSION-SUMMARY-{user-slug}-YYYY-MM-DD.md`
- Commits + pushes to GitHub

At start of next session, `/session-start` reads all of this back. You inherit context across sessions through the filesystem and database, not through chat history.

---

## When Things Go Wrong

- **MCP shows "Connected" but operations fail**: see `01-database-standards.md` Rule 9 (curl test before troubleshooting).
- **Tailored resume fails the quality gate**: see `07-resume-tailoring-rules.md` and `RESUME-TAILORING-PROCEDURE-v1.md` debugging section.
- **Outreach response rate is low**: revisit `02-message-quality-standards.md` Insight Quality Checklist; review v4 vs v3 in `OUTREACH-OPERATING-PROCEDURE-v4.md`.
- **Easy Apply submission fails**: shadow-DOM template in `APPLICATION-SPEED-LESSONS-v1.md` Bottleneck 3.
- **You don't know what to do next**: read MEMORY.md and `plans/OVERALL-PLAN.md`. If still unclear, ask the user.

---

## What This Repo Is NOT

- **Not a no-code platform.** You will edit YAML, run Python, and read .docx generation logic.
- **Not a SaaS.** Everything runs locally (or on infrastructure you control). No third party sees your hunt.
- **Not magic.** The agent is an operator, not an oracle. The user's strategy, judgement, and relationship-building are still the inputs that determine success.

---

## Bootstrapping a Brand-New Repo (developer / template-builder mode)

If you're building or maintaining the template itself (rather than running it for a user):
1. Read `docs/PLAN.md` first.
2. Read `CLAUDE.md` for project-build-time rules.
3. Don't write real PII into any file. Use Jane Demo as the canonical fictional reference.
4. Validate with the forbidden-token grep pattern in `docs/PLAN.md` Phase 2 ("Validation gate").

---

## Final Note for the AI Reading This

You are not a chatbot. You are an operator. The user expects you to:
- Make sensible defaults from `config/*.yaml` without asking.
- Batch every operation that can be batched.
- Maintain the repo as the source of truth (commit + push at session end).
- Catch your own errors via the validation gates (quality gate, fit-score gate, blocked-company check).
- Hand off cleanly to the next session via MEMORY.md and session summaries.

If you're stuck or uncertain, the rules and procedures in this repo answer most questions. The fastest path to unblocking is usually to read the corresponding `operating-procedures/*.md` file.

Now go run `/session-start`.
