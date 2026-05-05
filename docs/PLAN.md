# Rollout Plan — `job-hunt-os`

**Status as of last update**: **v1 template complete.** Phases 1, 2, 3, 5, 6, 7 done. Phase 4 (Python tooling + Docker infrastructure) deferred to a follow-up release. This file is the canonical handoff doc — read it first when picking up this project in a new session.

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

### Phase 4 — Port tools and infrastructure — DEFERRED

**Status**: deferred to a focused follow-up session. Reason: stateful, requires live testing with Docker, NocoDB, Python deps, and Playwright. Better as its own session than tacked onto the methodology port.

When this session runs, it will port (with sanitisation):
- `tools/resume-tailor/` — score, rewrite, generate `.docx` + PDF, quality gate.
- `tools/job-search/` — JobSpy + custom search wrappers.
- `tools/interview/` — `mock-interview.py`, `recruiter-review.py`, `run-mock-curl.sh`, generic role contexts.
- `tools/bootstrap/` — multi-user onboarding bootstrap.
- `tools/sia/` → `tools/employer-extension-example/` — fully sanitised port of the employer-extension pattern with placeholder names.
- `tools/setup/init-nocodb.py` — fresh-install schema initialiser.
- `tools/setup/first-run.py` — env / Docker / Chrome / MCP health check.
- `infrastructure/docker-compose.yml`, `Caddyfile`, `init-db/01-create-databases.sql`, `init-db/02-jobhunt-schema.sql`, `infrastructure/.env.example`.

Drop:
- `infrastructure/n8n-backup/` (n8n workflows from another project, not job-hunt).
- `infrastructure/migration-data/*.json` (Airtable migration dumps with real records).
- `infrastructure/migrate-airtable.py`, `tools/airtable-setup-applications.md`, `tools/migrate-file-structure.py` (one-time historical scripts).

Validation gate (when run): a user with a fresh NocoDB instance can run `python tools/setup/init-nocodb.py` and end up with a working schema; can run `tools/resume-tailor/tailor-resume.py` against the template YAML without errors.

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

### Phase 4 — Python tooling + Docker infrastructure
See above. This is the next focused session.

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
| 4 — Tools + infra | **DEFERRED** | (when run) Fresh init produces working schema + tools execute | — |
| 5 — Operating procedures + reference templates | DONE | Forbidden-token grep zero hits | M3 |
| 6 — Jane Demo + walkthrough | DONE | Walkthrough internal links resolve | M4 |
| 7 — Documentation + AGENTS.md | DONE | Internal markdown links resolve; SETUP followable | M5 |

**v1 template release**: ready when Phase 4 ships. Until then, this is a **methodology + structure release** — the reasoning system is complete, the executable Python tooling is the remaining gap.
