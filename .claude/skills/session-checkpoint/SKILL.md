---
name: "session-checkpoint"
description: "Mid-session checkpoint: save progress to MEMORY.md, update active plan status, write/append session summary, and note lessons learned — then continue working. Use when switching focus areas or after completing a major milestone within a session."
user_invocable: true
---

# Session Checkpoint

Mid-session save point that preserves all context without ending the session.

## How It Differs From Session End

| Checkpoint | Session End |
|-----------|-------------|
| Saves progress, keeps working | Saves progress, wraps up |
| Appends to existing session summary | Creates final session summary |
| No "ready to restart" message | Tells user safe to restart |
| Git commit + push (sync) | Full file-state review + git push |
| Quick (2-3 min) | Thorough (~5 min) |

## Workflow

### Step 1: Quick lessons check

Scan the session since the last checkpoint (or session start) for:
- Technical discoveries worth remembering
- Rule/skill updates needed
- Mistakes to prevent next time

If lessons found: add to `MEMORY.md` "Lessons Learned" section immediately (no approval needed for memory — it's internal).
If rule/skill updates needed: note them but ASK the user before modifying rules/skills.

### Step 2: Update MEMORY.md

Update the project's MEMORY.md (path is OS-specific — see `docs/SETUP.md`; on Claude Code it lives at `~/.claude/projects/<project-hash>/memory/MEMORY.md`).

- Update "Next Session Priorities" to reflect the current state.
- Update any infrastructure / MCP changes.
- Update project status sections.
- Keep under 200 lines.

### Step 3: Update active plan (if any)

Check `MEMORY.md` for plan references. If an active plan exists:
1. Read the plan file.
2. Mark completed steps (`⬜` → `✅`).
3. Update "Resume at" to the current position.
4. Note any new decisions or blockers.

### Step 4: Git commit + push

Sync all changes to GitHub. The repo is a public template (or your private fork) — commit and push.

```bash
git add -A
git status --short

git commit -m "Checkpoint $(date +%Y-%m-%d): <brief summary of work since last checkpoint>"

# Push (uses whatever auth you have configured: SSH key, credential cache, or PAT-in-URL pattern documented in docs/SETUP.md).
git push origin main
```

If your remote requires PAT-in-URL: use the pattern documented in `docs/SETUP.md` (set token → push → strip token). NEVER leave a PAT in the remote URL.

### Step 5: Append to session summary

If a session summary exists for today (`plans/archive/SESSION-SUMMARY-{user-slug}-YYYY-MM-DD.md`):
- Append a new checkpoint section with what was accomplished since the last save.
- Use suffix letters if multiple summaries exist (a, b, c, d…).

If no summary exists yet, create one with the checkpoint format:

```markdown
# Session Summary — {user-slug} — YYYY-MM-DD[suffix]

## Checkpoint 1: HH:MM / [milestone]
### Done
- [What was completed]

### Status
- [Current state of work]

### Next (continuing this session)
- [What we're doing next]
```

Save to: `plans/archive/SESSION-SUMMARY-{user-slug}-YYYY-MM-DD[suffix].md`.

### Step 6: Confirm and continue

Output a brief status line:
```
Checkpoint saved. Continuing with [next focus area].
```

Then immediately proceed with whatever work comes next — do NOT wait for user input unless there's an unresolved question.

## Rules

1. **Be fast** — this is a mid-session save, not a full wrap-up. 2-3 minutes max.
2. **NEVER skip MEMORY.md** — always update, even if minor.
3. **Append, don't overwrite** — add to the existing session summary, don't replace it.
4. **Don't ask unnecessary questions** — save and move on.
5. **Always update active plan** — if one exists, mark progress.
6. **Keep it brief** — short bullets, not paragraphs.
