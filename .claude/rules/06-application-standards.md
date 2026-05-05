# Application Standards

## BLOCKED COMPANIES — NEVER APPLY WITHOUT EXPLICIT USER APPROVAL

**Read the active user's blocked-company list from `config/user-profile.yaml` (`excluded_companies[]`).**

Any company in that list requires the user's explicit approval BEFORE any application action. This includes:
- Re-opening Withdrawn postings
- Submitting applications (portal, Easy Apply, or any method)
- Tailoring resumes for these companies
- Creating application records

**Typical reasons a company gets onto this list**:
- The user has an existing networking relationship there (any application activity must be coordinated with the relationship).
- The user is a former employee — sensitive relationship.
- The user has personal/strategic reasons to opt out.

**Enforcement**:
1. ALWAYS check `excluded_companies[]` BEFORE applying to ANY company.
2. If a job posting has status `Withdrawn`, NEVER re-open or re-apply without explicit user approval.
3. Violation of this rule damages real professional relationships — treat it as the highest-priority rule in this file.

## NEVER Reuse Another Company's Tailored Resume

Each application MUST use a resume specifically tailored for that job posting. The tailored resume path must match the target company and role:
```
applications/{user-slug}/{company}-{job-slug}/resume.pdf
```

If no tailored resume exists, create one first using the `resume-tailor` skill. NEVER proceed with the application until the tailored resume is generated.

Using a resume tailored for a different company/role is a process violation — the resume contains keywords, bullet rewrites, and summary overrides specific to the original job, not the one being applied to. This rule has the same severity as the Blocked Companies rule above.

**Validation**: Before uploading any resume file to any form, verify the file path contains the target company name. If it doesn't match, STOP.

## Base Configuration

- **Database**: NocoDB (default — see `01-database-standards.md` for details and `.env` for credentials)
- **Job Postings table**: `job_postings`
- **Applications table**: `applications`
- The base ID, URL and token are env vars (`${NOCODB_BASE_ID}`, `${NOCODB_URL}`, `${NOCODB_API_TOKEN}`)

## Fit Score Calculation (MANDATORY before applying)

Score each posting 0-10 using the **weighted criteria defined in `config/fit-score.yaml`**.

The default scoring matrix (read from `config/fit-score.yaml` `raw_criteria[]`):

| Criteria | Points | Description |
|----------|--------|-------------|
| Role Alignment | 0-3 | User's `target_roles[]` match to posting |
| Region Expansion Signal | 0-2 | Company actively expanding in user's `target_regions[]` |
| Industry Match | 0-2 | Posting's industry is in user's `target_industries[]` |
| Seniority Fit | 0-1 | Senior / Director / VP level (not junior, not C-suite at mega-corp) |
| Geography Match | 0-1 | Based in target region or remote-friendly |
| Existing Contact Bonus | 0-1 | Company already in Target Companies with networking contacts |

**Raw threshold**: Score ≥ 6 proceeds to adjusted scoring. Score 4-5 reviews with user. Below 4 skips.

## Adjusted Score Calculation (MANDATORY — Applied After Raw Score)

After calculating the raw fit score, apply adjustments from `config/fit-score.yaml` (`penalties[]` and `bonuses[]`).

The defaults (illustrative — customise to your gap analysis):

**Penalties (subtract from raw score)**:
| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Role type the user has explicitly identified as a hard gap | -3 | Hard gap (e.g., pure B2C if user has no B2C experience) |
| Top-tier consulting at Manager+ level (if user has no consulting tenure) | -2 | Hard gap |
| Specific degree explicitly required that user lacks | -2 | Hard gap |
| Required language the user doesn't speak | -3 | Hard gap |
| Same language "nice to have" / "preferred" | -1 | Soft gap |
| MBA explicitly required (if user lacks one) | -2 | Soft gap |
| MBA "preferred" / "nice to have" | -1 | Soft gap |

**Bonuses (add to raw score)**:
| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Company native to user's target region OR building a regional practice | +1 | Sweet spot |
| Role values breadth over domain depth | +1 | Sweet spot if user has multi-industry background |
| Startup / scaleup (<500 employees) | +1 | Sweet spot if user has founder mindset |
| Independent consulting engagement model | +1 | Matches consulting tenure if user has it |

**Adjusted Score = Raw Score + Bonuses − Penalties** (floor at 0)

**The agent MUST read the actual values from `config/fit-score.yaml`** — the table above is documentation of the *shape*, not the *values*.

## Adjusted Score Thresholds (REPLACES raw threshold above)

