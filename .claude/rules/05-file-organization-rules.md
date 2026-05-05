# File Organization Rules

## CRITICAL: ONE FILE PER PERSON

**NEVER** create batch files containing multiple messages.
**ALWAYS** create individual files for each contact.

**Why**: Individual files enable proper tracking, easy finding, and professional organization.

## Directory Structure

```
job-hunt-os/                            ← repo root
├── applications/                       ← Per-user application outputs (gitignored at user level)
│   ├── {user-slug}/                   ← e.g., jane-demo/
│   │   └── {company}-{job-slug}/
│   │       ├── resume.docx
│   │       ├── resume.pdf
│   │       └── cover-letter.md
│   ├── jobs/                          ← Captured job postings (shared)
│   ├── tracking/                      ← Application screenshots
│   ├── cover-letters/                 ← Standalone cover letter drafts
│   └── resumes/
│       ├── source/                    ← Master .docx files (READ-ONLY)
│       └── data/                      ← Per-user YAML source data
│           ├── _template/             ← Annotated template YAMLs (shipped with repo)
│           ├── jane-demo/             ← Demo user (shipped with repo)
│           └── {user-slug}/           ← Real users (gitignored)
│
├── interviews/                         ← Per-user interview prep by company
│   └── {user-slug}/
│       └── {company}/                  ← prep.md, mock-questions.md, deep-dives
│
├── outreach/                           ← Per-user networking
│   └── {user-slug}/
│       ├── messages/                   ← Individual message files (ONE PER PERSON)
│       ├── prep/                       ← Networking MEETING prep (NOT interview prep)
│       ├── calls/                      ← Video recordings + transcripts
│       ├── analysis/                   ← Post-meeting analysis
│       └── sessions/                   ← Session notes
│
├── research/                           ← Per-user market/company research
│   └── {user-slug}/
│       └── {topic}-{focus}.md
│
├── plans/                              ← Strategic planning documents
│   ├── EXAMPLES/                       ← Walkthroughs (Jane Demo)
│   └── archive/                        ← Session summaries
│
├── reference-files/                    ← Resumes, templates, examples
├── operating-procedures/               ← Methodology documentation
├── config/                             ← User-specific config (yaml)
├── .claude/{rules,skills}/             ← Auto-loaded rules and skills
├── docs/                               ← Setup, architecture, customisation docs
└── tools/                              ← Utility scripts (resume-tailor, job-search, interview, ...)
```

## File Naming Conventions

### Outreach Messages (CRITICAL)

**Location**: `outreach/{user-slug}/messages/`
**Format**: `[company-name]-[firstname-lastname].md`

Examples:
- `acme-renewables-jane-smith.md`
- `globex-power-bob-jones.md`

Wrong:
- `batch-2026-MM-DD-outreach-messages.md` (never batch files!)
- `ACME_contacts.md` (not individual)
- `acme-messages.md` (not specific person)
- `Jane Smith - Acme.md` (wrong order, spaces)

**Naming rules**:
- Lowercase with hyphens
- Company name first
- First name, then last name
- No spaces
- `.md` extension

### Job Posting Files (Direct Application Workstream)

**Location**: `applications/jobs/`
**Format**: `[company-name]-[job-slug].md` (or `.yaml`)

Examples:
- `acme-renewables-senior-program-manager.md`
- `globex-power-product-manager-region.md`

Wrong:
- `Acme - Senior PM.md` (spaces, not lowercase)
- `job-posting-1.md` (no company/role info)

### Tailored Resume Directories

**Location**: `applications/{user-slug}/`
**Format**: `[company-name]-[job-slug]/` (directory)

Contents per directory:
- `resume.docx` — tailored Word document
- `resume.pdf` — PDF conversion
- `cover-letter.md` — cover letter draft
- `tailoring-notes.md` — which achievements were selected and why (optional)

### Application Tracking Screenshots

**Location**: `applications/tracking/`
**Format**: `[company-name]-[job-slug]-[step].png`

Examples:
- `acme-renewables-senior-pm-pre-submit.png`
- `acme-renewables-senior-pm-confirmation.png`

### Interview Prep (separate from networking prep)

**Location**: `interviews/{user-slug}/{company-name}/`
**Files per company**: `prep.md`, `mock-questions.md`, optional deep-dives.

Examples:
- `interviews/jane-demo/acme-renewables/prep.md`
- `interviews/jane-demo/acme-renewables/mock-questions.md`
- `interviews/jane-demo/acme-renewables/product-deep-dive.md`

**NOT in `outreach/prep/`** — `outreach/prep/` is for networking meeting prep only (not formal interviews).

### Networking Meeting Prep Documents

**Location**: `outreach/{user-slug}/prep/`
**Format**: `[company-name]-[person-name]-prep.md`

Example: `acme-renewables-jane-smith-prep.md`

### Meeting Analysis

**Location**: `outreach/{user-slug}/calls/` or `outreach/{user-slug}/analysis/`
**Format**: `[contact-name]-meeting-analysis.md`

