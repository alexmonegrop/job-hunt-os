# Architecture

How `job-hunt-os` is structured. Read this if you want the mental model before customising or extending.

## Four-layer model

The system has four layers. Each has a different role and a different reload cadence.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 4 — Tools                                                     │
│  Python CLIs that skills shell out to (resume-tailor, job-search,    │
│  init-nocodb, mock-interview). One-off invocations.                  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3 — Operating procedures (operating-procedures/)              │
│  Long-form methodology docs. Read on demand — usually when an agent  │
│  needs the "why" behind a rule, or when a human is studying the      │
│  workflow.                                                            │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2 — Skills (.claude/skills/*/SKILL.md)                        │
│  Invokable workflows. Triggered by /skill-name. The skill orchestrates│
│  the work: reads rules, calls tools, writes files, updates the DB.    │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1 — Rules (.claude/rules/*.md)                                │
│  Auto-loaded into every Claude Code session. Non-negotiable standards.│
└─────────────────────────────────────────────────────────────────────┘
```

When the agent gets a request:
1. **Rules** are already in context (auto-loaded).
2. The agent identifies the right **skill** for the request, reads its SKILL.md.
3. If the skill needs deeper context, it reads an **operating procedure**.
4. The skill calls **tools** (Python CLIs) when it needs to crunch data (score achievements, scrape job boards, generate `.docx`, etc.).

## Configuration model

Three layers of configuration, with strict separation:

### `.env` — secrets and runtime
- API keys, tokens, database connection.
- The active user (`JOB_HUNT_USER`).
- Tool prefixes for MCPs.
- Gitignored.

### `config/*.yaml` — user / role / domain config
- Identity, target roles, regions, industries.
- Fit-score weights, penalties, bonuses.
- Industry vocabulary, region presets.
- Gitignored (only `*.example.yaml` is tracked).

### `applications/resumes/data/{slug}/*.yaml` — per-user content
- Master experience, skills inventory, standard answers.
- User-specific config (resume variants, template mapping).
- Gap analysis.
- Gitignored except `_template/` and `jane-demo/`.

### `MEMORY.md` — persistent agent memory across sessions
- Lives outside the repo (`~/.claude/projects/<hash>/memory/`).
- Loaded into every Claude Code session.
- Contains: next-session priorities, lessons learned, project state, MCP status.
- Updated by `/session-end` and `/session-checkpoint`.

## Data flow

```
[User invokes /skill-name in Claude Code]
                    │
                    ▼
   [Rules in .claude/rules/ auto-loaded into context]
                    │
                    ▼
        [Skill SKILL.md read for workflow]
                    │
                    ▼
   ┌──────────────┬──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
[Reads        [Reads          [Reads         [Calls tool
 config/*.yaml] master-        operating-     (Python CLI)]
                experience.    procedures/    
                yaml]          *.md when      
                               needed]        
                    │
                    ▼
        [Reads / writes via MCP tools]
                    │
                    ▼
   ┌──────────────────┬─────────────────┐
   ▼                  ▼                 ▼
[NocoDB tables]   [Filesystem]      [External services]
 users             applications/     LinkedIn MCP
 target_companies  interviews/       Playwright MCP
 target_contacts   outreach/         WebSearch
 sales_pipeline    research/         OpenRouter (LLM)
 interactions      plans/
 job_postings
 applications
                    │
                    ▼
   [/session-end commits + pushes to GitHub]
```

## Database schema

Default backend: **NocoDB self-hosted**. The schema is backend-agnostic in principle — it can be re-implemented on Postgres directly, Airtable, or another tool, by remapping the MCP prefix.

7 tables (initialised by `tools/setup/init-nocodb.py`):

| Table | Purpose | Key fields |
|-------|---------|------------|
| `users` | Multi-user support | `id`, `slug`, `full_name`, `email`, `linkedin`, `target_roles` |
| `target_companies` | Companies in the hunt | `company_name`, `industry`, `tier`, `why_strong_fit`, `recent_signals`, `workstream` |
| `target_contacts` | People at target companies | `full_name`, `title_role`, `linkedin_profile`, `company_id`, `why_right_person`, `contact_priority` |
| `sales_pipeline` | Outreach pipeline entries | `pipeline_name`, `contact_id`, `company_id`, `pipeline_stage`, `temperature`, `notes` |
| `interactions` | Audit log of every touch | `interaction_type`, `interaction_date`, `target_contact_id`, `pipeline_entry_id`, `subject_topic`, `details` |
| `job_postings` | Discovered jobs | `company_name`, `job_title`, `company_id`, `job_url`, `fit_score`, `status`, `resume_version_used` |
| `applications` | Submitted applications | `application_name`, `job_posting_id`, `company_id`, `application_status`, `networking_contact_id`, `pipeline_entry_id` |

All tables have a `user_id` (Number) for multi-user filtering.

The full schema lives in `infrastructure/init-db/02-jobhunt-schema.sql` (Phase 4).

## Filesystem layout

```
job-hunt-os/
├── README.md, AGENTS.md, LICENSE, CLAUDE.md, .env.example, .gitignore
├── docs/                              # All public docs
├── .claude/
│   ├── rules/                         # 9 auto-loaded rule files
│   └── skills/                        # 13 invokable skills
├── config/                            # *.example.yaml + (gitignored) *.yaml
├── infrastructure/                    # docker-compose, init-db, Caddy (Phase 4)
├── tools/                             # Python CLIs (Phase 4)
├── operating-procedures/              # 9 long-form methodology docs
├── reference-files/templates/         # Generic resume / cover-letter templates
├── applications/
│   ├── jobs/                          # Captured job postings (yaml/md, shared)
│   ├── cover-letters/                 # Standalone cover letter drafts
│   ├── tracking/                      # Application screenshots
│   └── resumes/
│       ├── source/                    # Master .docx (read-only, gitignored)
│       └── data/
│           ├── _template/             # Annotated YAMLs (tracked)
│           ├── jane-demo/             # Demo user (tracked)
│           └── {slug}/                # Real users (gitignored)
├── interviews/{slug}/                 # Per-user interview prep
├── outreach/{slug}/                   # Per-user networking artefacts
├── research/{slug}/                   # Per-user market research
└── plans/
    ├── EXAMPLES/                      # Walkthroughs (Jane Demo)
    └── archive/                       # Session summaries (gitignored)
```

## Rule auto-loading

Claude Code automatically loads every `.md` file under `.claude/rules/` at session start. The agent reads them as high-priority context — they apply to every interaction in the session.

The rule files use `ALWAYS`, `NEVER`, `MUST` for things that are non-negotiable. They cover:
- Database hygiene (`01-database-standards.md`)
- Message quality (`02-message-quality-standards.md`)
- Batch operations (`03-batch-operations-rules.md`)
- Contact selection (`04-contact-selection-priorities.md`)
- File organisation (`05-file-organization-rules.md`)
- Application protocol (`06-application-standards.md`)
- Resume tailoring (`07-resume-tailoring-rules.md`)

If a rule contradicts a skill or procedure, the rule wins.

## Skill invocation

Skills live in `.claude/skills/<name>/SKILL.md` with YAML frontmatter:
```yaml
---
name: "skill-name"
description: "When this skill should be used and what it does."
user_invocable: true   # optional — can the user trigger it directly?
---
```

The agent uses the `description` field to decide when to invoke a skill autonomously, and matches on `name` when the user types `/name`.

## Why rules + skills (and not "everything is a skill")?

- **Rules** apply to all work, all the time. They're invariants — bus, file org, blocked companies — that should never depend on the user invoking a specific workflow.
- **Skills** are the workflows themselves. They package rules + procedures + tools into invokable units.

A common mistake when extending is to add a new rule that's actually a workflow step, or to add a workflow step into a rule. The split: if it's "always true regardless of task", it's a rule. If it's "the steps to do X", it's a skill.

## Why the four-layer split (and not "everything is a skill")?

- **Operating procedures** capture the rationale, examples, and lessons that don't fit in a concise SKILL.md. They keep skills lean while preserving institutional knowledge.
- **Tools** isolate stateful / heavy work (Python, file generation, web scraping) from the agent's reasoning loop. The agent calls them, doesn't simulate them.

This separation is what makes the system maintainable: each layer can change independently, and the agent's context window only loads the layers it needs.

## Cross-workstream integration

The networking and direct-application workstreams share the **Target Companies hub**. Cross-workstream intelligence flows automatically:

- When applying at a company with networking contacts → flag as "Warm Application"; mention contact in cover letter; follow up through contact, not cold HR.
- When researching for outreach at a company with active applications → outreach should NEVER mention the application (per `OUTREACH-OPERATING-PROCEDURE-v4.md`).

This is encoded in the rules (`06-application-standards.md` Cross-Workstream Check) and skills (`apply`, `cold-outreach`, `application-tracker`).

## Continuity across sessions

The repo + database are the source of truth — not the agent's context window.

End of session:
- `/session-end` updates MEMORY.md, `plans/OVERALL-PLAN.md`, writes session summary, commits + pushes.

Start of next session:
- `/session-start` reads all of the above + tests MCP connectivity, presents action menu.

This means a fresh agent in a new session can pick up where the last session left off without re-orienting.
