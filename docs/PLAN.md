# Rollout Plan — `job-hunt-os`

**Status as of last update**: Phase 1 complete. This file is the canonical handoff doc — read it first when picking up this project in a new session.

---

## Origin & objective

This repository is a sanitised, generalised public template extracted from a real, private agentic job-hunt repo (`alexmonegrop/job-hunt`, private). The private repo ran a full 12-month pipeline for one applicant (Calgary / GCC focus, Energy + AI/DT + Industrials industries) and produced ~110 applications, 500+ contacts, multiple offers. The objective of this template is to expose the **methodology, skills, rules, tooling, and operating procedures** so anyone can clone, configure for their region/industries/roles, and run a similar pipeline — with their own infrastructure or simplified local-only deployment.

## Strategy summary

- **New public repo**, not a sanitised fork. The private repo's history contains 60+ session summaries with names, message drafts, and contact data — `git filter-repo` is fragile and risky. Clean tree, clean history.
- **Configurable, not hardcoded.** Region, industries, target roles, fit-score weights, NocoDB base ID — everything that was hardcoded for one applicant becomes a config file or env var.
- **Local-first backend.** Default deployment recommendation is NocoDB self-hosted via Docker Compose on the user's laptop. No VPS or Tailscale required for solo use. (Heavy users can scale to a remote stack later.)
- **Multi-user is optional.** The original system has multi-user support (Alex + Jessie). The template keeps it but the docs default to a single-user setup; multi-user is an opt-in section.
- **Strip all PII (Option A).** No anonymised case studies. One fictional demo user ("Jane Demo") for screenshots and walkthroughs. The Sia-Partners-style employer-extension example is kept structurally but with all names/employers replaced.
- **License**: MIT.

## Source repo (read-only reference)

Path: `C:\Users\alexm\claude-work-folder\job-hunt`

Use this as a reference for what to port. Do **not** modify it from this template's session — that's a separate piece of work (see "Deferred — private-repo hygiene audit" below).

## Phases

### ✅ Phase 1 — Scaffolding & repo creation (DONE)

Output:
- Local folder at `C:\Users\alexm\claude-work-folder\job-hunt-os` with full directory skeleton.
- Public GitHub repo `alexmonegrop/job-hunt-os` created, MIT licensed.
- Skeleton files committed: `README.md`, `LICENSE`, `.gitignore`, `.env.example`, `CLAUDE.md`, `docs/PLAN.md` (this file), and stub docs.
- `.gitkeep` placeholders in empty directories.

### ⬜ Phase 2 — Port rules and skills (sanitise as you go)

**Source paths (private repo):**
- `.claude/rules/00-README.md`, `00-project-structure.md`, `01-nocodb-standards.md`, `02-message-quality-standards.md`, `03-batch-operations-rules.md`, `04-contact-selection-priorities.md`, `05-file-organization-rules.md`, `06-application-standards.md`, `07-resume-tailoring-rules.md`
- `.claude/skills/` — all skills

**Target paths**: same in this repo.

**Sanitisation checklist for each file:**

- [ ] Replace hardcoded `base_id: pgg5yb2zorospul` with `${NOCODB_BASE_ID}` env-var pattern; document the lookup in CLAUDE.md.
- [ ] Replace hardcoded `xc-token: FOfjXH...` with `${NOCODB_API_TOKEN}`.
- [ ] Replace Tailscale URL `100.102.50.46:8080` with `${NOCODB_URL}` (default `http://localhost:8080`).
- [ ] Replace hardcoded link field IDs with placeholders + a note pointing to `tools/setup/init-nocodb.py` to discover them post-schema-init.
- [ ] Strip "Alex's background" examples in rule 01 (3-element formula) and rule 04 — replace with illustrative `<your relevant role>` placeholders.
- [ ] Rule 02 — strip "Calgary / GCC / Aramco / Saudi" examples, keep generic insight formulas. Industry vocabulary moves to `config/industries.yaml`.
- [ ] Rule 06 — strip Calgary fit-score adjustments. Replace with reference to `config/fit-score.yaml`. Strip BLOCKED COMPANIES list (per-user concern, not template).
- [ ] Rule 07 — generic, mostly OK after stripping the "Alex's resume variants" specifics.
- [ ] Skills — sanitise any "Alex" / "Jessie" / specific company name. Convert to `<active user>` references.
- [ ] Any path like `applications/{user_slug}/` already templated, OK; verify per skill.
- [ ] Rename rule 01 from `nocodb-standards` to `database-standards.md` to allow alternative backends later.

