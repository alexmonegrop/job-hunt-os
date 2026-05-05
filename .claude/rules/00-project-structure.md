# Project Structure — job-hunt-os

This is a **standalone, single-purpose repo**: an agentic job-hunt operating system. All paths below are relative to the repo root.

## Top-level layout

```
job-hunt-os/
├── README.md, LICENSE, AGENTS.md, CLAUDE.md, .gitignore, .env.example
├── docs/                            # SETUP, CUSTOMIZE, ARCHITECTURE, EXAMPLES, EXTEND, CONTRIBUTING, MULTI-USER, MIGRATION-FROM-PRIVATE-FORK, PLAN
├── .claude/
│   ├── rules/                       # 00-07 — auto-loaded standards (this directory)
│   └── skills/                      # invokable workflows
├── config/                          # user-profile, fit-score, industries, regions (.example.yaml + .yaml)
├── infrastructure/                  # docker-compose, init-db, Caddyfile (NocoDB self-hosted stack)
├── tools/
│   ├── setup/                       # init-nocodb.py, first-run.py
│   ├── resume-tailor/               # YAML-driven .docx resume generator + quality gate
│   ├── job-search/                  # JobSpy + custom search wrappers
│   ├── interview/                   # mock-interview, recruiter-review, role contexts
│   ├── bootstrap/                   # multi-user onboarding flow
│   └── employer-extension-example/  # documented example of extending the system per-employer
├── operating-procedures/            # methodology docs (workflows, examples, lessons)
├── reference-files/templates/       # generic resume/cover-letter/master-experience templates
├── applications/
│   ├── jobs/                        # captured job postings (yaml/md, shared)
│   ├── cover-letters/               # standalone cover letters (gitignored at user level)
│   ├── tracking/                    # screenshots from application submissions (gitignored)
│   └── resumes/
│       ├── source/                  # master .docx files (read-only, gitignored)
│       └── data/
│           ├── _template/           # annotated template YAMLs
│           └── {user-slug}/         # per-user master-experience.yaml etc. (gitignored)
├── interviews/{user-slug}/          # per-user interview prep by company (gitignored)
├── outreach/{user-slug}/            # per-user networking artefacts (gitignored)
│   ├── messages/                    # ONE FILE PER PERSON
│   ├── prep/                        # networking meeting prep
│   ├── calls/                       # video + transcripts
│   ├── analysis/                    # post-meeting analysis
│   └── sessions/                    # session notes
├── research/{user-slug}/            # per-user market/company research (gitignored)
└── plans/
    ├── EXAMPLES/                    # walkthroughs (Jane Demo)
    └── archive/                     # session summaries (gitignored)
```

## Key conventions

- **Per-user data is gitignored at the user level** — `applications/{slug}/`, `interviews/{slug}/`, `outreach/{slug}/`, `research/{slug}/`, `applications/resumes/data/{slug}/` (except `_template/` and `jane-demo/`). The active user is set by `JOB_HUNT_USER` in `.env`.
- **Never save working files to the repo root.** All artefacts go into the appropriate sub-tree.
- **Never write secrets to any tracked file.** `.env` is the only place credentials live, and it is gitignored.
- **Configurable values live in `config/*.yaml`**, not in rules or skills.

## Backend access

This repo is backend-agnostic in principle: the rules describe NocoDB by default (the original reference implementation), but the schema can be re-implemented on Postgres, Airtable, or other tools. The skill code reads MCP tool prefixes from environment variables — see `01-database-standards.md`.

## GitHub access

For pushing this repo to GitHub:
- Use whichever GitHub MCP your environment has configured, or `git push` over HTTPS with a personal access token.
- The active user owns their fork. This template repo lives at `<your-org>/job-hunt-os`.
- Never use `gh` CLI if your environment authenticates a different account — use the configured MCP or git directly.

## File organisation

See `05-file-organization-rules.md` for naming conventions and directory placement details.
