# Rollout Plan — `job-hunt-os`

**Status as of last update**: **All 7 phases complete. v1 template shipped (M12 closes out Phase 4).**

This file is the canonical handoff doc — read it first when picking up this project in a new session.

---

## v1 release: shipped

All seven phases are complete. The v1 template is operational end-to-end:

- Rules + skills + operating procedures (Phases 2, 3, 5)
- Configurable for any region/industry/role (Phase 3)
- Python tooling: resume tailor, quality gate, PDF, job search, interview/transcription, NocoDB bootstrap (Phase 4)
- Docker infrastructure: Postgres + NocoDB with seed schema (Phase 4)
- Jane Demo dataset + walkthrough (Phase 6)
- Full documentation including AGENTS.md (Phase 7)

### M12 close-out (most recent)

- **Smoke test against jane-demo passed end-to-end**: scoring-only → full `.docx` → quality gate (8 PASS, 1 WARN for the deferred recruiter-review skip, 0 FAIL) → PDF generation via docx2pdf.
- **Two real bugs fixed in flight**:
  - `quality-gate.py` `check_bullet_count` now actually honours `min_bullets` / `hard_fail_min_bullets` from the job YAML. Its error message previously promised this but the constants were hardcoded.
  - `init-nocodb.py` now walks workspace-scoped endpoints (NocoDB 2026.04 returns 403 on the legacy flat `/api/v2/meta/bases` for PATs) **and** auto-creates the JobHunt base + postgres source if it doesn't exist yet — eliminating the "add the data source via the UI" manual step.
- **Two infrastructure gotchas documented + solved**:
  - `docker-compose.yml` now sets `NC_ALLOW_LOCAL_EXTERNAL_DBS=true` so NocoDB doesn't reject the Docker-internal `postgres` hostname with "Forbidden host name or IP address".
  - `_template.yaml` surfaces the `min_bullets` and `hard_fail_min_bullets` overrides.

### M13 close-out (2026-05-06, follow-up to v1)

- **`tools/resume-tailor/recruiter-review.py` shipped.** Independent LLM recruiter review via OpenRouter — emits the JSON contract that `quality-gate.py` already consumes (`verdict: PASS|FAIL|SKIP`, `issues[].severity: blocking|advisory`). Default model `anthropic/claude-sonnet-4-6`, overridable via `RECRUITER_REVIEW_MODEL` env. SKIPs cleanly (no FAIL) when `OPENROUTER_API_KEY` is unset or the API is unreachable.
- **Smoke test confirmed WARN → PASS**: re-running the M12 jane-demo gate without the key gives `8 PASS, 1 WARN (recruiter_review SKIP)`; with the key set, `9 PASS, 0 WARN, 0 FAIL`. The previously-deferred WARN is gone.

### M14 close-out (2026-05-07, setup ergonomics)

- **`init-nocodb.py --auto-bootstrap` shipped.** Folds admin signup + PAT minting into the existing init script via NocoDB's `/api/v1/auth/user/signup` + `/api/v1/tokens` endpoints. Idempotent: if an admin already exists, signup 401s and the script falls back to signin with the same creds. Writes `NOCODB_ADMIN_EMAIL`, `NOCODB_ADMIN_PASSWORD`, and `NOCODB_API_TOKEN` back to `.env` so subsequent runs skip the bootstrap step.
- **Setup ergonomics**: cuts new-user setup from ~3 min of UI clicks (sign up, navigate Account → Tokens, generate, paste) to a single `python tools/setup/init-nocodb.py --auto-bootstrap` command (~5 sec).
- **Validated end-to-end against the live stack**: PAT-set path is a no-op (regression check); signin path mints a fresh 40-char PAT that returns HTTP 200 against `/api/v2/meta/bases/.../tables`.
- `docs/SETUP.md` Step 4 now presents Option A (auto-bootstrap, recommended) vs Option B (manual UI) with both paths explained.

### Repo polish (2026-05-07)