**Validation gate:** grep the new files for: `Alex`, `Jessie`, `Monegro`, `Calgary`, `Dubai`, `Riyadh`, `Aramco`, `ADNOC`, `pgg5yb2zorospul`, `FOfjXH`, `100.102.50.46`. Should return zero hits in `.claude/`.

### ⬜ Phase 3 — Generalise config

Create:
- [ ] `config/user-profile.example.yaml` — `name`, `slug`, `location`, `target_roles[]`, `target_regions[]`, `target_industries[]`, `excluded_companies[]`, `language[]`. Example values for Jane Demo. Skill code reads `config/user-profile.yaml` (gitignored) which user copies from the example.
- [ ] `config/fit-score.example.yaml` — weighted scoring matrix with penalties + bonuses. Document each adjustment.
- [ ] `config/industries.example.yaml` — illustrative industry vocabulary; user customises.
- [ ] `config/regions.example.yaml` — illustrative region/market presets (optional).

Update rules and skills to read from `config/*.yaml` instead of inline hardcoded values.

**Validation gate**: a fresh user can clone, copy `config/*.example.yaml` → `config/*.yaml`, customise values, and run a skill that uses fit scoring without editing rule files.

### ⬜ Phase 4 — Port tools and infrastructure

**Source paths (private repo):**
- `tools/resume-tailor/` — Python scripts + master YAML structure.
- `tools/job-search/` — JobSpy + custom search.
- `tools/interview/` — `mock-interview.py`, `recruiter-review.py`, `run-mock-curl.sh`, contexts.
- `tools/bootstrap/` — multi-user onboarding flow.
- `tools/sia/` — port as `tools/employer-extension-example/` with all names anonymised. This becomes a documented worked example of how to extend the system for a new employer/use case.
- `infrastructure/docker-compose.yml`, `infrastructure/Caddyfile`, `infrastructure/init-db/01-create-databases.sql`, `infrastructure/init-db/02-jobhunt-schema.sql`, `infrastructure/.env.example`.

**Target paths**: same in this repo, with sanitisation.

**Sanitisation checklist:**

- [ ] `tools/resume-tailor/` — replace `applications/resumes/data/{slug}/master-experience.yaml` references with template path; ship `applications/resumes/data/_template/master-experience.template.yaml` (annotated, no real bullets).
- [ ] `tools/interview/contexts/` — strip role-specific contexts tied to real companies (`inter-pipeline.txt`, `sia-partners.txt`, `aeso.txt`). Ship 1-2 generic example contexts (e.g., `program-manager-energy.txt`, `product-manager-saas.txt`).
- [ ] `tools/bootstrap/` — strip `BOOTSTRAP.md` references to specific past users; replace with generic onboarding instructions.
- [ ] `tools/sia/sia_content.py` — refactor into `tools/employer-extension-example/employer_content.example.py` with placeholder names ("ACME Consulting", "Generic Energy Co"). Document the pattern in `docs/EXTEND.md`.
- [ ] `infrastructure/docker-compose.yml` — verify no hardcoded credentials; rely on `.env`.
- [ ] `infrastructure/init-db/02-jobhunt-schema.sql` — should be safe (schema only); review for any seed data that includes real names.
- [ ] Drop `infrastructure/n8n-backup/` entirely (Lexacon-related n8n workflows leaked from another project; not job hunt).
- [ ] Drop `infrastructure/migration-data/*.json` (Airtable migration dumps with real records).
- [ ] Drop `infrastructure/migrate-airtable.py` (one-time migration tool, not template-relevant).
- [ ] Drop `tools/airtable-setup-applications.md`, `tools/migrate-file-structure.py` (one-time historical scripts).
- [ ] Add `tools/setup/init-nocodb.py` — fresh-install script: takes `NOCODB_API_TOKEN` + `NOCODB_URL`, creates the 8 tables from the schema SQL, returns the new `base_id` and link-field IDs to write into `.env`.
- [ ] Add `tools/setup/first-run.py` — checks Docker, Tailscale (optional), Chrome closed, MCPs configured; offers to install missing pieces.

