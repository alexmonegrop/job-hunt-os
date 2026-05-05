---
name: "resume-tailor"
description: "Tailor a resume for a specific job posting by scoring achievements against requirements, selecting the best template variant (Innovation/Delivery/Generic), generating a tailored .docx and PDF, and drafting a cover letter. Uses master YAML data from the active user's resume data. NEVER fabricates achievements."
---

# Resume Tailor

Generates role-specific resume versions and cover letters tailored to individual job postings.

## What This Skill Does

- **Template selection** — Innovation / Delivery / Generic variant based on role type
- **Achievement scoring** — score each achievement against job requirements (0-10)
- **Content selection** — pick top-scoring achievements per experience entry
- **Resume generation** — create tailored `.docx` via `python-docx`
- **PDF conversion** — via `docx2pdf`
- **Cover-letter drafting** — 250-400 words, Hook-Alignment-Value-CTA structure
- **Database integration** — update Job Posting record with the resume version used

## Prerequisites

Required:
- Python 3.10+ with `python-docx`, `pyyaml`, `docx2pdf`
- Active user's master data: `applications/resumes/data/{user-slug}/master-experience.yaml`
- Active user's skills inventory: `applications/resumes/data/{user-slug}/skills-inventory.yaml`
- Active user's user-config: `applications/resumes/data/{user-slug}/user-config.yaml`
- Shared role schemas: `applications/resumes/data/role-type-schemas.yaml` (optional — falls back to defaults)

Multi-user: the active user's slug (from `JOB_HUNT_USER`) determines which data directory to use.

Python tools:
- `tools/resume-tailor/tailor-resume.py` — supports `--user {slug}` flag
- `tools/resume-tailor/generate-pdf.py`
- `tools/resume-tailor/generate-cover-letter-pdf.py` — supports `--user {slug}` flag
- `tools/resume-tailor/quality-gate.py`

## Quick Start

```
"Tailor my resume for the Senior Program Manager role at Acme Renewables"
"Create a resume version using the Innovation template for the AI Product Lead role at Globex Power"
```

## Workflow

### Step 1: Analyze job posting

1. Read the job posting (from `applications/jobs/{company}-{job}.md` / `.yaml` or URL).
2. Extract must-have requirements, nice-to-haves, and industry keywords.
3. Determine role category from `config/user-profile.yaml` `target_roles[]`.

### Step 2: Select template

Read default mapping from `applications/resumes/data/{user-slug}/user-config.yaml` (`template_mapping`):
- PM / Operations → Delivery
- AI-DT / Product → Innovation
- Mixed / unclear → Generic

User can override.

### Step 3: Create job YAML with keyword extraction

Read the full JD and create `applications/jobs/{company}-{job-slug}.yaml`:
```yaml
company: "Acme Renewables"
job_title: "Senior Program Manager"
role_category: "PM"
template: "Delivery"
requirements:
  - "..."
nice_to_haves:
  - "..."
industry_keywords:
  - "..."
```

### Step 4: Run scoring (`--scoring-only` mode)

```bash
python tools/resume-tailor/tailor-resume.py \
  --user {user-slug} \
  --job-file applications/jobs/{company}-{job-slug}.yaml \
  --output-dir applications/{user-slug}/{company}-{job-slug}/ \
  --scoring-only
```

Outputs JSON: selected achievements, scores, matched requirements/keywords per bullet.

### Step 5: Rewrite bullets to mirror JD (Claude LLM step)

Review the JSON and rewrite each selected bullet:

**Rules**:
1. **Mirror JD terminology** — exact phrasing.
2. **Front-load JD keywords**.
3. **Preserve all facts** — every metric, number, company name, timeline.
4. **Emphasise matching aspects** — restructure to lead with what JD emphasises.
5. **Keep similar length** — max +10 words.
6. **NEVER fabricate** — no new achievements or claims.

Also write:
- `summary_override` — summary echoing JD themes
- `skills_override` — skills line reordered to prioritise JD-mentioned tools (see format below)
- `title_override` — optional, when template title doesn't fit

Update the job YAML with `text_overrides`, `summary_override`, `skills_override`, optionally `title_override`.

**`skills_override` format (MANDATORY)**:
```
"Technical Skills: Power BI | JIRA | SAP | SQL | AWS | Python | Docker | Agile/Scrum | <user certifications from config/user-profile.yaml credentials[]>"
```
- First 60% MUST be hard tools.
- Last 40% can include methodologies (Agile/Scrum, PMP, CSPO, PRINCE2, Lean/Six Sigma).
- NEVER include soft capability statements like "Strategic Partnership", "Cross-Functional Leadership".

