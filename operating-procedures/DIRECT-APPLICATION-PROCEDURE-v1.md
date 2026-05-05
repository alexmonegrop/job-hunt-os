# Direct Application Operating Procedure v1

**Document type**: Reference. For automatic enforcement, see `.claude/rules/06-application-standards.md`.

**Purpose**: End-to-end workflow for discovering, preparing, and submitting job applications.

**Companion**: skills `job-search`, `apply`, `application-tracker`. Networking workstream procedure: `OUTREACH-OPERATING-PROCEDURE-v4.md`.

## Overview

The Direct Application workstream runs alongside the Networking workstream. Both share the Target Companies hub but have separate pipelines:

```
Target Companies (HUB)
├── Networking:    Target Contacts → Sales Pipeline → Interactions → outreach/{user-slug}/messages/
└── Applications:  Job Postings → Applications → Interactions → applications/{user-slug}/
```

**Cross-workstream intelligence**: when applying at a company with existing networking contacts, flag as "Warm Application" and adjust strategy.

## Step 1: Job Discovery

### 1.1 Automated search (python-jobspy)

Run via skill `job-search`:
```python
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "glassdoor", "linkedin"],
    search_term="Program Manager AI",
    location="<target city, country>",
    results_wanted=20,
    country_indeed="<country>"
)
```

Boards covered (defaults — extend in `config/regions.yaml` `job_boards[]`):
- Indeed, LinkedIn (via JobSpy)
- Glassdoor where supported
- Regional boards (Bayt, GulfTalent, NaukriGulf, etc.) via WebSearch + Playwright
- Company career pages via Playwright snapshot

### 1.2 Search strategy

Run multiple searches per session:
- Role variants: pull from `user-profile.yaml` `target_roles[]`
- Location variants: pull from `user-profile.yaml` `target_regions[]` and `target_cities[]`
- Industry variants: pull from `user-profile.yaml` `target_industries[]`

### 1.3 Fit scoring

Score each result 0-10 before creating records (see `06-application-standards.md` and `config/fit-score.yaml`).

Raw threshold: ≥6 → proceed. 4-5 → review with user. <4 → skip.

### 1.4 Two-pass scoring (NEW — see APPLICATION-SPEED-LESSONS-v1)

| Pass | When | Input | Purpose |
|------|------|-------|---------|
| Pass 1 (discovery) | During search | Title + summary + location | Quick filter; drop obvious mismatches |
| Pass 2 (pre-application) | Before resume prep | Full JD via WebFetch | Confirm score ≥6, verify role / location / requirements match |

Never start resume tailoring until Pass 2 confirms the score.

### 1.5 Record creation

Batch-create Job Posting records (`bulk_insert` to `job_postings`) for all qualifying postings (adjusted score ≥5, tagging 5-6 as LONGSHOT) in a single message.

## Step 2: Application Preparation

### 2.1 Resume tailoring

Run via skill `resume-tailor` (or `RESUME-TAILORING-PROCEDURE-v1.md`):
1. Analyse posting → must-haves, nice-to-haves, industry keywords
2. Select template variant (per `user-config.yaml` `template_mapping`)
3. Score achievements
4. Generate `.docx`
5. Quality gate (BLOCKING — must PASS before PDF)
6. Generate PDF
7. Draft cover letter (Hook → Alignment → Value → CTA, 250-400 words)

**Output**: `applications/{user-slug}/{company}-{job-slug}/`

### 2.2 Standard answers

Pre-loaded from `applications/resumes/data/{user-slug}/standard-answers.yaml`:
- Personal info, work authorisation, salary expectations
- Common screening questions
- "Why interested" templates
- Leadership style, challenges overcome, etc.

### 2.3 Parallel resume prep (CRITICAL for batch sessions)

Spin up one sub-agent per qualifying posting. All run simultaneously. See `APPLICATION-SPEED-LESSONS-v1.md` for the pattern.

```
Agent("Prep Company A", "...", subagent_type="coder")
Agent("Prep Company B", "...", subagent_type="coder")
Agent("Prep Company C", "...", subagent_type="coder")
```

5-7 tailored resumes ready in ~3 min instead of 45-60 min sequential.

## Step 3: Application Submission

### 3.1 Non-LinkedIn (automated via Playwright)

