---
name: "session-start"
description: "Start-of-session bootup: select active user, test MCP connectivity (database, LinkedIn), check MEMORY.md for priorities, review last session summary, verify tool health, and present a prioritized action menu. Use at the beginning of every work session."
user_invocable: true
---

# Session Start

Standardized session bootup to quickly orient and verify all systems are working.

## What This Skill Does

1. **Select active user** — ask who is using the system (or onboard a new user).
2. **Read MEMORY.md** — load current project state and priorities.
3. **Find last session summary** — check what was done and what's next.
4. **Test MCP connectivity** — verify database, LinkedIn, Context7, Playwright.
5. **Quick database health check** — confirm base access, list tables.
6. **Present action menu** — show prioritized options for this session.
7. **Git pull (latest)** — sync with remote.

## Workflow

### Step 0: Select active user

ALWAYS start by identifying who is using the system. Read `JOB_HUNT_USER` from `.env`. If unset or set to a value not present in the database `users` table, proceed with selection:

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "users",
  fields: "id,full_name,slug,location,target_roles",
  limit: 10
})
```

Present an `AskUserQuestion` with:
- One option per existing user (show name + location).
- A "New user (onboard someone new)" option.

If the user picks an existing person:
- Set that person as the active user for the session.
- Load their `applications/resumes/data/{slug}/user-config.yaml`.
- Use their `user_id` for all DB queries this session.

If the user picks "New user":
- Invoke `/onboard-user` — the full automated onboarding flow.
- After onboarding completes, continue with normal session start for the new user.

Store the active user slug in session context. All subsequent skills and queries should use this user's data.

### Step 1: Load context

Read MEMORY.md (already in system prompt for Claude Code, but review the "Next Session Priorities" and status sections explicitly).

Find and read the most recent session summary for this user:
```
Glob for: plans/archive/SESSION-SUMMARY-{user-slug}-*.md
Read the most recent one (by date in filename).
```

Read the overall plan: `plans/OVERALL-PLAN.md` (if present). This is the living master plan with workstream status, metrics, blockers, and next steps.

Find and read any active sub-plan (if any):
```
Check MEMORY.md and OVERALL-PLAN.md for "IN PROGRESS" references.
Glob for: plans/**/*.md (excluding archive/) — find plans with incomplete steps.
Read any plan with incomplete steps (⬜ markers or "Resume at" notes).
```

If no session summary or plan found, note it and continue.

### Step 2: Test MCP connectivity (parallel)

```javascript
// Database (NocoDB by default)
mcp__nocodb__list_tables({ base_id: "${NOCODB_BASE_ID}" })

// LinkedIn
mcp__linkedin__get_company_profile({ company_name: "anthropic" })

// Context7 (if configured)
mcp__context7__resolve_library_id({ libraryName: "python" })
```

Report results as a status table.

### Step 3: Database health check

If the database MCP is connected, run:
```javascript
mcp__nocodb__list_tables({
  base_id: "${NOCODB_BASE_ID}",
  detailLevel: "tableIdentifiersOnly"
})
```

Report:
- Number of tables found
- Whether `job_postings` and `applications` tables exist
- Any tables with unexpected names

### Step 4: Check pending must-dos

Review MEMORY.md "Next Session Must-Dos". For each item: mark DONE / PENDING / BLOCKED.

### Step 5: Present action menu

Based on context gathered, present the user with a prioritised action menu via `AskUserQuestion`:

1. **Infrastructure setup** — if tables need creating, MCPs need fixing, etc.
2. **Networking outreach** — cold outreach, contact population, follow-ups
3. **Job search** — run job searches, review postings, score opportunities
4. **Application prep** — tailor resumes, draft cover letters, prepare applications
5. **Meeting prep** — prepare for upcoming meetings/interviews
6. **Free-form** — user has a specific task in mind

### Step 6: Git pull (sync with remote)

ALWAYS pull latest from GitHub before starting work — the repo can be the shared source of truth across users / sessions.

```bash
git pull --rebase origin main
```

If using PAT-in-URL pattern (when SSH keys / credential cache aren't available), use the documented "set token → operation → strip token" pattern from `docs/SETUP.md`. NEVER leave a PAT in the remote URL.

- If succeeds: "Git: synced with remote"
- If conflicts: "Git: CONFLICTS — resolve before proceeding" (show conflicting files)
- If 401: "Git: PAT expired — regenerate per docs/SETUP.md"
- If network failure: "Git: pull failed — working offline, will sync later"

Report git sync status in the output table alongside MCP status.

## Output Format

```
## Session Start — YYYY-MM-DD
**Active User**: [Name] (user_id: X, slug: [slug])

### MCP Status
| Service | Status | Notes |
|---------|--------|-------|
| Database | ✅ / ❌ | [details] |
| LinkedIn | ✅ / ❌ | [details] |
| Context7 | ✅ / ❌ | |
| Playwright | ✅ / ❌ | |
| Git | ✅ / ❌ | |

### Database Tables
[List of tables]

### Last Session ([date])
**Done**: [brief]
**Next**: [priorities]

### Overall Plan
**Workstreams**: [summary]
**Blockers**: [active blockers]

### Active Sub-Plan (if any)
**Plan**: [name + path]
**Resume at**: [Phase X, Step Y]
**Remaining**: [count]

### Pending Must-Dos
- [ ] / [x] Item 1
- [ ] / [x] Item 2

### What would you like to work on?
[AskUserQuestion]
```

## Rules

1. **Run MCP tests in parallel** — don't test sequentially.
2. **Don't block on MCP failures** — report status and continue.
3. **Keep output concise** — status table, not paragraphs.
4. **Always end with action menu** — user picks what to work on.
5. **If LinkedIn MCP fails, suggest checking Docker** — most common issue.
6. **If database MCP fails, suggest checking credentials** — second most common.
7. **Git pull BEFORE any work** — another user / session may have pushed changes.
8. **Never leave a PAT in the remote URL.**
