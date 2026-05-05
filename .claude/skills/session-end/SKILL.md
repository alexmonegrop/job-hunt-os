---
name: "session-end"
description: "End-of-session wrap-up: update MEMORY.md with lessons learned, capture session summary with what was done and what's next, update overall plan and any active sub-plans, and prepare handoff notes for the next session. Use at the end of every work session."
user_invocable: true
---

# Session End

Standardized session wrap-up to preserve context across sessions.

## What This Skill Does

1. **Capture lessons learned** — check if anything should be added to rules, skills, or memory.
2. **Update MEMORY.md** — record key facts, technical details, and project state changes.
3. **Update plans** — overall plan + any active sub-plan.
4. **Write session summary** — what was done, what's pending, what to do next.
5. **Git commit + push** — commit all changes and push to GitHub.
6. **MCP health check** — note which MCPs are connected/disconnected for next session.

## Workflow

### Step 1: Lessons-learned check

Review the session for:
- Mistakes that could be prevented with a rule
- Repeated workflows that could become a skill
- Technical discoveries worth remembering
- Rules or skills that need updating based on what happened

If lessons found: present to user for approval before updating rules/skills.
If no lessons: skip — don't force it.

### Step 2: Update MEMORY.md

Update the project's MEMORY.md with:
- Any new project structure changes
- New technical details discovered
- Updated database status (table IDs, field changes)
- Tool/dependency changes
- Key decisions made this session

Keep MEMORY.md under 200 lines.

### Step 3: Update plans (MANDATORY)

#### 3a: Update overall plan (ALWAYS do this)

File: `plans/OVERALL-PLAN.md` (create if not present).

This is the living master plan. Update every session with:
- **Last Updated** date at the top
- **Workstream progress** — counts, milestones, completed items
- **Current Priorities** — adjust based on what was done and what's next
- **Blockers** — add new ones, remove resolved ones
- **Key Metrics** — update the snapshot table if numbers changed
- **Session History** — add a row for this session
- **Next Session Checklist** — concrete next steps

#### 3b: Update active sub-plan (if any)

If there's an active sub-plan in `plans/[date]/`:
1. Read the plan file.
2. Update phase/step completion status (✅ for done, ⬜ for pending).
3. Add any newly discovered blockers or decisions.
4. Note the exact resumption point ("Resume at Phase X, Step Y").

If no active sub-plan, skip.

### Step 4: Write session summary

Create: `plans/archive/SESSION-SUMMARY-{user-slug}-YYYY-MM-DD.md`

```markdown
# Session Summary — {user-slug} — YYYY-MM-DD

## What Was Done
- ...

## What's Pending
- ...

## Next Session Priorities
1. ...
2. ...
3. ...

## MCP Status
- nocodb: [Connected/Disconnected]
- linkedin: [Connected/Disconnected]
- context7: [Connected/Disconnected]
- playwright: [Connected/Disconnected]

## Files Modified This Session
- ...

## Notes for Next Session
- ...
```

If multiple sessions on the same date, append a letter suffix: `SESSION-SUMMARY-{user-slug}-YYYY-MM-DDb.md`.

### Step 5: File-state check + git sync

This project IS a git repo. The remote is whatever you configured during setup (typically a fork of `<your-org>/job-hunt-os`).

```bash
git add -A
git status --short

git commit -m "Session $(date +%Y-%m-%d): <brief summary>"

# Push using whatever auth your environment has configured.
# If using PAT-in-URL pattern (documented in docs/SETUP.md):
#   1. Set remote with PAT
#   2. Push
#   3. Strip PAT from remote (ALWAYS — even if push fails)
git push origin main
```

Report: "Git: committed N files, pushed to origin/main" or "Git: push failed — [error]".

List key files created/modified during the session in the session summary under "Files Modified This Session".

### Step 6: Confirm ready

Tell the user: "Session wrapped up. You can restart Claude Code — the next session will pick up from MEMORY.md, the overall plan, and the session summary."

## Rules

1. **NEVER skip MEMORY.md update** — it's loaded into every session's context.
2. **NEVER skip overall plan update** — it's the master tracker across all sessions.
3. **Keep MEMORY.md concise** — under 200 lines, link to other files for details.
4. **Don't create lessons that don't exist** — if nothing was learned, say so.
5. **Ask before updating rules/skills** — present proposed changes for approval.
6. **Always note MCP status** — saves debugging time in the next session.
7. **Always update active sub-plan** — if a multi-session plan is in progress, update its status.
8. **ALWAYS git commit + push at session end** — the repo is the shared source of truth.
9. **NEVER leave a PAT in the remote URL** — strip it after every push, even on failure.