### Step 6: Generate resume (full mode with overrides)

```bash
python tools/resume-tailor/tailor-resume.py \
  --user {user-slug} \
  --job-file applications/jobs/{company}-{job-slug}.yaml \
  --output-dir applications/{user-slug}/{company}-{job-slug}/
```

### Step 6.5: Quality gate (MANDATORY — BLOCKING)

```bash
python tools/resume-tailor/quality-gate.py \
  --resume applications/{user-slug}/{company}-{job-slug}/resume.docx \
  --job-file applications/jobs/{company}-{job-slug}.yaml
```

If FAIL:
1. Read scorecard to identify failures.
2. Fix the job YAML (more overrides, fix `skills_override`, add `title_override`).
3. Regenerate (re-run Step 6).
4. Re-run quality gate.
5. Repeat until PASS.

If WARN: flag to user, proceed.

NEVER proceed to PDF or submission with FAIL.

### Step 7: Generate PDF

```bash
python tools/resume-tailor/generate-pdf.py \
  --input applications/{user-slug}/{company}-{job-slug}/resume.docx
```

### Step 8: Draft cover letter

Create at `applications/{user-slug}/{company}-{job-slug}/cover-letter.md`:
1. **Hook** (1-2 sentences) — reference specific company news/initiative.
2. **Alignment** (2-3 sentences) — connect user's experience to their needs.
3. **Value** (2-3 sentences) — unique value proposition (regional + AI + enterprise — pull from `config/user-profile.yaml` `value_props[]`).
4. **CTA** (1-2 sentences) — specific next step.

### Step 9: Update database

- Set `resume_version_used` field on Job Posting record.
- Create Interaction record with type `Resume Tailored`.

## Output Structure

```
applications/{user-slug}/{company}-{job-slug}/
├── resume.docx
├── resume.pdf
└── cover-letter.md
```

## Rules

1. **NEVER fabricate achievements** — only use data from `master-experience.yaml`.
2. **NEVER modify source `.docx` templates** — read-only.
3. **ALWAYS score before selecting** — document which achievements were chosen and why.
4. **Keep to 2 pages maximum**.
5. **Cover letters: 250-400 words** with Hook-Alignment-Value-CTA structure.
6. **Every tailored version must reference a Job Posting record**.
7. **Resume bullet rewriting (Step 5) MUST use a high-quality model** — Claude Sonnet 4.6 / Opus 4.6+ or equivalent. Never use a small/fast model for resume content generation.
8. **Quality gate (Step 6.5) MUST pass before PDF generation**.
9. **`skills_override` MUST contain hard tools** — see format above.
10. **`title_override`** — use when the template-derived title doesn't match the target role. Set in job YAML alongside `summary_override`.
11. **`role_category`** — accepts both forms with hyphens or underscores (`AI-DT` / `AI_DT`). Both work.

## Reframed-Experience Guidance (driven by `gap-analysis.yaml`)

The user's `applications/resumes/data/{user-slug}/gap-analysis.yaml` defines reframing rules per role type. The agent reads it and applies the rules during tailoring. The shape of the file:

```yaml
reframes:
  - role_type: "consulting"
    description: "Consulting / advisory / transformation roles"
    rules:
      - "Use 'consulting' title variants for any independent-engagement roles"
      - "Frame summary_override with total years of independent consulting"
      - "Include engagement_type=consulting achievements prominently"
  - role_type: "regional"
    description: "Roles based in or focused on the user's target region"
    rules:
      - "ALWAYS include region-specific achievement bullets"
      - "Frame regional tenure prominently in summary_override"
  - role_type: "technical_pm"
    description: "Technical PM / data / digital transformation roles"
    rules:
      - "ALWAYS include cloud / data-pipeline achievement bullets"
      - "Frame technical depth: SQL, Power Query/DAX, AWS, Docker"
  # ... add more
```

Do not hardcode user-specific reframing rules in this skill. Read them from the user's `gap-analysis.yaml`.

## Template Selection Guide

| Role Type | Template | Emphasis |
|-----------|----------|----------|
| Program Manager | Delivery | PMO, execution, risk management, $-M scale |
| Product Manager | Delivery | Product lifecycle, user journey, backlog |
| AI/ML Lead | Innovation | Startup founder, LLMs, computer vision |
| Innovation Director | Innovation | Design thinking, corporate innovation |
| DT Consultant | Generic | Balanced transformation + technology |
| Operations Director | Delivery | Stakeholder management, team leadership |
