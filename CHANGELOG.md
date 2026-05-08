# Changelog

All notable user-visible changes to this template are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For the full development history (per-milestone, with rollout notes), see [`docs/PLAN.md`](docs/PLAN.md).

---

## [1.0.0] — 2026-05-08

First public release. The template is share-ready: rules, skills, operating procedures, configuration, Python tooling, Docker infrastructure, demo data, and full documentation are all in place.

### Added

- **Rules** (`.claude/rules/`) — 9 auto-loaded rule files covering project structure, database standards, message quality, batch operations, contact selection, file organisation, application standards, and resume tailoring.
- **Skills** (`.claude/skills/`) — 13 invokable workflows: `/cold-outreach`, `/contact-population`, `/meeting-prep`, `/company-deep-dive`, `/warm-followup`, `/job-search`, `/resume-tailor`, `/apply`, `/application-tracker`, `/onboard-user`, `/session-start`, `/session-checkpoint`, `/session-end`.
- **Operating procedures** (`operating-procedures/`) — 9 long-form methodology documents.
- **Python tooling** (`tools/`) — resume tailor + quality gate + PDF generator, JobSpy job search, mock-interview LLM, recruiter-review LLM (M13), NocoDB schema initialisation with `--auto-bootstrap` (M14), onboarding bootstrap, employer-extension example.
- **Infrastructure** (`infrastructure/`) — Docker Compose stack for self-hosted NocoDB + Postgres, with seed schema and Caddy reverse proxy as an opt-in profile.
- **Configuration** (`config/`) — `.example.yaml` files for `user-profile`, `fit-score`, `industries`, `regions`. Same agent, any market.
- **Demo user "Jane Demo"** — full fictional dataset and end-to-end walkthrough.
- **Documentation** (`docs/`) — SETUP, CUSTOMIZE, ARCHITECTURE, EXAMPLES, EXTEND, MULTI-USER, MIGRATION-FROM-PRIVATE-FORK, PLAN, CONTRIBUTING. Plus root-level `AGENTS.md` for AI-agent onboarding and `CLAUDE.md` for Claude-Code-specific configuration.
- **GitHub community standards** — `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.yml`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), this `CHANGELOG.md`.

### Notes

- This is a *template*. Fork it, configure it, run the pipeline against your own data. Per-user content (resumes, applications, outreach, interviews, research) is gitignored at the user level so a fork stays clean.
- The system was extracted from a real, working private repo that ran a successful 12-month job-hunt pipeline (~110 applications, ~500 networked contacts, multiple offers, one role accepted). All personal data has been stripped; only methodology, tooling structure, and rules remain.

[1.0.0]: https://github.com/alexmonegrop/job-hunt-os/releases/tag/v1.0.0
