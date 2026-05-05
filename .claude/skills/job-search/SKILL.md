---
name: "job-search"
description: "Automated job discovery across Indeed, Glassdoor, LinkedIn, and regional boards using python-jobspy + Playwright LinkedIn search + WebSearch. Scores results by fit (0-10), applies adjusted-score adjustments from config/fit-score.yaml, batch-creates Job Posting records, and cross-references with existing Target Companies. Use when searching for new opportunities or running periodic sweeps."
---

# Job Search

Automated job discovery and scoring across multiple boards.

## What This Skill Does

- **Multi-board search** — Indeed, Glassdoor, LinkedIn via `python-jobspy`
- **LinkedIn Playwright search** — direct LinkedIn job search via Playwright (logged in as the active user) — supplements jobspy with real-time results, Easy Apply filtering, accurate posting data
- **LinkedIn MCP `search_jobs`** — fast URL-only discovery (no DOM parsing)
- **Regional board coverage** — additional boards via WebSearch + Playwright (configured in `config/regions.yaml` `job_boards[]`)
- **Fit scoring** — 0-10 raw score, then adjusted score per `config/fit-score.yaml`
- **Batch processing** — score all results, then bulk_insert records
- **Cross-reference** — check existing Target Companies for warm-application opportunities
- **Deduplication** — check existing Job Postings to avoid double-creating

## Prerequisites

Required:
- Python 3.10+ with `python-jobspy`
- Database access (`mcp__nocodb__*`, `${NOCODB_BASE_ID}`)
- Playwright MCP (load via ToolSearch each session — tools are deferred)
- LinkedIn MCP (optional, recommended)
- `config/fit-score.yaml`, `config/user-profile.yaml`, `config/regions.yaml`

## Quick Start

```
"Search for Program Manager jobs in [target city]"
"Find AI Product Manager roles in [target country] on Indeed and LinkedIn"
"Search for open roles at Acme Renewables, Globex Power, Initech AI"
```

## Workflow

### Step 1: Define search parameters

Gather from user or load from `config/user-profile.yaml`:
- **Keywords** — from `target_roles[]`
- **Locations** — from `target_regions[]`
- **Boards** — from `config/regions.yaml` `job_boards[]` (default: all available)
- **Distance** — radius in miles (default: 50)
- **Results per board** — default: 20

### Step 2: Execute searches in parallel

#### Source A: python-jobspy (passive — no login)

```python
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "glassdoor", "linkedin"],
    search_term="Program Manager AI",
    location="[target city, country]",
    results_wanted=20,
    country_indeed="[country]"
)
```

Known limitations:
- Glassdoor doesn't support all countries — check before searching.
- Some regional boards return 403 — fall back to WebSearch.
- Indeed in some markets is very noisy — title-filter aggressively.
- LinkedIn via jobspy is a passive scrape; may miss recent postings.

#### Source B: LinkedIn Playwright search (active — logged in)

CRITICAL: load Playwright tools first via `ToolSearch("playwright browser")`.

```
browser_navigate → https://www.linkedin.com/jobs/search/?keywords=<role>&location=<city>
```

Search-results snapshots are small (~10K chars) and contain clean job-listing data:
- Job title (link text)
- Company name
- Location + work mode (On-site / Hybrid / Remote)
- Job ID (from URL: `/jobs/view/{ID}/`)

Each `listitem` in the search-results list contains:
```yaml
- listitem:
    - link "Job Title":
        - /url: /jobs/view/JOBID/?trk=...
    - generic: Company Name
    - generic: Location (Work Mode)
```

Extract job ID with regex: `/jobs/view/(\d+)/`.

Pagination: `&start=25`, `&start=50`, etc.

Anti-loop rules:
- Search-result snapshots are small — `browser_navigate` is safe.
- NEVER use `browser_navigate` or `browser_snapshot` on individual job-detail pages (500K+ chars).
- If `browser_navigate` times out on search, retry ONCE. If it fails again, fall back to jobspy-only.
- Max 3 pages of results (start=0, 25, 50) per search — diminishing relevance after that.

Easy Apply filter: add `&f_AL=true` to URL.

#### Source C: LinkedIn MCP `search_jobs` (fast, no DOM parsing)

```javascript
mcp__linkedin__search_jobs({
  keywords: "Program Manager",
  location: "[target city]",
  limit: 25
})
// Returns: { job_urls: ["https://www.linkedin.com/jobs/view/<id>/", ...], count: N }
```

Strengths: fast, returns clean URLs, no snapshot issues.
Limitations: URL-only (no titles/companies/descriptions). Cross-reference with Source B or WebFetch.
Note: `get_job_details` returns mostly null fields — unreliable for metadata.

#### Source D: WebSearch (regional boards)

```
WebSearch "site:[regional board] [role] [region] <current year>"
```

### Step 3: Deduplicate across sources

Merge results from Sources A-D:
- Match by job ID (LinkedIn) or by `(company, title)` cross-board.
- Prefer LinkedIn Playwright data (most accurate, real-time).
- Flag duplicates found across sources.