**Validation gate**: a user with a fresh NocoDB instance can run `python tools/setup/init-nocodb.py` and end up with a working schema; can run `tools/resume-tailor/tailor-resume.py` against the template YAML without errors.

### ⬜ Phase 5 — Port operating procedures + reference templates

**Source paths (private repo):**
- `operating-procedures/00-README-PROCEDURES.md`, `OUTREACH-OPERATING-PROCEDURE-v4.md`, `MEETING-PREP-PROCEDURE-v4.md`, `RESUME-TAILORING-PROCEDURE-v1.md`, `DIRECT-APPLICATION-PROCEDURE-v1.md`, `contact-population-plan-v3.md`, `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md`, `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`, `APPLICATION-SPEED-LESSONS-v1.md`, `VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md`.
- `reference-files/templates/` — generic resume/cover-letter templates if any exist.

**Sanitisation checklist:**
- [ ] All examples that reference Alex / Jessie / Calgary / GCC / specific companies → replace with Jane Demo or generic `<your industry>`.
- [ ] OUTREACH and MEETING-PREP procedures are the highest-value methodology docs — preserve their structure precisely while swapping examples.
- [ ] `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md` — keep the formula structure; rewrite the 8 worked examples with fictional companies/regions.
- [ ] APPLICATION-SPEED-LESSONS-v1.md — keep the principles; strip the "Alex applied to N companies in M days" specifics.

**Reference templates to ship:**
- `reference-files/templates/resume-template.docx` — generic 2-page PM/Product resume skeleton.
- `reference-files/templates/cover-letter-template.md` — generic structured cover letter.
- `reference-files/templates/master-experience.template.yaml` — annotated master YAML schema (already covered in Phase 4).

### ⬜ Phase 6 — Demo user + worked examples