```
Navigate → Snapshot → Fill Form → Upload Resume → Screenshot → User Confirms → Submit → Screenshot
```

Critical rules:
- ALWAYS screenshot before submit
- ALWAYS get user confirmation
- ALWAYS screenshot after submit
- Save all screenshots to `applications/tracking/`

### 3.2 LinkedIn Easy Apply (automated — user authorised)

Use the standardised shadow-DOM pattern in skill `apply` Step 3 (or `APPLICATION-SPEED-LESSONS-v1.md` Bottleneck 3 template).

### 3.3 Post-submission records

Create:
1. **Application record** — status `Submitted`
2. **Interaction record** — type `Application Submitted`
3. **Update Job Posting** — status `Applied`

Batch via `bulk_insert` at end of session, not per-application.

## Step 4: Follow-Up Management

### 4.1 Timing

| Follow-up | Timing | Action |
|-----------|--------|--------|
| First | 7 business days | Professional check-in |
| Second | 14 days after first | Value-add with new insight |
| Close | 21+ days | Mark as no response |

### 4.2 Warm vs cold follow-up

- **Cold** (no networking contact): standard professional follow-up.
- **Warm** (networking contact exists): follow up through contact instead.
  - "Hi [Contact], I applied for [Role] on your team. Any insight on timeline?"

### 4.3 Weekly review

Run via skill `application-tracker`:
- Dashboard of all application statuses
- Follow-ups due this week
- Cross-workstream opportunities
- Action list for next week

## Step 5: Cross-Workstream Integration

### When discovering a Job Posting
1. Check Target Companies → link if exists
2. Check Sales Pipeline → flag as "Warm Application"
3. If warm: consider reaching out to contact before / alongside the application

### When doing networking outreach
1. Check Job Postings at that company → mention in outreach context
2. If posting exists: "I noticed you're hiring for X..."

### Warm-application strategy
- Mention contact in cover letter (subtly)
- Reach out to contact with application context
- Follow up through contact, not cold HR

## Batch Processing Patterns

### Job-search session (all searches parallel)
```
Search 1: "Program Manager [city 1]" (Indeed + Glassdoor + LinkedIn)
Search 2: "AI Product Manager [country]" (Indeed + LinkedIn)
Search 3: "Digital Transformation [region]" (Indeed + regional board)
WebSearch: "site:[regional board] program manager"
→ Score all results
→ Batch-create all Job Posting records
```

### Application-prep session (per company)
```
Read job posting → Read master YAML → Generate resume → Generate PDF → Draft cover letter
→ All in one message per company
```

### Weekly review (single session)
```
Query all Applications → Identify follow-ups → Cross-reference contacts → Generate action list
→ All in one session
```

## File Organisation

```
applications/
├── jobs/                       ← Job posting files (yaml/md)
│   └── {company}-{job-slug}.{yaml,md}
├── resumes/
│   ├── source/                 ← Original .docx (READ-ONLY)
│   └── data/                   ← YAML source data
│       ├── _template/
│       └── {user-slug}/
├── {user-slug}/                ← Per-application tailored versions (gitignored)
│   └── {company}-{job-slug}/
│       ├── resume.docx
│       ├── resume.pdf
│       └── cover-letter.md
├── cover-letters/              ← Standalone drafts
└── tracking/                   ← Screenshots + session logs
```

## Quality Checklist

### Per application
- [ ] Job Posting record exists in DB with adjusted fit score ≥ 5
- [ ] Full JD read (not just title / summary) — Pass 2 score confirmed
- [ ] Resume tailored to specific posting (or generic for longshots)
- [ ] Quality gate PASSED
- [ ] Cover letter drafted (if Full protocol)
- [ ] Cross-workstream check completed
- [ ] Application submitted (or package prepared)
- [ ] Application + Interaction records created
- [ ] Follow-up date set

### Weekly
- [ ] All pending follow-ups addressed
- [ ] New job search run
- [ ] Application dashboard reviewed
- [ ] Cross-workstream opportunities checked

## See Also

- `APPLICATION-SPEED-LESSONS-v1.md` — bottlenecks and fixes from high-volume sessions
- `RESUME-TAILORING-PROCEDURE-v1.md` — tailoring detail
- skill `apply`, `job-search`, `application-tracker`
