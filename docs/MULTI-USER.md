# Multi-User

Most of the system assumes a single user. This doc covers the opt-in multi-user setup — useful if you're operating the system on behalf of multiple people (e.g., as a recruiter, a coach, or for family).

## What "multi-user" means here

- **One database, multiple users**: all data lives in the same NocoDB base, separated by a `user_id` column on every table.
- **Per-user directories**: each user has their own `applications/{slug}/`, `interviews/{slug}/`, `outreach/{slug}/`, `research/{slug}/`, `applications/resumes/data/{slug}/`.
- **Per-user resume corpus**: each user's `master-experience.yaml`, `skills-inventory.yaml`, `standard-answers.yaml`, `user-config.yaml` are independent.
- **Per-user session summaries**: `plans/archive/SESSION-SUMMARY-{slug}-YYYY-MM-DD.md` — prefixed by slug to prevent collisions.
- **One repo per "shared system"**: all users share the same git repo, the same MCPs, and the same Claude Code installation. The active user is set per-session via `JOB_HUNT_USER` in `.env`.

If your users need fully separate setups (no shared DB, separate GitHub repos), that's not multi-user — that's just two people each running their own fork.

## When to use it

Good fit:
- A coach running the system on behalf of 2-5 mentees
- A recruiter who runs structured outreach for 3-10 candidates
- A founder hunting for themselves while also helping a co-founder hunt

Bad fit:
- 50+ users (you'll outgrow self-hosted NocoDB)
- Users with strong privacy requirements (everyone's data is in the same database, accessible to the operator)
- Users who need their own LinkedIn cookies (each user MUST use their own `li_at` — see Privacy below)

## Setup

### One-time

1. Make sure your NocoDB schema has the `users` table populated. Each user is one row with `slug`, `full_name`, `email`, `phone`, `linkedin`, `location`, `target_roles`, `notes`.
2. Make sure each user's slug is reflected in:
   - `applications/resumes/data/{slug}/` (their resume YAMLs)
   - `applications/{slug}/`, `interviews/{slug}/`, `outreach/{slug}/`, `research/{slug}/` (created automatically by `/onboard-user`)
   - `config/user-profile.yaml` — wait, this is per-user. See note below.

### Per-user `config/user-profile.yaml`

`config/user-profile.yaml` is the active user's profile. Multi-user setups can either:

**Option A: switch the file at session start (recommended)**

Keep one `config/user-profile.yaml` per user, named by slug:
```
config/
├── user-profile-jane-demo.yaml
├── user-profile-bob-jones.yaml
└── user-profile.yaml          # symlink or copy of the active user's profile
```

When you switch users, `cp config/user-profile-{slug}.yaml config/user-profile.yaml` (or symlink) and update `.env` `JOB_HUNT_USER`.

**Option B: encode user profiles in the DB and read from there**

The `users` table can hold the user's profile directly. The agent reads from the DB at session start instead of YAML. Tradeoff: harder to version-control, easier to switch.

Most users will prefer Option A.

### Per-session

When operating on behalf of user X:
1. Edit `.env`: set `JOB_HUNT_USER=<X-slug>`.
2. (If using Option A) `cp config/user-profile-<X-slug>.yaml config/user-profile.yaml`.
3. Run `/session-start`. The skill reads `JOB_HUNT_USER`, looks up X's `user_id` from the DB, sets it as the active user for the session.
4. All subsequent skills filter DB queries by `(user_id,eq,<X's id>)` and write to `applications/<X-slug>/`, etc.

### Onboarding a new user

```
/onboard-user
```

The skill walks the new user (or you, on their behalf) through 8 phases:
1. Intake (name, contact, target roles, regions, industries)
2. Job search (15-25 postings to analyse the market)
3. Role profiles (synthesise what the market demands)
4. Resume extraction (parse their resume into YAML)
5. Gap analysis (compare experience vs market demands)
6. Interview (ask targeted questions to fill gaps)
7. Finalise (save config, summarise)

At the end:
- A new `users` row with their slug
- Per-user directories created
- Per-user resume YAMLs populated
- Per-user `user-config.yaml` and `gap-analysis.yaml`

You'll likely also want to create `config/user-profile-{their-slug}.yaml` manually based on their intake answers.

## Critical rules for multi-user

1. **Always include `(user_id,eq,X)` in every DB query** that touches per-user tables. The agent does this automatically when `JOB_HUNT_USER` is set, but it's worth verifying for custom skills.

2. **Always include `user_id: X` in every DB insert.** Same rule.

3. **Never share LinkedIn cookies between users.** Each user MUST use their own `li_at`. Sharing cookies will get accounts flagged. The LinkedIn MCP config in `~/.claude.json` can include the active user's cookie; switch the cookie when you switch users.

4. **Per-user MCP cookies require switching `~/.claude.json`** at user-switch time, OR running separate Claude Code instances per user. The latter is cleaner if your users have very different LinkedIn setups.

5. **Per-user file-organisation rules apply universally.** A user's outreach messages live ONLY in `outreach/{their-slug}/messages/`. Never mix.

6. **Session summaries are slug-prefixed.** `plans/archive/SESSION-SUMMARY-{slug}-YYYY-MM-DD.md` — never just `SESSION-SUMMARY-YYYY-MM-DD.md` in a multi-user setup. Two users working the same date would collide.

## Privacy considerations

- **Same database = same access.** If you operate the system for User A, you can see User A's data. If User A then leaves, all their data is in your DB. Have a clear data-handling agreement.
- **GitHub repo is the source of truth.** Anything in tracked files is in git history. Per-user data is gitignored — but make sure it stays gitignored. Run `git ls-files | grep <slug>` to verify nothing leaked.
- **MEMORY.md is shared.** It's loaded into every session for the operator. Be careful what you write there — never include sensitive details from one user that another user might overhear (if they ever read your sessions).

## Switching users mid-session

Don't. Always end the current session first (`/session-end` writes the summary, commits, pushes), then switch `JOB_HUNT_USER`, then start a new session (`/session-start` reads the new user's context). Mixing two users' actions in one session leads to data corruption — wrong `user_id` on records, wrong slug on file paths.

## When you outgrow this

If you find yourself running 10+ users:
- Move to a hosted database (NocoDB Cloud, Supabase, or Postgres directly).
- Consider per-user GitHub repos (one fork per user) instead of one shared repo.
- Build an admin UI (this template is CLI-driven; a multi-user admin UI is out of scope).
- Look into actual recruiting CRMs (Greenhouse, Lever) — at scale, this template stops being the right tool.
