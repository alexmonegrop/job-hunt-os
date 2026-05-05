# Jane Demo — End-to-End Walkthrough

This is a narrative walkthrough of a typical session for the bundled demo user, **Jane Demo** (`slug: jane-demo`). Everything in this walkthrough is fictional — Jane, her employers, and her contacts don't exist. The point is to show how the rules, skills, and procedures fit together end-to-end.

If you're a fresh user who just cloned this template, you can run the same sequence with your own data after `/onboard-user`.

---

## Setup (one-time, already done for Jane Demo)

1. Cloned the repo and ran `cp .env.example .env`. Filled in `NOCODB_*` and set `JOB_HUNT_USER=jane-demo`.
2. Ran `python tools/setup/init-nocodb.py` to create the schema. The `users` table now has Jane (user_id 1).
3. Ran `cp config/user-profile.example.yaml config/user-profile.yaml` and customised for Jane's region (Demoland) and target roles.
4. The repo ships with Jane's resume YAMLs at `applications/resumes/data/jane-demo/`:
   - `master-experience.yaml` — fictional but plausible 14-year career
   - `skills-inventory.yaml`, `standard-answers.yaml`, `user-config.yaml`
5. Optional: `pip install python-jobspy python-docx pyyaml docx2pdf`.

---

## Session start

Jane runs `/session-start`. The agent:
- Sees `JOB_HUNT_USER=jane-demo` in `.env`, picks Jane as the active user.
- Reads MEMORY.md (empty on first run).
- Tests MCPs (NocoDB connected, LinkedIn connected, Playwright registered).
- Pulls the latest from `origin/main`.
- Asks: "What would you like to work on?" Jane picks **Networking outreach**.

---

## Cold outreach: 5 companies, 15 contacts

Jane invokes `/cold-outreach`. The agent runs the 5-phase workflow from the `cold-outreach` skill:

### Phase 1 — Company selection (5 min)

Query the database for `target_companies` with no Sales Pipeline entries and tier ≥ 2. Jane has previously seeded 8 companies (via the `contact-population` skill) including:

- **Acme Renewables (jr.)** — a smaller competitor to Jane's current employer; expanding into Eastern Federation.
- **Solaris Demoland** — a state-owned solar developer with a $200M new-build program.
- **Vortex Robotics** — fictional industrial-inspection robotics startup, just raised a $30M round.
- **Helio Grid Solutions** — fictional grid-modernisation player active in Riverbend.
- **Pioneer AI** — fictional industrial-AI startup, ex-Acme founders, raised $15M Series A.

The agent picks all 5 (Tier 1 + Tier 2).

### Phase 2 — Target-region expansion research (20 min for all 5)

For each, the agent runs 3-4 WebSearch queries (`{Company} Demoland expansion 2026`, `{Company} Eastern Federation partnership`, etc.), updates the Target Companies record's `why_strong_fit` and `recent_signals`. Each `why_strong_fit` connects three elements:

> *"Solaris Demoland's $200M Northgate solar build-out (announced March 2026) needs operational program managers with Demoland-region energy experience. Jane's 3 years at Globex Power leading $22M grid-modernisation across 5 substations + her current Acme Renewables digital-twin programme are directly relevant. Solaris is hiring 4 program managers in Q2 2026."*

The agent develops a counter-intuitive insight per company using the `QUICK-INSIGHT-DEVELOPMENT-GUIDE` 15-minute method. For Solaris:

> *"Most assume the Northgate build-out is a generation problem. The hidden challenge is grid-interconnect timing — Demoland's regulator requires interconnect-impact studies that take 9 months on average, and 4 of the last 6 utility-scale solar builds missed their COD because of it. Helio Grid Solutions is the only Demoland-native player that has navigated this twice."*

### Phase 3 — Contact selection (10 min)

For each company, find the top 3 contacts (target: 3 per × 5 = 15). The agent uses `WebSearch site:linkedin.com/in/ "Solaris Demoland" "manager"` and similar. Picks operational mid-level contacts (Directors, Senior Managers) for the bigger companies, founders / VPs for the smaller ones.

Batch-duplicate-check across all 15 in one query. None already in pipeline.

### Phase 4 — Database record creation (10 min)

`bulk_insert` 15 Sales Pipeline records (one message). Capture returned IDs. `bulk_insert` 15 Interaction records linked to those Pipeline IDs (second message).

### Phase 5 — Message drafting + file creation (15 min)

For each of 15 contacts, draft a 70-90 word message using the v4 formula (Deep Hook → Practitioner Insight → Builder Credibility → Peer Ask). Reference research dossier elements found in Phase 2.

Example for Solaris's Director of Project Delivery, **Tom Frost** (fictional):

> *Subject: Northgate solar build-out — the interconnect-timing trap*
>
> *Tom — congrats on the Northgate program announcement. Pattern from Globex's grid-modernisation portfolio: 4 of 6 recent utility-scale Demoland builds missed COD because the interconnect-impact studies ran 9+ months. Helio Grid Solutions is the only player I've seen navigate this twice cleanly. At Globex I co-managed those exact regulator touchpoints. Worth 15 minutes to compare notes? Based in Northgate, flexible across Demoland.* (76 words)

Save 15 individual files to `outreach/jane-demo/messages/`. Never batch.

---

## Reply, meeting prep

Three days later, Tom replies: *"This is interesting — let's talk Thursday 2pm Northgate office, walking meeting then lunch."*