Examples:
- `jane-smith-meeting-analysis.md`
- `bob-jones-end-to-end-analysis.md`

Video files:
- `jane-smith-2026-MM-DD.mp4`
- `jane-smith-transcript.txt`

### Planning Documents

**Location**: `plans/[YYYY-MMM-DD]/`
**Format**: `[descriptive-name].md`

Examples:
- `plans/2026Mar03/quarterly-outreach-plan.md`
- `plans/2026Mar03/RESTART-INSTRUCTIONS.md`

**Why date folders**: easy to find plans by time period; natural chronological organization.

### Research Documents

**Location**: `research/{user-slug}/`
**Format**: `[topic]-[focus].md`

Examples:
- `research/jane-demo/regional-market-research.md`
- `research/jane-demo/acme-renewables-bd-prospects.md`

## NEVER Save to Repo Root

ALWAYS organize files in appropriate subdirectories.

Never:
- `job-hunt-os/test.md`
- `job-hunt-os/working-file.txt`
- `job-hunt-os/batch-messages.md`
- `job-hunt-os/temp.md`

Always:
- `outreach/{user-slug}/messages/company-person.md`
- `research/{user-slug}/company-analysis.md`
- `plans/2026Mar03/implementation-plan.md`

## Message File Structure (REQUIRED)

Each outreach message file MUST include this structure (template):

```markdown
# Message Draft: [Full Name] - [Company]

**Contact**: [Full Name]
**Title**: [Job Title]
**Company**: [Company Name]
**LinkedIn**: [LinkedIn URL]
**Priority**: [Primary/Secondary/Backup]
**Date Drafted**: [YYYY-MM-DD]

---

## Why This Person:
[3-5 sentences explaining why this specific person — 3-element formula]

---

## Email Subject Line:
```
[Primary subject line]
```

**Alternative Subject Lines**:
- "[Alternative 1]"
- "[Alternative 2]"

---

## Message Draft ([word count] words):

```
[Full message text — 70-90 words]
```

---

## Personalization Elements:
- [Element 1]
- [Element 2]
- [Element 3]

---

## Connection Points:
- [Point 1]: [Explanation]
- [Point 2]: [Explanation]
- [Point 3]: [Explanation]

---

## Follow-Up Strategy (if no response):

### Follow-Up #1 (After 5-7 business days):
```
[Follow-up message 1]
```

### Follow-Up #2 (After additional 7-10 business days):
```
[Follow-up message 2]
```

---

## Next Steps After Positive Response:
1. [Research item 1]
2. [Research item 2]
3. Prepare questions about: [topics]
4. Prepare STAR stories about: [topics]

---

**Status**: Draft Ready for Review
**Next Action**: [Next action]
```

## File Quality Checklist

For each outreach message file created:
- [ ] Named correctly: `company-firstname-lastname.md`
- [ ] Contains full structure (all required sections above)
- [ ] Message is 70-90 words (verified count)
- [ ] Includes personalized unique insight
- [ ] Has follow-up strategies
- [ ] Includes next steps for positive response
- [ ] Saved to correct location: `outreach/{user-slug}/messages/`

## Archive Strategy

- **Sent messages**: Move to `outreach/{user-slug}/messages/sent/[YYYY-MM]/`. Keep drafts in `messages/`.
- **Completed meetings**: Move video to `outreach/{user-slug}/calls/archive/[YYYY-MM]/`. Keep analysis in `outreach/{user-slug}/analysis/`.

## Batch Processing File Creation

When processing 15 contacts:
1. Draft all messages in a single session.
2. Create 15 individual files (not 1 batch file).
3. Use consistent formatting across all files.
4. Each file must be complete and stand-alone.
5. Files can reference batch date in Notes section.

Correct:
```javascript
[Single session — creates 15 individual files]:
Write("outreach/{user-slug}/messages/acme-jane-smith.md")
Write("outreach/{user-slug}/messages/acme-bob-jones.md")
// ...15 individual files
```

NOT: `Write("outreach/{user-slug}/messages/batch-2026-MM-DD-all-messages.md")`

## Git and Version Control

Commit messages for outreach files:
- "Add outreach messages for Acme Renewables (3 contacts)"
- "Add meeting prep for Jane Smith - Acme Renewables"

NOT: "Add files"

Gitignore (already in repo `.gitignore`):
- `applications/{slug}/`, `interviews/{slug}/`, `outreach/{slug}/`, `research/{slug}/` (per-user content; only `_template/` and `jane-demo/` are tracked)
- `*.mp4`, `*.mov` (large video files)
- `**/archive/` (archived materials)
- `applications/resumes/source/` (master .docx — read-only, gitignored)

## For Complete File Organization Guidance

See `../../operating-procedures/`:
- `OUTREACH-OPERATING-PROCEDURE-v4.md` (Step 7: File Creation — ONE FILE PER PERSON)
- `contact-population-plan-v3.md` (file naming conventions section)
