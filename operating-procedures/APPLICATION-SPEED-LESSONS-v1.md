# Application Speed Lessons v1

**Document type**: Reference. For automatic enforcement, see `.claude/rules/06-application-standards.md`.

**Purpose**: bottlenecks discovered during high-volume batch application sessions and the fixes that 2x throughput.

**Companion**: `DIRECT-APPLICATION-PROCEDURE-v1.md`, `RESUME-TAILORING-PROCEDURE-v1.md`, skill `apply`.

## Overview

A batch session targeting 7+ postings revealed five systemic bottlenecks that collectively wasted 45-60 minutes per session. This doc codifies the fixes so future sessions follow the optimised workflow from the start.

- **Before optimisation**: ~3 applications per 60+ minutes
- **After optimisation**: ~5-7 applications per 45 minutes (2x throughput)

## Bottleneck 1: Dead-End Portal Checks (~30 min wasted)

### What happened
Time lost navigating company career portals that turned out to be dead ends:
- Title vs reality mismatches: e.g., "Program Manager" listed but actually an events / content / speaker role
- Location mismatches: LinkedIn says one city, portal says another (or different country / salary band)
- Expired postings: portals showing "no longer accepting applications" (often in local language)
- Wrong category: portal listings are R&D / engineering only, no PM roles exist

### The fix: 2-minute pre-check before any resume prep

Before starting resume tailoring or Playwright navigation:

1. **WebFetch the full job description first** — read the actual role, not just the title
2. **Verify the role matches expectations** — "Program Manager" can mean event coordinator
3. **Check posting age** — anything older than 1 month is likely expired for Easy Apply; older than 2 months is almost certainly dead
4. **For portal applications, WebFetch the careers page before Playwright** — quick text fetch catches "no longer accepting" or location mismatches without launching a browser

```
Pre-check sequence (per posting):
  WebFetch(job_url) → Read full JD → Confirm role match → Confirm location → Confirm open
  Time: ~2 min per posting
  Savings: prevents 5-10 min wasted per dead end
```

## Bottleneck 2: Sequential Resume Prep (~15-20 min per posting)

### What happened
Each application required three sequential steps: create the job YAML file, run `tailor-resume.py`, then run `generate-pdf.py`. Doing this one posting at a time meant 15-20 minutes per application just for materials prep.

### The fix: parallel sub-agents for ALL resume prep

Spin up one sub-agent per qualifying posting. All run simultaneously.

```
Pattern:
  Agent("Prep Company A", "Create YAML + tailor resume + generate PDF for [job details]...", subagent_type="coder")
  Agent("Prep Company B", "...", subagent_type="coder")
  Agent("Prep Company C", "...", subagent_type="coder")
```

Each sub-agent independently:
1. Creates job YAML at `applications/jobs/{company}-{job-slug}.yaml`
2. Runs `python tools/resume-tailor/tailor-resume.py --user {slug} --job-file <path> --output-dir <path>`
3. Runs quality gate (BLOCKING — must PASS)
4. Runs `python tools/resume-tailor/generate-pdf.py` to convert `.docx` → `.pdf`
5. Reports back when complete

CRITICAL: all sub-agents must use named arguments and absolute file paths.

Result: 3 postings prepped in ~90 seconds instead of 45-60 minutes.

## Bottleneck 3: LinkedIn Easy Apply Shadow DOM (~5 min per submission)

### What happened
LinkedIn Easy Apply uses a shadow DOM modal that standard Playwright selectors cannot reach. Each submission required manual discovery of the correct DOM traversal path.

### The fix: standardised shadow-DOM template

Copy-paste this pattern for every LinkedIn Easy Apply submission. No improvisation needed.