Jane invokes `/meeting-prep "Tom Frost - Solaris Demoland - Thursday 2pm transit + meal"`.

The agent runs the meeting-prep workflow (`MEETING-PREP-PROCEDURE-v4`):

- **News check**: WebSearch — finds a Solaris press release from yesterday announcing a partnership with Helio. Updates the hook.
- **Research batch**: Tom's LinkedIn (15 years at Solaris, recent posts about renewable interconnect challenges, blog post on regulator timelines), competitive intel, regional pattern.
- **6 insights**: 3 core (interconnect timing, regulator behaviour patterns, grid-side operations gaps) + 3 extended.
- **Vulnerability share** (from Jane's master-experience): the stalled $8M sensor-deployment programme she recovered at Acme.
- **Environment strategy**: transit + meal — 3 must-hit points memorised, story-based delivery, save technical detail for meal portion.
- **Intelligence extraction**: 12 prepared questions tagged by category.

Output: `outreach/jane-demo/prep/solaris-demoland-tom-frost-prep.md`.

---

## Application — direct application workstream

Two weeks later, Solaris posts a Senior Program Manager — Grid Interconnect role on LinkedIn. Jane runs `/job-search "Senior Program Manager Demoland renewables"`.

The agent runs the `job-search` skill: jobspy + LinkedIn Playwright search + WebSearch over Demoland's regional board. 9 results.

For each, **Pass 1 score** uses title + summary. Then the agent **WebFetches the full JD in parallel** for all qualifying postings (Pass 2). The Solaris role scores:

- Raw: role 3 + region 2 + industry 2 + seniority 1 + geography 1 + existing-contact 1 = **10**
- Adjusted bonus +1 for "Demoland-native company building regional practice" = **11 → capped at 10**
- Existing networking pipeline (Tom Frost, Pipeline stage "Meeting completed") flags as **Warm Application**

The agent batch-creates 5 qualifying Job Posting records in one `bulk_insert`.

Jane invokes `/apply "Solaris Senior PM Grid Interconnect"`. The agent:
1. Adjusted score check (passes — full protocol).
2. Resume-tailoring gate: tailored resume doesn't exist → calls `/resume-tailor` first.
3. `resume-tailor`: reads Jane's `master-experience.yaml`, scores achievements against the JD's must-haves (interconnect, multi-stakeholder, energy, PMP), selects top 3-4 per role, rewrites bullets to mirror JD ("multi-stakeholder regulator alignment" instead of "stakeholder management"), generates `resume.docx`, runs quality gate (PASS), generates PDF.
4. Drafts cover letter (Hook = recent Helio partnership; Alignment = Globex grid-modernisation parallels; Value = native Demoland + AI/IoT crossover; CTA = specific availability). Mentions Tom Frost subtly in the alignment paragraph (warm application).
5. Apply: portal-first per channel-priority rule. Solaris portal exists, found via WebFetch. Opens via Playwright, fills form using `standard-answers.yaml` data, uploads tailored PDF, screenshots, submits, screenshots confirmation.
6. Creates Application + Interaction records. Updates Job Posting status to `Applied`.

---

## Interview — company deep dive

A week later Solaris invites Jane for a 45-minute interview with the Director of Operations. She runs `/company-deep-dive "Solaris Demoland - VP Operations interview"`.

The agent generates `outreach/jane-demo/prep/company-deep-dive-solaris-demoland.md`:
- Business fundamentals
- Current strategy (Northgate program details)
- Future direction
- Global + regional competitive landscape (Helio, the international players)
- Industry context (Demoland's interconnect regulator timeline, regional renewable buildout pace)
- Strategic fit (where Jane's Globex + Acme experience maps to their needs)
- Interview intelligence (5 strategic questions, 3 anticipated concerns + responses)

She uses this alongside the meeting-prep doc and standard-answers.

---

## Session end

End of week, Jane runs `/session-end`. The agent:
- Updates MEMORY.md with what happened.
- Updates `plans/OVERALL-PLAN.md` (workstream metrics: 1 message sent, 1 meeting completed, 1 application submitted, 1 interview scheduled).
- Writes session summary to `plans/archive/SESSION-SUMMARY-jane-demo-2026-04-XX.md`.
- Commits everything and pushes to her fork on GitHub.

---

## What this walkthrough demonstrates

- **Configurability**: every step uses `config/user-profile.yaml`, `config/fit-score.yaml`, etc. — not hardcoded values.
- **Layering**: rules auto-enforce; skills orchestrate; procedures provide rationale; tools (resume-tailor, init-nocodb) execute.
- **Cross-workstream**: networking and direct application share the company hub. Warm applications are flagged automatically.
- **Per-user data**: everything Jane creates lands under `outreach/jane-demo/`, `applications/jane-demo/`, etc. — gitignored at the user level (Jane Demo herself is the exception, since this is a public template).
- **Quality gates**: fit-score pre-check, resume quality gate, news-hook date validation — none are optional.

---

## Try it yourself

1. Run `/onboard-user` to create your own profile.
2. Customise `config/*.yaml` for your region / industries / roles.
3. Run `/session-start`, then `/cold-outreach` for 5 of your real target companies.
4. Read `operating-procedures/OUTREACH-OPERATING-PROCEDURE-v4.md` for the full methodology.

The goal is not to follow this exact script — it's to give you a working operating system that handles the rote work so you can focus on the things only you can do (deep research, judgement, building relationships).