Create a fictional demo user "Jane Demo":
- `applications/resumes/data/jane-demo/master-experience.yaml` — populated with plausible-but-fake achievements.
- `applications/resumes/data/jane-demo/skills-inventory.yaml`
- `applications/resumes/data/jane-demo/standard-answers.yaml`
- `applications/resumes/data/jane-demo/user-config.yaml`
- `config/user-profile.yaml` (Jane's profile, used as default if `JOB_HUNT_USER=jane-demo`)
- `plans/EXAMPLES/jane-demo-walkthrough.md` — narrative walkthrough of a session: cold outreach → response → meeting prep → application → interview prep. References screenshots if we add them.

**Don't** populate with real-feeling data that could be mistaken for a real applicant — keep it obviously fictional.

### ⬜ Phase 7 — Documentation + polish + Template flag

Write/finalise:
- [ ] `docs/SETUP.md` — full installation walkthrough, including Docker, MCP install, OpenRouter signup, NocoDB API token creation, schema init.
- [ ] `docs/CUSTOMIZE.md` — how to swap in your own resume YAML, set your region/industries, adjust fit-score weights, add custom rules.
- [ ] `docs/ARCHITECTURE.md` — rules vs skills vs operating procedures vs tools; the four-layer config model; data flow diagram (NocoDB ↔ skills ↔ tools ↔ filesystem).
- [ ] `docs/EXAMPLES.md` — Jane Demo walkthrough, screenshots if produced.
- [ ] `docs/EXTEND.md` — new — how to add a new skill, a new rule, a new tool, a new employer-extension. References the `tools/employer-extension-example/`.
- [ ] `docs/CONTRIBUTING.md` — issue/PR conventions, dev environment setup, testing.
- [ ] `docs/MULTI-USER.md` — opt-in multi-user setup (NocoDB `users` table, `user_id` columns, per-user data dirs).
- [ ] `docs/MIGRATION-FROM-PRIVATE-FORK.md` — for anyone (e.g., the original author) who maintains a private fork: how to pull in updates from this template without leaking PII.
- [ ] Mark the GitHub repo as a Template Repository.
- [ ] Add repo description, topics (`claude-code`, `agent`, `job-search`, `nocodb`, `automation`), and pin to profile if appropriate.
- [ ] README screenshots (optional but recommended).

**Validation gate**: a fresh, never-saw-this-before user can clone the repo, follow `SETUP.md` end-to-end, and run their first `/cold-outreach` skill against their NocoDB without asking the maintainer for help.

## Deferred — separate workstream

### Private-repo hygiene audit (`alexmonegrop/job-hunt`)

After Phase 3 of this template is done (i.e., once we have the canonical generalised structure nailed down), do a sweep of the private repo to:

- Move any tracked secrets out of tracked paths (`tools/bootstrap/`, anywhere `.env` may have been committed historically).
- Audit git history with [`gitleaks`](https://github.com/zricethezav/gitleaks) or similar for leaked credentials.
- Normalise paths and patterns to match what the template expects, so future template→private syncs are clean.
- Verify `.gitignore` covers everything we now know to gitignore.

This is **separate** from the template work and should be its own session.

## Operating notes for whoever continues this

- **Always start a continuation session by re-reading `docs/PLAN.md`.** Update the phase checkboxes as you finish work. Move completed sub-tasks from "checklist" lines to checked-off bullets in the phase header.
- **The private repo at `C:\Users\alexm\claude-work-folder\job-hunt` is read-only reference** — never modify it from a `job-hunt-os` session.
- **Validation gates are not optional.** Each phase has a gate; don't move on until you've grep-verified PII is gone (Phase 2), config-verified a fresh user can run a skill (Phase 3), or run-verified the tools work (Phase 4).
- **Single source of truth = this file.** If you make a strategic decision in conversation, write it here so the next session inherits it.
- **Default branch is `main`.** Standard PR flow: feature branch → PR → merge to main.
- **Never push secrets.** `.env` is gitignored. If you generate test data, put it under `applications/jane-demo/` (which is gitignored at the per-user level).

## Quick reference — directory structure

```
job-hunt-os/
├── README.md, LICENSE, CLAUDE.md, .gitignore, .env.example
├── docs/                            # PLAN.md (this), SETUP, CUSTOMIZE, ARCHITECTURE, EXAMPLES, EXTEND, CONTRIBUTING, MULTI-USER
├── .claude/
│   ├── rules/                       # 00-07 — auto-loaded standards (Phase 2)
│   └── skills/                      # invokable workflows (Phase 2)
├── config/                          # user-profile, fit-score, industries, regions (Phase 3)
├── infrastructure/                  # docker-compose, init-db, Caddyfile (Phase 4)
├── tools/
│   ├── setup/                       # init-nocodb, first-run (Phase 4)
│   ├── resume-tailor/               # (Phase 4)
│   ├── job-search/                  # (Phase 4)
│   ├── interview/                   # (Phase 4)
│   ├── bootstrap/                   # multi-user onboard (Phase 4)
│   └── employer-extension-example/  # the Sia-pattern, sanitised (Phase 4)
├── operating-procedures/            # methodology docs (Phase 5)
├── reference-files/templates/       # generic resume/cover-letter (Phase 5)
├── applications/                    # gitignored at per-user level
│   ├── jobs/, cover-letters/, tracking/
│   └── resumes/source/ + resumes/data/_template/
├── interviews/, outreach/, research/   # gitignored at per-user level
└── plans/
    ├── EXAMPLES/                    # Jane Demo walkthrough (Phase 6)
    └── archive/                     # gitignored
```