```javascript
// 1. Navigate to job posting
await page.goto('https://www.linkedin.com/jobs/view/JOBID/');

// 2. Click Easy Apply
//    MUST use JS click, not Playwright click — shadow DOM intercepts pointer events.
await page.evaluate(() => {
  const link = document.querySelector('a[aria-label="Easy Apply to this job"]');
  if (link) link.click();
});

// 3. Wait for modal in shadow DOM
await new Promise(r => setTimeout(r, 4000));

// 4. Check dialog state (headings tell you which step you're on)
const state = await page.evaluate(() => {
  const outlet = document.querySelector('#interop-outlet');
  const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
  const headings = [...dialog.querySelectorAll('h1,h2,h3')].map(h => h.textContent.trim());
  const buttons = [...dialog.querySelectorAll('button')].map(b => b.textContent.trim());
  return { headings, buttons };
});

// 5. Upload resume (when file input step appears)
const fileInput = await page.evaluateHandle(() => {
  const outlet = document.querySelector('#interop-outlet');
  const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
  return dialog.querySelector('input[type="file"]');
});
await fileInput.asElement().setInputFiles('/absolute/path/to/resume.pdf');

// 6. Click through steps (Next, Review, Submit)
await page.evaluate((btnText) => {
  const outlet = document.querySelector('#interop-outlet');
  const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
  for (const btn of dialog.querySelectorAll('button')) {
    if (btn.textContent.trim() === btnText) { btn.click(); break; }
  }
}, 'Next');

// 7. Final submit (same pattern, btnText = 'Submit application')
// ALWAYS screenshot before and after submit.
```

Key notes:
- The `#interop-outlet` element contains the shadow root for the entire Easy Apply modal.
- Standard Playwright `click()` often fails because the shadow DOM intercepts pointer events — always use `page.evaluate()` with JS click.
- Wait at least 4 seconds after clicking Easy Apply before interacting with the dialog.
- Each "Next" click may load new form fields — re-query dialog state after each step.

## Bottleneck 4: Fit Score Drift (~scored high before reading full JD)

### What happened
Initial scoring during job-discovery used only title + brief requirements summary. Full JD read later revealed mismatches:
- "Program Manager [event]": title suggested PM; full JD revealed events / content programming role. Score 8 → 5.
- Location: LinkedIn said one city; full JD revealed remote-only / different country / different salary band.

Resume prep time was wasted on roles that would have been filtered out with a full JD read.

### The fix: two-pass fit scoring

| Pass | When | Input | Purpose |
|------|------|-------|---------|
| Pass 1 (discovery) | During job search | Title + summary + location | Quick filter; drop obvious mismatches |
| Pass 2 (pre-application) | Before ANY resume prep | Full JD via WebFetch | Confirm score ≥6, verify role / location / requirements |

**Rule**: never start resume tailoring until Pass 2 confirms the score. Adds 2 minutes per posting; saves 15-20 minutes per false positive.

```
Discovery:  10 postings found, Pass 1 scores assigned
Pre-check:  WebFetch all 10 full JDs (parallel)
Pass 2:     Re-score with full JD, drop below 6
Result:     5-7 qualifying postings proceed to resume prep
Savings:    15-20 min per false positive avoided
```

## Bottleneck 5: Company Portal vs LinkedIn Mismatch

### What happened
Some companies post on LinkedIn with different location / role details than their actual career portal listings. Time spent browsing full company portals (via Playwright) looking for specific postings that either didn't exist or had different details.

### The fix: portal verification before resume prep

When DB shows `Company Website` as the `job_board`:

1. **WebFetch the specific portal URL first** — don't launch Playwright yet.
2. **Search for the exact job title** in the fetched page text.
3. **If found**: proceed with Playwright for the actual application.
4. **If not found**: fall back to LinkedIn Easy Apply immediately — don't browse the full portal.

```
Decision tree:
  job_board == "Company Website"?
    YES → WebFetch(portal_url) → Job title found?
           YES → Playwright application on portal
           NO  → Fall back to LinkedIn Easy Apply
    NO  → Proceed with LinkedIn Easy Apply directly
```

Prevents 3-5 min overhead of navigating a full career portal via Playwright only to discover the posting isn't there.

## Optimal Batch Application Workflow (Revised)

### Phase 1: Discovery and Filtering (~10 min for 10 postings)

1. Collect all candidate postings from the DB or new search results.
2. **WebFetch ALL full job descriptions in parallel** (10 simultaneous fetches).
3. Re-score each posting with full JD content (Pass 2).
4. Drop anything scoring below 5 adjusted, expired, or location-mismatched.
5. Expected yield: 10 discovered postings narrowed to 5-7 qualifying.

### Phase 2: Parallel Resume Prep (~3 min for all qualifying)

1. Spin up one sub-agent per qualifying posting.
2. Each agent: create job YAML, run `tailor-resume.py`, run quality gate, generate PDF.
3. All agents run simultaneously.
4. Expected: 5-7 tailored resumes ready in one parallel batch.