### Step 4: Score results

Calculate **raw fit score** (0-10) per `config/fit-score.yaml` `raw_criteria[]`:

| Criteria | Points | How to Assess |
|----------|--------|---------------|
| Role Alignment | 0-3 | Posting role vs `target_roles[]` |
| Region Expansion Signal | 0-2 | Company expanding in `target_regions[]` |
| Industry Match | 0-2 | Posting industry vs `target_industries[]` |
| Seniority Fit | 0-1 | Senior / Director / VP level |
| Geography Match | 0-1 | Based in target region or remote-friendly |
| Existing Contact Bonus | 0-1 | Company already in `target_companies` |

### Step 4b: Calculate adjusted score (MANDATORY)

Apply penalties + bonuses from `config/fit-score.yaml` (`penalties[]`, `bonuses[]`).

The agent reads the actual values from config — DO NOT hardcode.

**Adjusted Score = Raw Score + Bonuses − Penalties** (floor at 0).

### Step 4c: Apply adjusted-score thresholds

| Adjusted Score | Action | Protocol |
|----------------|--------|----------|
| 7+ | Full | Tailored resume + cover letter + portal-first |
| 5-6 | Longshot | Easy Apply only, generic template, no cover letter, tag "LONGSHOT" |
| 3-4 | Skip (unless user overrides) | Present to user with reasoning |
| <3 | Auto-skip | No DB record needed |

ALWAYS present both raw and adjusted scores in the summary.

### Step 5: Cross-reference Target Companies

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  query: "Company Name"
})
```

Flag results where:
- Company exists → "Warm Application" opportunity
- Company has existing networking contacts → prioritise

### Step 6: Batch-create Job Posting records

Create all qualifying records (**adjusted ≥ 5**) via `bulk_insert`. Tag longshots (5-6) with "LONGSHOT" in notes:

```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  records: [
    {
      job_title: "...",
      company_name: "Acme Renewables",
      company_id: 159,
      job_board: "LinkedIn",
      job_url: "https://www.linkedin.com/jobs/view/<id>/",
      location: "[city, country]",
      fit_score: 8,
      status: "New",
      discovered_date: "2026-MM-DD",
      user_id: ${ACTIVE_USER_ID}
    },
    // ... all qualifying postings
  ]
})
```

### Step 7: Report summary

Output a summary table with BOTH scores:

```
| # | Company | Job Title | Source | Raw | Adj | Protocol | Easy Apply? | Warm? | Status  |
|---|---------|-----------|--------|-----|-----|----------|-------------|-------|---------|
| 1 | Acme    | Sr PM     | Indeed | 8   | 9   | Full     | No          | Yes   | Created |
| 2 | Globex  | AI PM     | LI PW  | 7   | 9   | Full     | Yes         | No    | Created |
| 3 | Initech | PM        | LI PW  | 6   | 3   | Skip     | Yes         | No    | Skipped |
| 4 | MBB Co  | Consultant| LI PW  | 7   | 5   | Longshot | Yes         | No    | Created |
```

Protocol column: Full (7+), Longshot (5-6), Skip (3-4), Auto-skip (<3).

## Search Templates

These are illustrative — generate actual queries from `config/user-profile.yaml` `target_roles[]` × `target_regions[]`.

```python
search_term = "Program Manager"
locations = ["[target city 1]", "[target city 2]"]
```

```python
search_term = "AI Product Manager"
# OR: "ML Product", "AI Strategy", "AI Program Manager"
```

```python
search_term = "Digital Transformation Director"
# OR: "DT Manager", "Innovation Director"
```

```python
search_term = "Operations Director"
# OR: "Delivery Manager", "PMO Director"
```

## LinkedIn Search URL Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `keywords` | Search terms | `Program%20Manager` |
| `location` | Location filter | `[city]` |
| `start` | Pagination offset | `0`, `25`, `50` |
| `f_AL` | Easy Apply only | `true` |
| `f_TPR` | Time posted | `r86400` (24h), `r604800` (week), `r2592000` (month) |
| `f_E` | Experience level | `4` (mid-senior), `5` (director) |
| `f_JT` | Job type | `F` (full-time), `C` (contract) |

## Rules

1. **ALWAYS score before creating records** — no unscored postings in the database.
2. **ALWAYS cross-reference Target Companies** — flag warm opportunities.
3. **ALWAYS check for duplicate postings** before creating records.
4. **ALWAYS use multiple sources** — jobspy + LinkedIn Playwright/MCP + WebSearch (use at least 2).
5. **NEVER use `browser_snapshot` on individual LinkedIn job pages** — 500K+ chars, causes loops.
6. **Batch-create all records** via `bulk_insert`.
7. **Include the current year and prior year** in search queries.
8. **Max 2 retries on any Playwright action** — if it fails twice, fall back to jobspy-only.
9. **Load Playwright tools via ToolSearch** at start of every session (deferred tools).
10. **ALWAYS present both raw and adjusted scores** in summary tables.
