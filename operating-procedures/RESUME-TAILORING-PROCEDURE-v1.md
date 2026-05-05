# Resume Tailoring Operating Procedure v1

**Document type**: Reference (for humans + AI agents). For automatic enforcement, see `.claude/rules/07-resume-tailoring-rules.md`.

**Purpose**: Detailed workflow for creating role-specific resume versions and cover letters.

**Companion**: skill `resume-tailor`.

## Overview

Each user has 2-3 resume variants defined in `applications/resumes/data/{user-slug}/user-config.yaml`. Defaults shipped:

| Template | Title | Best For |
|----------|-------|----------|
| Innovation | "<emphasizes startup/founder, AI/ML, product innovation>" | Startup / founder roles, innovation director, entrepreneurship |
| Delivery | "<emphasizes program management, large-scale delivery>" | Program management, product management, digital transformation |
| Generic | "<balanced version>" | General applications, mixed roles |

The tailoring process scores the user's achievements against job requirements and selects the most relevant content for each application.

## Source Data

### Master YAML files

Located at `applications/resumes/data/{user-slug}/`:

1. **`master-experience.yaml`** — all work experience with tagged achievements
   - Each achievement has: id, text, tags, metrics, priority score, variant availability
   - Tagged for filtering (e.g., `[ai, startup, region, consulting]`)

2. **`skills-inventory.yaml`** — technical and management skills
   - Each skill tagged with role-type relevance
   - Priority scores for ordering

3. **`standard-answers.yaml`** — form-field answers
   - Personal info, work authorisation, salary
   - Common interview / application questions

4. **`user-config.yaml`** — user-specific tailoring config
   - Resume variants available
   - Default `template_mapping` (role → template)
   - `fit_score_adjustments` (penalties + bonuses)

### Keeping data current

When the user updates their actual resume:
1. Read the new resume PDF / DOCX.
2. Update `master-experience.yaml` with any new achievements.
3. Add new tags for new skills / industries.
4. Update dates and metrics.
5. Update `skills-inventory.yaml` if new tools / methodologies appear.

## Step-by-Step Tailoring Process

### Step 1: Analyse job posting

Read the posting and extract:
```yaml
job_title: "Senior Program Manager, AI Initiatives"
company: "Acme Renewables"
requirements:
  - "10+ years program management experience"
  - "PMP certification"
  - "Experience with large-scale digital transformation"
  - "[Industry] knowledge"
  - "Stakeholder management at C-suite level"
nice_to_haves:
  - "AI/ML project experience"
  - "[Region] experience"
  - "Team leadership (5+ reports)"
industry_keywords:
  - "[industry term 1]"
  - "[industry term 2]"
role_category: "PM"  # PM / Product / AI-DT / Operations
```

### Step 2: Select template

Read default mapping from `user-config.yaml` `template_mapping`:
- PM / Operations → Delivery
- Product → Delivery
- AI-DT / Innovation → Innovation
- Mixed / unclear → Generic

User can always override.

### Step 3: Score achievements

For each achievement in `master-experience.yaml`:

| Match type | Points | Example |
|-----------|--------|---------|
| Must-have keyword match | 3 | Job requires "PMP" → achievement mentions PMP |
| Nice-to-have match | 2 | Job prefers regional experience → achievement references regional client |
| Industry keyword match | 1 | Job in "energy" → achievement at an energy company |
| Base priority bonus | 0-2 | Scaled from achievement's inherent priority |

**Selection**: take top 3-4 scored achievements per experience entry.

Example scoring:
```
Achievement: "Managed program and PMO for 15 RT3D, VR, and AI agile projects, $10M+ revenue"
vs Job requiring: "Program management", "AI experience", "Large budgets"

- "Program management" match → +3
- "AI" match → +3
- "Large budgets" ($10M+) → +3
- Nice-to-have "team leadership" → +2
- Industry "technology" → +1
- Base priority (10) → +2
Total: 14 → very high relevance
```

### Step 4: Generate tailored resume

```bash
python tools/resume-tailor/tailor-resume.py \
  --user {user-slug} \
  --job-file applications/jobs/{company}-{job-slug}.yaml \
  --output-dir applications/{user-slug}/{company}-{job-slug}/
```