### Phase 3: Sequential Submissions (~5 min each)

Submit applications one at a time (browser constraint):
- **LinkedIn Easy Apply**: shadow-DOM pattern (Bottleneck 3 template).
- **SmartRecruiters / Greenhouse**: established Playwright patterns.
- **Company portals**: `browser_snapshot` first, then fill.
- **Screenshot before every submit**, save to `applications/tracking/`.
- Expected: 5-7 submissions in 25-35 min.

### Phase 4: Database Batch Update (~2 min)

1. `bulk_insert` all Application records in a single call.
2. `bulk_insert` all Interaction records (type `Application Submitted`) in a single call.
3. Update all Job Posting statuses to `Applied` (batch where supported).

### Total time budget

```
Phase 1:  10 min  (discovery + filtering)
Phase 2:   3 min  (parallel resume prep)
Phase 3:  30 min  (5-7 sequential submissions at ~5 min each)
Phase 4:   2 min  (DB batch updates)
─────────────────
Total:    ~45 min for 5-7 applications
```

Compared to unoptimised: ~60+ min for 3 applications.

## Key Rules for Speed

1. Never prep a resume before reading the full JD.
2. Always use parallel sub-agents for resume prep — 3-5x faster than sequential.
3. Check posting age before anything — older than 2 months on LinkedIn is almost certainly expired.
4. Portal check = 1 WebFetch, not full Playwright navigation — saves 3-5 min per dead end.
5. Batch DB updates at the end — `bulk_insert` for Applications and Interactions, not per-record.
6. LinkedIn Easy Apply pattern is standardised — no improvisation needed.
7. Two-pass fit scoring — quick filter first, full JD verification second.

## Metrics to Track

| Metric | Target | How to measure |
|--------|--------|----------------|
| Applications per hour | 4-6/hr (after ramp-up) | submissions / total session time |
| Dead-end rate | <20% of investigated postings | dead ends / total postings checked |
| Resume prep time (batch of 5) | <3 min via sub-agents | time from agent spawn to all PDFs ready |
| LinkedIn Easy Apply time | <5 min per submission | page load to confirmation screenshot |
| Pass 2 filter rate | 30-50% of Pass 1 dropped | dropped after full JD read |

## ATS-Specific Notes

### LinkedIn Easy Apply
- Shadow DOM modal via `#interop-outlet` — always use `page.evaluate()`.
- Standard Playwright `click()` fails on shadow DOM elements — JS click instead.
- Wait 4+ seconds after opening modal.
- Multi-step forms: Contact Info → Resume → Additional Questions → Review.

### SmartRecruiters
- Rejects em dashes and semicolons in text fields — sanitise before pasting.
- Phone field: must explicitly click the country-code dropdown option.
- Custom comboboxes need click-then-select pattern.

### Greenhouse.io
- Use `browser_run_code` to batch combobox selections efficiently.
- Single-page forms common, but some have multi-step wizards.

### Phenom People (and similar)
- Simple single-page forms, straightforward to automate.
- Verify location / salary band matches LinkedIn before applying.

### Company portals (general)
- Always `browser_snapshot` before filling.
- Always `browser_take_screenshot` before and after submit.
- Save screenshots to `applications/tracking/{company}-{job-slug}-{step}.png`.

## Common Dead-End Patterns

| Pattern | Example | How to detect |
|---------|---------|---------------|
| Title mismatch | "Program Manager" = events coordinator | Read full JD, check responsibilities |
| Location mismatch | LinkedIn says City A, portal says Country B | WebFetch portal listing, compare |
| Expired posting | Local-language "no longer accepting" text | Check age, scan for expiry indicators |
| R&D-only portal | All postings are researchers / engineers | WebFetch careers page, scan for PM roles |
| Salary band mismatch | US salary range on supposedly regional role | Look for compensation section |

## Checklist: Before Starting Any Application

- [ ] Full JD fetched and read (not just title / summary)
- [ ] Pass 2 fit score confirmed ≥5 (adjusted)
- [ ] Posting age verified (<2 months for LinkedIn, <1 month ideal)
- [ ] Location verified against actual JD (not just LinkedIn header)
- [ ] Role responsibilities match expectations
- [ ] If portal application: portal URL verified via WebFetch
- [ ] Resume prep assigned to sub-agent (not sequential)