| Adjusted Score | Protocol | Action |
|----------------|----------|--------|
| 7+ | **Full** | Full resume tailoring + cover letter + apply via company portal first |
| 5-6 | **Longshot** | Easy Apply only, generic template, no cover letter. Tag "LONGSHOT" in notes |
| 3-4 | **Skip** | Do not apply unless user explicitly overrides |
| <3 | **Auto-skip** | NEVER apply. No database record needed |

These thresholds can be overridden in `config/fit-score.yaml` (`thresholds:` map).

## Longshot Protocol Definition

For adjusted score 5-6 postings:
- **Application method**: Easy Apply ONLY (no portal hunting)
- **Resume**: Closest generic template variant (Innovation / Delivery / Generic). NO full tailoring.
- **Cover letter**: None
- **DB notes**: Tag with "LONGSHOT" and adjusted score
- **Follow-up**: None unless employer responds first
- **Priority**: Apply AFTER all 7+ postings are processed

## Job Posting Required Fields

- **company_name** — REQUIRED. Plain text (e.g., "Acme Renewables"). Used for dedup. ALWAYS populate.
- **job_title** — Exact title from posting
- **company_id** — FK to `target_companies` (populate when company exists)
- **job_board** — Select: LinkedIn / Indeed / Glassdoor / [your regional boards] / Company Website
- **job_url** — Direct link
- **location** — City, Country
- **remote_status** — On-site / Hybrid / Remote
- **posted_date**, **discovered_date** — ISO dates
- **job_description**, **key_requirements** — Long text
- **role_category** — Select from `config/user-profile.yaml` `target_roles[]`
- **fit_score** — 1-10
- **fit_analysis** — Brief explanation
- **status** — New / Reviewing / Applying / Applied / Interview / Rejected / Withdrawn / Expired
- **resume_version_used** — File path
- **notes** — Additional context

## Application Required Fields

- **application_name** — `{Company} - {Job Title}`
- **job_posting_id** — FK to `job_postings`
- **company_id** — FK to `target_companies`
- **application_date** — ISO date
- **application_method** — Direct / Easy Apply / Company Portal / Recruiter / Referral
- **resume_version** — Path to tailored resume used
- **cover_letter** — Boolean
- **application_status** — Preparing / Submitted / Acknowledged / Screening / Interview Scheduled / Interview Completed / Offer / Rejected / Withdrawn
- **response_date** — When company responded
- **networking_contact_id** — FK to `target_contacts` (if warm)
- **pipeline_entry_id** — FK to `sales_pipeline` (if warm)
- **follow_up_date** — Next follow-up due
- **notes** — Additional context

## Application Status Progression

```
Preparing → Submitted → Acknowledged → Screening → Interview Scheduled → Interview Completed → Offer
                                                                                              → Rejected
                                                                                              → Withdrawn
```

## Follow-Up Timing Rules

- **First follow-up**: 7 business days after submission (if no response)
- **Second follow-up**: 14 business days after first follow-up
- **After second follow-up**: Mark as "No Response" and move on
- **Exception**: If a networking contact exists, follow up through them instead

## Duplicate Detection (MANDATORY — BEFORE Every Application)

BEFORE creating a Job Posting record OR submitting any application:

