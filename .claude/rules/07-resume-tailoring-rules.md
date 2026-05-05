# Resume Tailoring Rules

## Source Data Management

### Master YAML Files (Single Source of Truth)

Located at `applications/resumes/data/{user-slug}/`:

- **`master-experience.yaml`** — All work experience, achievements, and summary variants.
- **`skills-inventory.yaml`** — Technical, management, industry, and tool skills.
- **`standard-answers.yaml`** — Common application form Q&A.
- **`user-config.yaml`** — User-specific tailoring config (resume variants available, default certifications, contact info).

A annotated template lives at `applications/resumes/data/_template/master-experience.template.yaml`. Copy to `applications/resumes/data/{your-slug}/master-experience.yaml` and fill in.

### CRITICAL Rules

1. **NEVER fabricate achievements or credentials** — only use data from actual resumes.
2. **NEVER modify source `.docx` templates** in `applications/resumes/source/` — they are read-only.
3. **Master YAML must stay in sync** — if the user updates their resume, YAML must be updated too.
4. **Every tailored version references a Job Posting record** in the database.
5. **NEVER substitute one company's tailored resume for another.** Each tailored resume contains JD-specific keyword mirroring, bullet rewrites, and summary overrides. A resume tailored for Company A is useless for Company B even if the role title looks similar. Always tailor fresh. No "closest match" shortcuts.

## Resume Variants

The user defines available variants in `applications/resumes/data/{user-slug}/user-config.yaml`. The default template ships with three variants:

- **Innovation** — emphasises startup/founder experience, AI/ML, product innovation.
- **Delivery** — emphasises program management, execution, large-scale delivery.
- **Generic** — balanced version for general applications.

**Selection logic** (defaults — overridable in `user-config.yaml`):
- PM / Operations roles → Delivery template
- AI-DT / Product roles → Innovation template
- Mixed / unclear → Generic template

## Tailoring Process

### Step 1: Analyze Job Posting
- Extract must-have requirements
- Identify nice-to-have requirements
- Note industry/domain keywords
- Identify role category (PM / Product / AI-DT / Operations — per `config/user-profile.yaml` `target_roles[]`)

### Step 2: Score Achievements (`--scoring-only` mode)

Run the script with `--scoring-only` to get JSON output:
```bash
python tools/resume-tailor/tailor-resume.py \
  --job-file applications/jobs/{company}-{job-slug}.yaml \
  --output-dir applications/{user-slug}/{company}-{job-slug}/ \
  --scoring-only
```

For each achievement in `master-experience.yaml`:
- **3 points**: Directly matches a must-have requirement
- **2 points**: Matches a nice-to-have requirement
- **1 point**: Same industry/domain relevance
- **0 points**: No clear connection

JSON output includes `matched_requirements` and `matched_keywords` per achievement.

### Step 3: Rewrite Bullets to Mirror JD Language (Claude LLM step)

After reviewing the scoring JSON, rewrite each selected bullet:

**Rewriting Rules (MANDATORY)**:
1. **Mirror JD terminology** — if JD says "cross-functional alignment," use that exact phrase, not "stakeholder management".
2. **Front-load JD keywords** — put the most relevant JD terms near the start of each bullet.
3. **Preserve ALL facts** — every metric, number, company name, and timeline must stay exactly as-is.
4. **Emphasize matching aspects** — if JD emphasizes "budget management" and the bullet mentions it midway, restructure to lead with budget.
5. **Keep similar length** — max +10 words over the original bullet.
6. **NEVER fabricate** — no new achievements, metrics, claims, or credentials.

