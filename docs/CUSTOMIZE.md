# Customize

> ⏳ Stub — full guide lands in Phase 7. See [`docs/PLAN.md`](PLAN.md).

Areas this guide will cover:

- **Your identity & profile** — `config/user-profile.yaml`: name, slug, location, languages, target roles, citizenship, base location, work-authorization markets.
- **Your target market** — region(s), industries, sub-segments, excluded companies, blocked employers (e.g., previous employer you don't want to apply to).
- **Your fit-score model** — `config/fit-score.yaml`: weights, penalties (e.g., MBA required → -2), bonuses (e.g., role values your specialty → +1), thresholds (Full / Longshot / Skip / Auto-skip).
- **Your resume corpus** — `applications/resumes/data/<slug>/master-experience.yaml`: every bullet from every job you've held, with metadata for tagging and scoring.
- **Your insight library** — `config/insight-formulas.yaml` (optional): pre-built counter-intuitive insights tied to your industries, used by `/cold-outreach`.
- **Your message tone** — rule 02 word counts, tone (peer / advisor / curious), call-to-action style.
- **Your operating cadence** — daily/weekly batch sizes, follow-up timings, archive policies.
- **Your tooling** — which job boards, which MCPs, which optional integrations (Hunter.io, Lusha, n8n).
- **Multi-user** — opt-in if you operate the system on behalf of multiple people.