### Step 1: Check by company name (PRIMARY)
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  where: "(company_name,like,%CompanyName%)",
  fields: "id,job_title,company_name,status",
  limit: 10
})
```

### Step 2: Check by job title (SECONDARY)
```javascript
// Catch variants (e.g., "Senior PM" vs "Sr. Project Manager")
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  where: "(job_title,like,%keyword%)",
  fields: "id,job_title,company_name,status",
  limit: 10
})
```

### Step 3: Evaluate
- **Same company + same/similar title** → DUPLICATE. Do NOT apply again.
- **Same company + different title** → OK (different role).
- **Same company + status `Applied`** → Already applied to a role there. Note in new posting.
- **No results** → New company; safe to proceed.

### CRITICAL: Never use `search_records` for dedup

`search_records` only indexes the primary display column (`job_title`). It does NOT search `company_name`, `notes`, or other text fields. Always use `list_records` with a `where` filter for reliable dedup.

### When creating Job Posting records

ALWAYS include `company_name` as a plain-text field:
```javascript
mcp__nocodb__insert_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  data: {
    "company_name": "Acme Renewables",   // REQUIRED for dedup
    "job_title": "Senior Program Manager",
    "job_board": "Indeed",
    // ...
  }
})
```

## Cross-Workstream Check (MANDATORY)

BEFORE creating a Job Posting record:
1. Search Target Companies for an existing company record.
2. If exists: link to it and check for existing networking contacts.
3. If networking contacts exist: flag as **"Warm Application"**.
4. Warm Application strategy: reach out to the contact BEFORE or simultaneously with the application.

BEFORE applying at a networked company:
1. Check Sales Pipeline for existing entries.
2. If a pipeline entry exists with temperature > Cold: mention the contact in the cover letter.
3. Consider reaching out to the contact with "I noticed you're hiring for X..." message.

## Application Channel Priority (CRITICAL — ALWAYS FOLLOW)

**Company Career Portal FIRST. LinkedIn Easy Apply is the LAST resort.**

Easy Apply has a LOWER success rate than direct portal applications. For EVERY job posting:

1. **Identify company name** from the LinkedIn posting.
2. **WebSearch `"{company}" careers page`** or check their website.
3. **If portal exists** → navigate to portal, find the same role, apply via Playwright form automation.
4. **If portal broken / role not listed on portal** → fall back to Easy Apply.
5. **"Confidential" postings** → Easy Apply is the only option (no company to search).

**Why**: Direct portal applications are taken more seriously by hiring teams. Easy Apply floods recruiters with low-effort applications. Portal applications show genuine interest.

**NEVER skip the portal check.** Even if Easy Apply is available, check the portal first.

## Playwright Automation Rules

### Non-LinkedIn (Indeed, Glassdoor, Company Portals, regional boards)

ALWAYS:
- `browser_snapshot` before filling any form (understand structure first)
- `browser_take_screenshot` before clicking submit (user confirms)
- `browser_take_screenshot` after submission (proof of submission)
- Save screenshots to `applications/tracking/`

NEVER:
- Auto-submit without user confirmation screenshot
- Fill forms without reading the full form first
- Upload files without verifying the correct file path

### LinkedIn Easy Apply (FALLBACK ONLY — User-Authorized)

Easy Apply is AUTHORIZED for auto-submit but is the LAST RESORT:
1. Discover posting on LinkedIn.
2. **First**: WebSearch company careers page → apply via portal if available.
3. **Only if no portal**: Use Easy Apply via shadow-DOM automation (see the `apply` skill).
4. Update the database after submission.

### Application Package (for portal applications)

Save to `applications/jobs/{company}-{job-slug}.md`:
- Direct link to LinkedIn posting
- Company careers portal URL
- Tailored resume path
- Cover letter text (ready to paste)
- Key points for "Additional Information" field
- Talking points if "Why interested?" question
- Standard answers for common form questions (read from `applications/resumes/data/{user-slug}/standard-answers.yaml`)

## Job Search Batch Patterns

### Running a Job Search Session

```javascript
// 1. Search across multiple boards in parallel
JobSpy search "Program Manager [target city 1]"
JobSpy search "AI Product Manager [target country]"
WebSearch "site:[regional board] program manager [region]"

// 2. Score ALL results before creating records
// Calculate Fit Score for each posting

// 3. Batch-create Job Posting records (adjusted score >= 5 only)
// Single message with all create_record calls

// 4. Cross-reference with Target Companies
// Single batch query to check existing companies
```

### Duplicate Detection (always before bulk insert)

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  where: "(company_name,like,%CompanyName%)",
  limit: 10
})
```

## Job Board Coverage

The `tools/job-search/` JobSpy wrapper supports the major boards. Add regional boards in `config/regions.yaml` (`job_boards[]`).

| Board | Method | Notes |
|-------|--------|-------|
| Indeed | JobSpy | Direct support |
| Glassdoor | JobSpy | Direct support |
| LinkedIn Jobs | JobSpy | Passive search (no login needed) |
| Bayt.com | JobSpy | GCC market |
| NaukriGulf | JobSpy | Via Naukri integration |
| GulfTalent / regional boards | WebSearch + Playwright | `site:{board}` + scrape if needed |
| Company career pages | Playwright snapshot | For target companies already in DB |

## Interaction Types for Applications

When creating Interaction records for application activities:
- `Application Submitted` — when application is sent
- `Application Follow-Up` — when following up
- `Resume Tailored` — when resume version created for specific posting
- `Job Posting Saved` — when interesting posting is saved for review

## For Complete Workflows

See `../../operating-procedures/`:
- `DIRECT-APPLICATION-PROCEDURE-v1.md` (full application workflow)
- `RESUME-TAILORING-PROCEDURE-v1.md` (resume customisation reference)
- `APPLICATION-SPEED-LESSONS-v1.md` (lessons from high-volume application sessions)