Also write:
- `summary_override`: Summary rewritten to echo the JD's key themes.
- `skills_override`: Skills line reordered to prioritise JD-mentioned tools.
- `title_override`: Resume title rewritten to match the target role (optional — only when the template title doesn't fit).

Updates are saved to the job YAML as `text_overrides`, `summary_override`, `skills_override`, and optionally `title_override`.

**`skills_override` format (MANDATORY)**:
```
"Technical Skills: Power BI | JIRA | SAP | SQL | AWS | Python | Docker | Agile/Scrum | PMP, CSPO Certified"
```
- First 60% MUST be **hard tools**: Power BI, JIRA, SAP, SQL, AWS, Python, Docker, Tableau, Figma, etc.
- Last 40% can include **methodologies**: Agile/Scrum, PMP, CSPO, PRINCE2, Lean/Six Sigma.
- **NEVER** include soft capability statements like "Strategic Partnership", "Cross-Functional Leadership", "Strategy & Execution".
- Pipe (`|`) or comma delimited.
- Certifications listed in `config/user-profile.yaml` `credentials[]` are appended.

### Step 4: Generate Output (full mode with overrides)
```bash
python tools/resume-tailor/tailor-resume.py \
  --job-file applications/jobs/{company}-{job-slug}.yaml \
  --output-dir applications/{user-slug}/{company}-{job-slug}/
```
- Uses `text_overrides` for bullet text, `summary_override` for summary, `skills_override` for skills line.
- Falls back to originals if overrides are empty.
- Save tailored `.docx` to `applications/{user-slug}/{company}-{job-slug}/resume.docx`.
- Generate PDF to the same directory.

## Cover Letter Standards

### Structure (250-400 words)

1. **Hook** (1-2 sentences) — reference specific company news/initiative + why it matters.
2. **Alignment** (2-3 sentences) — connect the user's specific experience to their needs.
3. **Value** (2-3 sentences) — what unique value the user brings (regional expertise, dual technical/business, etc.).
4. **CTA** (1-2 sentences) — specific next step, enthusiasm without desperation.

### NEVER in Cover Letters
- "I am writing to express my interest..." (generic opener)
- "I believe I would be a great fit..." (unsubstantiated)
- Repeat the entire resume in paragraph form
- Focus on what you want (job) vs what you offer (value)
- Use emojis or casual language

### ALWAYS in Cover Letters
- Reference a specific company initiative or news item
- Include at least one metric/achievement from the resume
- Mention regional expertise when relevant (per `config/user-profile.yaml`)
- Show knowledge of the company's current situation
- Keep under 400 words

### Save Location
- `applications/{user-slug}/{company}-{job-slug}/cover-letter.md`
- OR `applications/cover-letters/{company}-{job-slug}.md` for standalone drafts

## Output Directory Structure

```
applications/{user-slug}/{company}-{job-slug}/
├── resume.docx          ← Tailored Word document
├── resume.pdf           ← PDF conversion
├── cover-letter.md      ← Cover letter draft
└── tailoring-notes.md   ← Which achievements selected and why (optional)
```

## Quality Gate (MANDATORY — BLOCKING)

ALWAYS run `quality-gate.py` after generating `resume.docx`, BEFORE PDF generation:
```bash
python tools/resume-tailor/quality-gate.py \
  --resume applications/{user-slug}/{company}-{job-slug}/resume.docx \
  --job-file applications/jobs/{company}-{job-slug}.yaml
```

- **FAIL**: STOP. Fix issues in job YAML, regenerate, re-check. Never submit a FAIL resume.
- **WARN**: Flag to user, proceed if acknowledged.
- **PASS**: Continue to PDF generation and submission.

## Section Balance Rules (MANDATORY)

- **Minimum 3 bullets per company section** — exceptions only for tenures < 6 months.
- **Maximum 5 bullets per company section** — no section should dominate; distribute across companies.
- **No credential repetition** — if a certification appears in title and skills line, do NOT repeat in summary.
- **Recent roles must have enough bullets to show substantive work** — never leave a recent role at 1 bullet.
- **Career-break sections** have 0 bullets (just dates) — the only section with no minimum.

## Quality Checklist

For each tailored resume:
- [ ] Based on the correct template variant (Innovation / Delivery / Generic)
- [ ] All must-have requirements addressed
- [ ] Keywords from job posting appear naturally
- [ ] 2 pages maximum (≥16 bullets for page density)
- [ ] No fabricated achievements
- [ ] Contact info current
- [ ] **Quality gate PASS** (or WARN acknowledged by user)
- [ ] PDF generated and formatting verified
- [ ] Cover letter drafted (if required by posting)
- [ ] Files saved to correct directory

## For Complete Resume Tailoring Workflow

See `../../operating-procedures/RESUME-TAILORING-PROCEDURE-v1.md`.
