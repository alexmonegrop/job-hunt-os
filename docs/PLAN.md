# Rollout Plan — `job-hunt-os`

**Status as of last update**: **Phase 4 ~83% done. M7-M11 shipped. M12 remaining.**
Phases 1, 2, 3, 5, 6, 7 = v1 template (complete). Phase 4 (Python tooling + Docker infrastructure) is split across milestones M7-M12; M7 through M11 are committed and pushed. M12 (integration smoke test + Phase 4 close-out) is the only remaining work.

This file is the canonical handoff doc — read it first when picking up this project in a new session.

---

## RESUME HERE (next session)

**Last session ended after M11 push (commit `8767916`). Resume at M12.**

What M12 needs to do:

1. **Bring the data stack back up** (it was torn down clean at end of M7 testing):
   ```bash
   cd infrastructure
   cp .env.example .env
   # Edit .env: set POSTGRES_PASSWORD to a fresh hex token
   docker compose up -d
   ```
   Wait ~30 sec for healthcheck.

2. **Set up NocoDB**: visit `http://localhost:8080`, create admin user, add the postgres `jobhunt` DB as a Data Source (host `postgres`, port `5432`, user `jobhunt`, pwd from `infrastructure/.env`, db `jobhunt`), generate API token.

3. **Configure project `.env`**:
   ```bash
   cp .env.example .env
   # Edit: JOB_HUNT_USER=jane-demo
   # Edit: NOCODB_URL=http://localhost:8080
   # Edit: NOCODB_API_TOKEN=<from step 2>
   ```

4. **Discover schema IDs**:
   ```bash
   python tools/setup/init-nocodb.py
   ```
   Should write `NOCODB_BASE_ID` + 3 link-field IDs back to `.env`.

5. **End-to-end smoke test** against jane-demo:
   ```bash
   # 5a. Already proven during M8: scoring-only mode produces correct JSON
   python tools/resume-tailor/tailor-resume.py --user jane-demo \
     --job-file tools/resume-tailor/jobs/_template.yaml \
     --output-dir /tmp/jane-test --scoring-only

   # 5b. Full mode: generate .docx (NEW — not yet validated)
   python tools/resume-tailor/tailor-resume.py --user jane-demo \
     --job-file tools/resume-tailor/jobs/_template.yaml \
     --output-dir /tmp/jane-test
   # Expected: /tmp/jane-test/resume.docx written

   # 5c. Quality gate against the generated .docx (NEW — not yet validated)
   python tools/resume-tailor/quality-gate.py --user jane-demo \
     --resume /tmp/jane-test/resume.docx \
     --job-file tools/resume-tailor/jobs/_template.yaml
   # Expected: JSON scorecard with PASS/WARN/FAIL verdict.
   # Note: recruiter_review will WARN-skip (recruiter-review.py deferred).

   # 5d. PDF generation (NEW — needs docx2pdf or LibreOffice)
   python tools/resume-tailor/generate-pdf.py --input /tmp/jane-test/resume.docx
   # Expected: /tmp/jane-test/resume.pdf
   # If docx2pdf fails (no MS Word), fall back to LibreOffice or document
   # as a known platform-dependent step.
   ```

6. **Tear down**:
   ```bash
   docker compose --project-directory infrastructure down -v
   rm infrastructure/.env
   ```

7. **Update PLAN.md + README.md**:
   - Mark Phase 4 as **DONE**.
   - Drop the "Phase 4 deferred" callout from README.
   - Update status summary table.

8. **Final commit + push** as M12.

### Known issues to address in M12 if encountered

- **`docx2pdf` may fail without MS Word** — script falls back to LibreOffice. If neither is installed on the test machine, document as a "user-side dependency" and proceed (not a code bug).
- **Quality gate may FAIL on bullet count** — Jane's master-experience.yaml has 14 achievements total. With `min_bullets: 22` default, the tool will fill aggressively. If it can't reach 22 (because Jane only has 14), the gate FAILs on bullet_count. Either: (a) lower `min_bullets` in the test job YAML to 14, or (b) document as expected behaviour and PASS the WARN. Recommend (a) for the smoke test.
- **NocoDB MCP not configured in test session** — that's fine; the smoke test exercises the Python tools directly via CLI, not via Claude Code MCP. The MCP integration is exercised separately via `/session-start`.

### Optional in M12 (nice-to-have, not blocking)

- Run `/session-start` in Claude Code with the live stack to verify the MCP integration works end-to-end (database connected, can list tables, etc.). This requires `~/.claude.json` configured with the local NocoDB token — non-trivial setup. Defer to a documentation-only validation if time-constrained.

### Deferred from Phase 4 (not in M12 scope)

- `tools/resume-tailor/recruiter-review.py` — LLM recruiter review using OpenRouter. Quality gate gracefully WARN-skips when missing. Add in a follow-up release.
- `tools/resume-tailor/create-template.py` — variant scaffolding utility. Less critical than core flow.
- The full Sia / employer-extension Python port. The README pattern doc shipped in M5 documents the pattern; users can build their own employer extensions with that as guidance. Per session direction.
- n8n MCP integration. Per session direction (dropped entirely).

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

### Phase 4 — Port tools and infrastructure — IN PROGRESS (M7-M11 done, M12 remaining)

**Status**: Phase 4 split into 6 milestones; M7-M11 shipped, M12 (smoke test + close-out) is the only remaining work. See "RESUME HERE" section above.

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

#### M12 — Integration smoke test + close-out — REMAINING

See "RESUME HERE" section at the top of this file.

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
