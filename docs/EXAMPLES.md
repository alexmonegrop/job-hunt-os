# Examples

Walkthroughs and worked examples to give you a concrete sense of how the system runs.

## Jane Demo end-to-end walkthrough

The bundled demo user is **Jane Demo** (`slug: jane-demo`), an entirely fictional person with a plausible 14-year career across industrial AI, robotics, and grid modernisation.

**Read it**: [`plans/EXAMPLES/jane-demo-walkthrough.md`](../plans/EXAMPLES/jane-demo-walkthrough.md).

It covers:
- Session start with `/session-start`
- Cold outreach to 5 fictional companies (Acme Renewables, Solaris Demoland, Vortex Robotics, Helio Grid Solutions, Pioneer AI)
- Reply, meeting prep with `/meeting-prep`
- Direct application via `/job-search` + `/resume-tailor` + `/apply`
- Interview prep via `/company-deep-dive`
- Session-end with commit + push

Jane's data ships with the repo (under `applications/resumes/data/jane-demo/`) so you can inspect a complete profile before building your own.

## Worked outreach message examples

Eight detailed message examples (70-90 words each) with full analysis live in `operating-procedures/UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md`. Each example demonstrates the 6-part formula (news hook → unique insight → evidence → credibility → geographic flexibility → soft ask) applied to a different industry / scenario:

1. AI company expanding to a new region
2. Consulting firm's government partnership
3. Fintech Series B scaling
4. Enterprise software government deal
5. E-commerce platform regional launch
6. Cybersecurity firm's government focus
7. EdTech platform university partnerships
8. HealthTech regulatory approval

All companies and people are fictional — the structure is the lesson, not the specifics.

## Worked resume-tailoring example

> ⏳ Phase 4 — once `tools/resume-tailor/` ships, this will include:
> - Sample job posting YAML (input)
> - Scoring JSON output (with `matched_requirements` and `matched_keywords`)
> - Bullet rewrite examples (before / after, showing JD-mirroring)
> - `summary_override`, `skills_override`, `title_override` examples
> - Quality gate scorecard (PASS / WARN / FAIL)
> - Generated `.docx` and PDF samples

For now, see `applications/resumes/data/_template/master-experience.template.yaml` for the input shape and `operating-procedures/RESUME-TAILORING-PROCEDURE-v1.md` for the algorithm.

## Quick insight development examples

Two complete 15-minute insight-development walkthroughs in `operating-procedures/QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`:
- Fictional fintech expanding to a new country
- Fictional consulting firm's government contract

Each shows the minute-by-minute research process: identify public goal → find hidden pattern → identify counter-intuitive truth → find your authority angle → package the insight.

## Application-speed lessons

Real bottlenecks (with fixes) from running high-volume application sessions: `operating-procedures/APPLICATION-SPEED-LESSONS-v1.md`. Includes:
- The standardised LinkedIn Easy Apply shadow-DOM template
- Two-pass fit scoring (quick filter + full JD verification)
- Parallel sub-agent resume prep pattern (3-5x faster)
- Portal vs LinkedIn dead-end detection
- ATS-specific quirks (SmartRecruiters, Greenhouse, Phenom, Oracle HCM)

## What's coming

Phase 4 will add:
- A worked Docker Compose setup walkthrough
- A worked NocoDB schema initialisation
- Mock-interview transcript examples
- An employer-extension example (the "Sia pattern" — extend the system per-employer with custom resumes and templates)