### Step 5: Quality gate (MANDATORY — BLOCKING)

```bash
python tools/resume-tailor/quality-gate.py \
  --resume applications/{user-slug}/{company}-{job-slug}/resume.docx \
  --job-file applications/jobs/{company}-{job-slug}.yaml
```

If FAIL:
1. Read scorecard for failures.
2. Fix the job YAML (more `text_overrides`, fix `skills_override`, add `title_override`).
3. Regenerate resume.
4. Re-run quality gate.
5. Repeat until PASS.

### Step 6: Generate PDF

```bash
python tools/resume-tailor/generate-pdf.py \
  --input applications/{user-slug}/{company}-{job-slug}/resume.docx
```

Fallback: if `docx2pdf` fails (no MS Word), open the `.docx` manually and Save As PDF.

### Step 7: Draft cover letter

Structure (250-400 words):

#### 1. Hook (1-2 sentences)
Reference specific company news / initiative.

> "[Company]'s [recent initiative / commitment] represents exactly the kind of transformation I've spent my career enabling."

#### 2. Alignment (2-3 sentences)
Connect specific experience to their needs (pull from `master-experience.yaml`).

> "At [past employer], I managed [X] AI projects for enterprise clients, generating $[Y] in revenue with [Z]% budget deviation. My [certification] and experience orchestrating multi-stakeholder alignment on [flagship project] directly parallel the program-management demands of [Company]'s [initiative]."

#### 3. Value (2-3 sentences)
Unique value proposition (pull from `user-profile.yaml` `value_props[]`).

> "As a [credibility anchor 1] and [credibility anchor 2], I bring both the [trait A] to innovate and the [trait B] to deliver at scale. My [regional expertise] positions me to navigate the unique stakeholder dynamics of [Company]'s transformation."

#### 4. CTA (1-2 sentences)
> "I'd welcome the opportunity to discuss how my background can contribute to [Company]'s goals. I'm available at your convenience."

**Save**: `applications/{user-slug}/{company}-{job-slug}/cover-letter.md`.

## Quality Checks

### Resume quality
- [ ] Based on correct template variant
- [ ] All must-have requirements addressed
- [ ] Keywords from posting appear naturally (not forced)
- [ ] 2 pages maximum
- [ ] No fabricated achievements
- [ ] Contact info current
- [ ] Formatting clean and professional
- [ ] PDF generated and formatting verified
- [ ] Quality gate PASS

### Cover letter quality
- [ ] 250-400 words
- [ ] References specific company news / initiative
- [ ] Includes at least one metric from the resume
- [ ] Mentions regional expertise when relevant
- [ ] Shows company knowledge
- [ ] Hook → Alignment → Value → CTA structure
- [ ] No "I believe I would be a great fit" clichés
- [ ] Does not repeat the entire resume

## Common Pitfalls

1. **Keyword stuffing** — don't force keywords; weave naturally into achievements.
2. **Over-tailoring** — don't remove all non-matching achievements; keep credibility breadth.
3. **Template mismatch** — Innovation template for a PM role undersells delivery experience.
4. **Metric inflation** — only use metrics actually in the resume; never fabricate.
5. **Cover letter = resume rehash** — cover letter should add narrative, not repeat bullets.
6. **Ignoring nice-to-haves** — these often differentiate candidates; address them.

## File Structure Reference

```
applications/resumes/
├── source/                          ← Original .docx (NEVER modify)
│   └── {user-slug}-resume-<variant>.docx
├── data/
│   ├── _template/                   ← Annotated templates
│   │   └── master-experience.template.yaml
│   └── {user-slug}/
│       ├── master-experience.yaml
│       ├── skills-inventory.yaml
│       ├── standard-answers.yaml
│       ├── user-config.yaml
│       └── role-profiles.yaml
└── ../{user-slug}/                  ← Per-application tailored versions
    └── {company}-{job-slug}/
        ├── resume.docx
        ├── resume.pdf
        └── cover-letter.md
```

## See Also

- `.claude/rules/07-resume-tailoring-rules.md` — auto-enforced rules
- skill `resume-tailor` — the invokable workflow
- `applications/resumes/data/_template/master-experience.template.yaml` — annotated YAML schema