- GitHub repo marked as **Template Repository**; description set; topics added (`job-hunt`, `claude-code`, `nocodb`, `resume-tailoring`, `automation`, `agentic-workflows`, `template-repository`).
- `jane-demo` user record seeded into the live local NocoDB (id=2), so demo skills can resolve `JOB_HUNT_USER=jane-demo` against the database.
- `~/.claude.json` for `job-hunt-os` project: `context7` + `playwright` MCPs added alongside `nocodb`.
- `.claude/settings.local.json` (gitignored) populated with scoped Bash permission rules for routine GitHub/Docker/git/python ops on this repo, so per-action confirmation isn't needed for already-trusted workflows.

### Still deferred (not blocking v1)

- `tools/resume-tailor/create-template.py` — variant scaffolding utility. Less critical than the core flow.
- The full Sia / employer-extension Python port. The README pattern doc in M5 documents the pattern; users build their own employer extensions with that as guidance. Per session direction.
- n8n MCP integration. Per session direction (dropped entirely).

### Optional follow-up (not in v1 scope)

- `/session-start` MCP integration end-to-end test against a live local stack. **DONE 2026-05-07**: live NocoDB MCP returns all 7 tables in this session's `/session-start`; recovered after a Docker restart timing race.
- Mark the GitHub repo as a Template Repository, add description/topics, pin to profile. **DONE 2026-05-07** (template + topics; pin-to-profile is UI-only on the user's profile page).

---

## Origin & objective

This repository is a sanitised, generalised public template extracted from a real, private agentic job-hunt repo. The private repo ran a full 12-month pipeline for one applicant and produced ~110 applications, 500+ contacts, multiple offers received, one role accepted. The objective of this template is to expose the **methodology, skills, rules, tooling structure, and operating procedures** so anyone can clone, configure for their region / industries / roles, and run a similar pipeline — with their own infrastructure or simplified local-only deployment.

## Strategy summary

- **New public repo**, not a sanitised fork. Clean tree, clean history (the private repo's history contains 60+ session summaries with names and PII — `git filter-repo` would have been fragile).
- **Configurable, not hardcoded.** Region, industries, target roles, fit-score weights, NocoDB base ID — everything that was hardcoded for one applicant becomes a config file or env var.
- **Local-first backend.** Default deployment recommendation is NocoDB self-hosted via Docker Compose. No VPS or Tailscale required for solo use.
- **Multi-user is optional.** The original system has multi-user support. The template keeps it but the docs default to a single-user setup; multi-user is an opt-in section (see `docs/MULTI-USER.md`).
- **Strip all PII.** No anonymised case studies. One fictional demo user ("Jane Demo") for screenshots and walkthroughs.
- **License**: MIT.

## Phases

### Phase 1 — Scaffolding & repo creation — DONE

Output:
- Local folder at `C:\Users\alexm\claude-work-folder\job-hunt-os` with full directory skeleton.
- Public GitHub repo `alexmonegrop/job-hunt-os` created, MIT licensed.
- Skeleton files committed: `README.md`, `LICENSE`, `.gitignore`, `.env.example`, `CLAUDE.md`, `docs/PLAN.md`, and stub docs.
- `.gitkeep` placeholders in empty directories.

### Phase 2 — Port rules and skills — DONE

Output:
- 9 rule files in `.claude/rules/` (renamed `01-nocodb-standards.md` → `01-database-standards.md`).
- 13 skill files in `.claude/skills/<skill>/SKILL.md`.
- All hardcoded NocoDB IDs / tokens / URLs replaced with env-var references (`${NOCODB_BASE_ID}`, `${NOCODB_URL}`, `${NOCODB_API_TOKEN}`, `${NOCODB_MCP_PREFIX}`).
- All user-specific names / regions / companies replaced with placeholders pointing at `config/*.yaml`.
- All BlackHills / Tailscale references removed.
- `.env.example` updated with `NOCODB_MCP_PREFIX` and link-field IDs.

Validation gate (forbidden-token grep on `.claude/`): **PASSED**, zero hits.

### Phase 3 — Generalise config — DONE

Output:
- `config/user-profile.example.yaml` — identity, target roles / regions / industries, excluded companies, languages, credibility anchors, value props, credentials, work auth, resume variants.
- `config/fit-score.example.yaml` — `raw_criteria[]`, `penalties[]`, `bonuses[]`, `thresholds`.
- `config/industries.example.yaml` — canonical industry vocabulary + `insight_seeds` per industry.
- `config/regions.example.yaml` — region presets (cities, languages, flagship buyers, job boards, dynamics).
- `.gitignore` updated: `config/*.yaml` ignored; `*.example.yaml` tracked.

Validation gate: rules and skills reference `config/*.yaml` paths instead of hardcoded values; fresh user can `cp config/*.example.yaml → config/*.yaml` and run skills with sane defaults.

### Phase 4 — Port tools and infrastructure — DONE

**Status**: All 6 milestones (M7-M12) shipped. See "M12 close-out" at the top of this file for what the smoke test surfaced and fixed.

#### M7 — Infrastructure + setup tools — DONE (commit `da89ad9`)
Ported (sanitised):
- `infrastructure/docker-compose.yml` — postgres + nocodb only by default; caddy as `--profile caddy` opt-in. Drop website + n8n services.
- `infrastructure/Caddyfile` — env-var-driven NOCODB_DOMAIN (was hardcoded).
- `infrastructure/init-db/01-create-databases.sql` — only nocodb metadata DB now.
- `infrastructure/init-db/02-jobhunt-schema.sql` — 7-table schema (was 6). Adds `users` table + `user_id` FK on all data tables. Drops legacy `airtable_id` columns. Drops hardcoded CHECK constraints on industry / job_board / expansion_status (config-driven now).
- `infrastructure/.env.example` — generic.
- `tools/setup/init-nocodb.py` — NEW: discovers base id + 3 link-field IDs, writes to `.env`.
- `tools/setup/first-run.py` — NEW: read-only health check.

Dropped:
- `infrastructure/n8n-backup/` (40 JSON files from a different project)
- `infrastructure/migration-data/` (real Airtable PII)
- `infrastructure/migrate-airtable.py` (one-time historical)

Validation: live test with `docker compose up -d` produced 7 tables, seed user, NocoDB reachable HTTP 200. Stack torn down `down -v` clean.

#### M8 — Resume tailor tool — DONE (commit `b15eb7f`)
Ported (sanitised):
- `tools/resume-tailor/tailor-resume.py` — `--user` flag (was `--person`), JOB_HUNT_USER env fallback, removed hardcoded fallback skills, format-config per-user override.
- `tools/resume-tailor/quality-gate.py` — `--user` flag, recruiter-review.py gracefully WARN-skips.
- `tools/resume-tailor/generate-pdf.py` — docx2pdf primary, LibreOffice fallback.
- `tools/resume-tailor/generate-cover-letter-pdf.py` — drop hardcoded ALEX_DEFAULTS, reads from user-config.yaml.
- `tools/resume-tailor/format-config.yaml` — per-user-overridable.
- `tools/resume-tailor/jobs/_template.yaml` — annotated job-posting YAML.

Restructured Jane Demo data to canonical shape (contact + summary_variants for 7 variant keys + experience with title_variants / achievements with full metadata + education + certifications). 14 achievements across 5 fictional companies.

Added `applications/resumes/data/role-type-schemas.yaml` global fallback (empty achievement_ids lists; users populate from their gap-analysis).

Skipped (deferred):
- `recruiter-review.py` (OpenRouter LLM dependency)
- `create-template.py` (variant scaffolding utility)
- `build-jessi-resume.py` (personal-name-leaky, dropped)

Validation: `tailor-resume.py --scoring-only --user jane-demo` produces correct JSON with sensible scores (10/10 on top bullets matching JD requirements).

#### M9 — Job search tool — DONE (commit `ca1452b`)
Ported (sanitised):
- `tools/job-search/search-jobs.py` — full rewrite. Now reads target_roles[], target_regions[], target_industries[] from config/*.yaml at runtime instead of hardcoded GCC keyword maps. DEFAULT_CITY_COUNTRY_MAP spans 40+ global cities.
- `tools/job-search/sample-job-posting.yaml` — fictional Solaris Demoland example (was ADNOC / Abu Dhabi / oil-gas).

Dropped:
- 15+ `search*-results.json` and `fresh*-results.json` files (real PII)
- `search*-stderr.txt` log files

Validation: Python syntax OK; module imports cleanly.

#### M10 — Interview + transcription tools — DONE (commit `e6d0b9a`)
Ported (sanitised):
- `tools/interview/mock-interview.py` — replaced hardcoded AESO/Suha/Alex Monegro context with a generic recruiter persona. Candidate context loaded from per-user `recruiter-context.yaml` + `user-config.yaml` via `--user`. Default model: `google/gemini-3-flash-preview`. Removed model-pricing-rates dict.
- `tools/interview/contexts/program-manager-energy.txt` — NEW generic role context.
- `tools/interview/contexts/product-manager-saas.txt` — NEW.
- `tools/interview/contexts/ai-product-manager.txt` — NEW.
- `tools/transcribe_meeting.py` — CLI-driven (was hardcoded path). Platform-aware ffmpeg lookup.
- `tools/colab-whisper.py` — comments cleaned up.

Dropped:
- `tools/interview/contexts/inter-pipeline.txt` (real company)
- `tools/interview/contexts/sia-partners.txt` (real employer)
- `tools/interview/contexts/aeso.txt` (real ISO + interviewer)
- `tools/interview/run-mock-curl.sh` (referenced blackhillslabs.com + leaked tools/.env)
- `tools/whisper-setup.md` (covered by VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md)
- `tools/transform_skills.py`, `tools/airtable-setup-applications.md`, `tools/migrate-file-structure.py` (historical migrations)
- `tools/.env` (real tokens)

Validation: Python syntax OK on all 3 scripts.

#### M11 — Bootstrap docs (sanitised) — DONE (commit `8767916`)
Ported (sanitised):
- `tools/bootstrap/BOOTSTRAP.md` — 10-phase new-machine setup walkthrough. Reframed from "share Alex's shared infrastructure" to "set up your own job-hunt system". Detailed troubleshooting.
- `tools/bootstrap/bootstrap-prompt.md` — paste-ready Claude Code prompt.

Sanitised — removed 5 leaked secrets:
- NocoDB token `FOfjXH...`
- GitHub PAT `ghp_oFZAVl...`
- Hunter.io key `fa561f18...`
- Lusha key `9133b876...`
- n8n JWT `eyJhbGc...`

All replaced with placeholders. Real domains (`db.blackhillslabs.com`, `n8n.blackhillslabs.com`) replaced with NOCODB_URL env-var pattern. Tailscale IP `100.102.50.46` dropped. "Alex Monegro" / "alexmonegrop" → "the system owner" / "<your-org>". BlackHills MCP names → generic names.

Per session direction: dropped n8n MCP entry entirely; dropped Sia tool port entirely (README pattern doc in M5 stays as guidance only).

Validation: forbidden-token grep on tools/bootstrap/: zero hits across 40+ patterns.

#### M12 — Integration smoke test + close-out — DONE

Validated end-to-end against jane-demo with the live Postgres + NocoDB stack. Smoke test summary and the two bugs / two gotchas surfaced in flight are at the top of this file under "M12 close-out". Stack torn down clean (`docker compose down -v` + `rm infrastructure/.env`).

### Phase 5 — Port operating procedures + reference templates — DONE

Output:
- 9 operating procedures in `operating-procedures/`:
  - `00-README-PROCEDURES.md` — index, rules-vs-procedures contrast.
  - `OUTREACH-OPERATING-PROCEDURE-v4.md` — deep research dossier, practitioner insight framing, peer ask, application-adjacent networking.
  - `MEETING-PREP-PROCEDURE-v4.md` — meeting environment contingencies, 6-insight 2x prep model, intelligence extraction, vulnerability strategy.
  - `RESUME-TAILORING-PROCEDURE-v1.md` — scoring algorithm, quality gate, cover-letter Hook → Alignment → Value → CTA.
  - `DIRECT-APPLICATION-PROCEDURE-v1.md` — end-to-end application workflow with cross-workstream networking integration.
  - `contact-population-plan-v3.md` — 7-step workflow per company, 3-element formula, lessons learned (preserved as generic guidance).
  - `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md` — 15-minute insight research process, counter-intuitive truth formulas, quality scorecard.
  - `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md` — 8 worked examples (70-90 words), all with fictional companies (Nimbus AI, Helios Advisory, Sterling Pay, etc.).
  - `APPLICATION-SPEED-LESSONS-v1.md` — 5 bottlenecks + fixes from high-volume sessions, including the standardised LinkedIn Easy Apply shadow-DOM template.
  - `VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md` — Whisper / FFmpeg setup, prep-vs-reality framework, follow-up creation.
- Drop `OUTREACH-OPERATING-PROCEDURE-v3.md` (superseded).
- Reference templates:
  - `applications/resumes/data/_template/master-experience.template.yaml` — annotated YAML schema with tagging vocabulary.
  - `reference-files/templates/cover-letter-template.md` — Hook → Alignment → Value → CTA, what-to-avoid checklist.
  - The `.docx` resume template is deferred (binary, hard to author cleanly here — documented as a user action in `CUSTOMIZE.md`).

Validation gate (forbidden-token grep on `operating-procedures/`, `reference-files/`, `_template/`): **PASSED**, zero hits.

### Phase 6 — Demo user + worked examples — DONE

Output:
- Bundled fictional demo user "Jane Demo" (`slug: jane-demo`):
  - `applications/resumes/data/jane-demo/master-experience.yaml` — 5 jobs across 14 years (Acme Renewables, Bluepeak Robotics, Globex Power, Initech, Acme AI). All companies fictional. Plausible-but-fake achievements.
  - `applications/resumes/data/jane-demo/skills-inventory.yaml` — technical / management / industry / geographic expertise tagged for variant selection.
  - `applications/resumes/data/jane-demo/standard-answers.yaml` — form-fill data + screening Q&A + ATS keywords.
  - `applications/resumes/data/jane-demo/user-config.yaml` — resume variants, template mapping, Jane-specific fit-score adjustments, tailoring notes.
- `plans/EXAMPLES/jane-demo-walkthrough.md` — end-to-end narrative session showing how rules + skills + procedures fit together: cold outreach to 5 companies, reply + meeting prep, application via `/apply`, interview prep via `/company-deep-dive`, session-end.
- `.gitignore` allow-listed `jane-demo/` directories so the demo data ships with the repo while real users' per-slug data stays gitignored.

Validation gate: walkthrough internal links resolve; Jane's data plausibly drives the cold-outreach and resume-tailor skills end-to-end on paper.

### Phase 7 — Documentation + polish — DONE

Output:
- `AGENTS.md` at repo root — canonical AI-agent onboarding doc explaining the four-layer model, the bootstrap sequence, available skills, critical invariants, per-user data conventions, and continuity across sessions.
- Expanded existing doc stubs:
  - `docs/SETUP.md` — full installation walkthrough (env, config, MCPs, troubleshooting table).
  - `docs/CUSTOMIZE.md` — file map + common-customisation recipes.
  - `docs/ARCHITECTURE.md` — four-layer model diagram, data-flow diagram, schema, filesystem layout.
  - `docs/EXAMPLES.md` — pointer to Jane Demo walkthrough + worked-example references.
  - `docs/CONTRIBUTING.md` — opinionated-by-design framing, PR checklist with forbidden-token grep.
- New docs:
  - `docs/EXTEND.md` — how to add rules / skills / tools / procedures / employer extensions / new DB backends.
  - `docs/MULTI-USER.md` — opt-in multi-user setup.
  - `docs/MIGRATION-FROM-PRIVATE-FORK.md` — cherry-pick / remote / rebuild patterns; sanitisation checklist.
- `tools/employer-extension-example/README.md` — documents the pattern with placeholder names; Python implementation deferred to Phase 4.
- `README.md` updated: status, full skills list, quickstart, AGENTS.md prominence.

Validation gate: every internal markdown link resolves; SETUP.md is followable end-to-end on paper; README quickstart points at right files; forbidden-token grep on docs/ (excluding this PLAN.md, which is the migration meta-doc) + AGENTS.md + tools/employer-extension-example/ — **PASSED**.

Note: marking the GitHub repo as a Template Repository, adding repo description / topics, and pinning to profile are user actions in the GitHub UI. Document only.

## Deferred — separate workstreams

### Private-repo hygiene audit (`alexmonegrop/job-hunt`, separate from this template)

After Phase 4 lands, do a sweep of the private repo to:
- Move any tracked secrets out of tracked paths.
- Audit git history with [`gitleaks`](https://github.com/zricethezav/gitleaks) for leaked credentials.
- Normalise paths and patterns to match what the template expects, so future template → private syncs are clean.
- Verify `.gitignore` covers everything we now know to gitignore.

This is **separate** from the template work. See `docs/MIGRATION-FROM-PRIVATE-FORK.md` for the cross-pollination pattern.

## Operating notes for whoever continues this

- **Always start a continuation session by re-reading this file.** Update phase checkboxes as you finish work.
- **The private repo at `C:\Users\alexm\claude-work-folder\job-hunt` is read-only reference** — never modify it from a `job-hunt-os` session.
- **Validation gates are not optional.** Each phase has a gate; don't move on until you've passed it.
- **Single source of truth = this file.** Strategic decisions in conversation should be reflected here.
- **Default branch is `main`.** Standard PR flow: feature branch → PR → merge to main (for big changes); commit-to-main is OK for clearly-scoped milestone work like the v1 build.
- **Never push secrets.** `.env` is gitignored. `config/*.yaml` (real, not example) is gitignored. Per-user content directories are gitignored at the slug level (except `_template/` and `jane-demo/`).

## Quick reference — directory structure

```
job-hunt-os/
├── README.md, AGENTS.md, LICENSE, CLAUDE.md, .gitignore, .env.example
├── docs/                            # SETUP, CUSTOMIZE, ARCHITECTURE, EXAMPLES, EXTEND, CONTRIBUTING, MULTI-USER, MIGRATION-FROM-PRIVATE-FORK, PLAN
├── .claude/
│   ├── rules/                       # 9 auto-loaded rule files
│   └── skills/                      # 13 invokable skills
├── config/                          # *.example.yaml (tracked) + *.yaml (gitignored)
├── infrastructure/                  # docker-compose, init-db, Caddy (Phase 4)
├── tools/
│   ├── setup/                       # init-nocodb, first-run (Phase 4)
│   ├── resume-tailor/               # (Phase 4)
│   ├── job-search/                  # (Phase 4)
│   ├── interview/                   # (Phase 4)
│   ├── bootstrap/                   # multi-user onboard (Phase 4)
│   └── employer-extension-example/  # README pattern docs only; code in Phase 4
├── operating-procedures/            # 9 long-form methodology docs
├── reference-files/templates/       # Cover-letter template, master-experience.template.yaml
├── applications/                    # gitignored at per-user level
│   ├── jobs/, cover-letters/, tracking/
│   └── resumes/source/ + resumes/data/_template/ + resumes/data/jane-demo/
├── interviews/, outreach/, research/   # gitignored at per-user level
└── plans/
    ├── EXAMPLES/                    # Jane Demo walkthrough
    └── archive/                     # gitignored
```

## Status summary table

| Phase | Status | Validation | Commit |
|-------|--------|-----------|--------|
| 1 — Scaffolding | DONE | Skeleton + GitHub repo | (initial) |
| 2 — Rules + skills | DONE | Forbidden-token grep zero hits | M1 |
| 3 — Config | DONE | Skills read from config/*.yaml | M2 |
| 4 — Tools + infra | DONE | Smoke test against jane-demo: scoring-only → .docx → quality gate (PASS) → PDF | M7-M12 |
| 5 — Operating procedures + reference templates | DONE | Forbidden-token grep zero hits | M3 |
| 6 — Jane Demo + walkthrough | DONE | Walkthrough internal links resolve | M4 |
| 7 — Documentation + AGENTS.md | DONE | Internal markdown links resolve; SETUP followable | M5 |

**v1 template release**: shipped with M12.
