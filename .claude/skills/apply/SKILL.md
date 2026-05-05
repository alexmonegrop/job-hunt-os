---
name: "apply"
description: "End-to-end application workflow: resume tailoring, cover letter drafting, form submission via Playwright (non-LinkedIn) or LinkedIn Easy Apply automation via browser_run_code shadow DOM pattern, database record creation. Screenshots before submission."
---

# Apply

End-to-end job application workflow with Playwright automation for ALL platforms including LinkedIn Easy Apply.

## What This Skill Does

- **Resume tailoring** — calls the `resume-tailor` skill to create role-specific version
- **Cover letter drafting** — 250-400 word cover letter with company-specific hook
- **Non-LinkedIn automation** — Playwright form filling for Indeed, Glassdoor, company portals
- **LinkedIn Easy Apply automation** — Playwright via `browser_run_code` with shadow-DOM pattern (user-authorized)
- **Screenshot verification** — captures pre-submit screenshot
- **Database integration** — creates Application + Interaction records
- **Cross-workstream** — links to existing networking contacts when available

## Prerequisites

Required:
- Playwright MCP (load via `ToolSearch("playwright browser")` each session)
- Tailored resume (generated via `resume-tailor` skill)
- Job Posting record in the database
- `applications/resumes/data/{user-slug}/standard-answers.yaml`
- `applications/resumes/data/{user-slug}/user-config.yaml`
- **Multi-user**: resolve paths using the active user's slug (`JOB_HUNT_USER`).

## Quick Start

```
"Apply to the Senior Program Manager role at Acme Renewables (Job Posting record exists)"
"Apply to my top 5 scored job postings"
```

## Workflow

### Step 0: Adjusted-score check (MANDATORY — BEFORE EVERYTHING)

Check the Job Posting's adjusted score:
1. **Adjusted ≥ 7** → full protocol: tailored resume + cover letter + portal-first
2. **Adjusted 5-6** → longshot protocol: Easy Apply only, closest generic template, NO cover letter, NO portal hunt. Tag "LONGSHOT" in notes.
3. **Adjusted 3-4** → STOP. Confirm with user before proceeding.
4. **Adjusted <3** → DO NOT APPLY. Inform user and skip.

If the Job Posting has no adjusted score, calculate it first using the scoring table in the `job-search` skill (which reads `config/fit-score.yaml`).

### Step 0b: Resume-tailoring gate (MANDATORY — NEVER SKIP)

**Before ANY application action** (form filling, Easy Apply, portal submission, resume upload):

For full protocol (adjusted 7+):
1. Determine expected tailored resume path: `applications/{user-slug}/{company}-{job-slug}/resume.pdf`
2. Check if that file exists for THIS EXACT job posting.
3. **If YES** → proceed to Step 1.
4. **If NO** → STOP. Run `/resume-tailor` for this posting first. Create job YAML, run scoring, rewrite bullets, generate `.docx` and `.pdf`. Only then proceed.

For longshot protocol (adjusted 5-6):
1. Use the closest matching generic template (Innovation / Delivery / Generic) — no full tailoring.
2. Still verify the resume path is a valid generic template, not another company's tailored resume.

**HARD RULES**:
- NEVER upload a resume tailored for Company A to an application for Company B.
- NEVER substitute a "closest match" tailored resume. Each tailored resume contains JD-specific keyword mirroring.
- Before uploading ANY resume, verify the file path contains the target company name OR is a generic template.
- For batch applications: apply to adjusted-7+ first (full protocol), then 5-6 (longshot). Don't interleave.
- Tailor ALL 7+ resumes first, THEN apply all. Don't interleave "apply with whatever is available".

### For non-LinkedIn applications (Indeed, Glassdoor, company portals, regional boards)

#### Step 1: Prepare materials
1. Read Job Posting record from the database.
2. Verify tailored resume exists (Step 0 gate).
3. Draft cover letter if required.
4. Load `standard-answers.yaml` for form fields.

#### Step 2: Navigate
```
browser_navigate → application URL
```

#### Step 3: Understand form
```
browser_snapshot → capture form structure
```

#### Step 4: Fill form
```
browser_fill_form → populate fields with prepared data
```
For each field:
- Name / email / phone → `standard-answers.yaml` `personal` section
- Experience / years → `standard-answers.yaml` `experience` section
- Custom questions → match to `common_questions` patterns

#### Step 5: Upload resume
```
browser_file_upload → upload tailored resume (.pdf or .docx as required)
```

#### Step 6: Screenshot before submit
```
browser_take_screenshot → applications/tracking/{company}-{job}-pre-submit.png
```

#### Step 7: Submit
```
browser_click → submit
browser_take_screenshot → applications/tracking/{company}-{job}-confirmation.png
```

#### Step 8: Create database records
- Create Application record (status: `Submitted`)
- Create Interaction record (type: `Application Submitted`)
- Update Job Posting status to `Applied`

### For LinkedIn Easy Apply (automated — user-authorized)

#### Step 1: Prepare materials
1. Read Job Posting record — get the LinkedIn job ID.
2. Generate / confirm tailored resume PDF.
3. Note the resume file path for upload.

#### Step 2: Navigate to job posting
```
browser_navigate → https://www.linkedin.com/jobs/view/{JOBID}/
```

WARNING: do NOT use `browser_snapshot` on LinkedIn job-detail pages — 500K+ chars, causes loops.

If `browser_navigate` times out on the snapshot, that's OK — the page is loaded. Proceed with `browser_run_code`.

#### Step 3: Open Easy Apply modal and complete form

Use a SINGLE `browser_run_code` call to handle the entire flow:

```javascript
async (page) => {
  // Click Easy Apply — MUST use JS click (shadow DOM blocks pointer events).
  await page.evaluate(() => {
    const btn = document.querySelector('button.jobs-apply-button') ||
                document.querySelector('[aria-label*="Easy Apply"]') ||
                document.querySelector('a[aria-label*="Easy Apply"]');
    if (btn) btn.click();
  });

  await page.waitForTimeout(4000);

  // All Easy Apply modal content lives inside #interop-outlet shadow DOM.
  const getDialogState = async () => {
    return await page.evaluate(() => {
      const outlet = document.querySelector('#interop-outlet');
      if (!outlet?.shadowRoot) return { error: 'No shadow root' };
      const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
      if (!dialog) return { error: 'No dialog' };
      const headings = [...dialog.querySelectorAll('h1,h2,h3')].map(h => h.textContent.trim());
      const buttons = [...dialog.querySelectorAll('button')].map(b => b.textContent.trim());
      const labels = [...dialog.querySelectorAll('label')].map(l => l.textContent.trim());
      const selects = [...dialog.querySelectorAll('select')].map(s => ({
        label: s.closest('.fb-dash-form-element')?.querySelector('label')?.textContent?.trim(),
        options: [...s.options].map(o => o.text)
      }));
      return { headings, buttons, labels, selects };
    });
  };

  const clickButton = async (btnText) => {
    await page.evaluate((text) => {
      const outlet = document.querySelector('#interop-outlet');
      const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
      for (const btn of dialog.querySelectorAll('button')) {
        if (btn.textContent.trim() === text) { btn.click(); break; }
      }
    }, btnText);
    await page.waitForTimeout(2000);
  };

  let state = await getDialogState();
  const steps = [];

  for (let step = 0; step < 8; step++) {
    state = await getDialogState();
    steps.push(state.headings);

    if (state.buttons.includes('Submit application')) {
      return JSON.stringify({ status: 'ready_to_submit', steps, state });
    }

    if (state.headings.some(h => h.includes('Resume'))) {
      const fileInput = await page.evaluateHandle(() => {
        const outlet = document.querySelector('#interop-outlet');
        const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
        return dialog.querySelector('input[type="file"]');
      });
      if (fileInput.asElement()) {
        await fileInput.asElement().setInputFiles('RESUME_PATH_HERE');
        await page.waitForTimeout(2000);
      }
    }

    if (state.buttons.includes('Next')) {
      await clickButton('Next');
    } else if (state.buttons.includes('Review')) {
      await clickButton('Review');
    } else {
      break;
    }
  }

  return JSON.stringify({ status: 'navigated', steps, finalState: state });
}
```

CRITICAL:
- Replace `RESUME_PATH_HERE` with the actual absolute path to the tailored PDF.
- The function navigates through all steps and stops at "Submit application".
- Take a screenshot BEFORE calling submit.
- Then call submit in a separate `browser_run_code`.

#### Step 4: Screenshot before submit
```
browser_take_screenshot → applications/tracking/{company}-{job}-pre-submit.png
```

#### Step 5: Submit
```javascript
async (page) => {
  await page.evaluate(() => {
    const outlet = document.querySelector('#interop-outlet');
    const dialog = outlet.shadowRoot.querySelector('[role="dialog"]');
    for (const btn of dialog.querySelectorAll('button')) {
      if (btn.textContent.trim() === 'Submit application') { btn.click(); break; }
    }
  });
  await page.waitForTimeout(3000);

  const result = await page.evaluate(() => {
    const outlet = document.querySelector('#interop-outlet');
    const dialog = outlet?.shadowRoot?.querySelector('[role="dialog"]');
    const text = dialog?.textContent || document.body.textContent.substring(0, 500);
    const success = text.includes('Application submitted') || text.includes('applied');
    return { success, text: text.substring(0, 200) };
  });

  await page.goto('about:blank');
  return JSON.stringify(result);
}
```

#### Step 6: Post-submit screenshot + database records
```
browser_take_screenshot → confirmation
```
- Create Application record (status: `Submitted`, method: `Easy Apply`).
- Create Interaction record (type: `Application Submitted`).
- Update Job Posting status to `Applied`.

## Standard Answers

The agent reads `applications/resumes/data/{user-slug}/standard-answers.yaml` for form fields. The schema includes:
- `personal`: name, email, phone, location, linkedin
- `experience`: years_total, current_title, current_company
- `work_authorisation`: status, sponsorship_required (boolean)
- `availability`: start_date, willing_to_relocate (regions)
- `certifications[]`
- `languages[]`
- `common_questions`: question → answer pairs for typical screening questions

DO NOT hardcode standard answers in this skill — they're per-user.

## Cross-Workstream Integration

Before applying:
1. Does the company exist in `target_companies`? → link.
2. Does the company have networking contacts? → flag as "Warm Application".
3. Is there an active Sales Pipeline entry? → mention in cover letter.
4. Should the user reach out to the contact first? → recommend if temperature > Cold.

## Anti-Loop Rules (CRITICAL)

1. **NEVER use `browser_snapshot` on LinkedIn job-detail pages** — context overflow + retry loops.
2. **NEVER use `browser_navigate` to LinkedIn job pages expecting a usable snapshot** — it will timeout or return massive data.
3. **ALWAYS use `browser_run_code` with `page.evaluate()` for ALL LinkedIn interactions** — bypasses shadow DOM, returns only what you extract.
4. **If `browser_navigate` times out on LinkedIn**, the page is probably loaded — proceed with `browser_run_code`.
5. **Max 2 retries on any single Playwright action** — if it fails twice, the approach is wrong. Stop and try a different strategy.
6. **If Easy Apply modal doesn't appear after 2 attempts**, the posting may not have Easy Apply. Flag as manual and move on.
7. **After completing an Easy Apply submission, navigate to `about:blank`** — prevents stale LinkedIn DOM bloating subsequent operations.

## ATS-Specific Patterns

These are observed patterns. Add new ones as you encounter them; keep them generic.

### SmartRecruiters
- Rejects em-dashes and semicolons in text fields — sanitise before pasting.
- Phone field: must explicitly click the country-code dropdown option.

### Greenhouse.io
- Use `browser_run_code` to batch combobox selections efficiently.

### Phenom People
- Simple single-page forms, straightforward to automate.

### Oracle HCM
- Comboboxes use `[role="gridcell"]`; citizenship uses nationality names (e.g., "Canadian").

### Company portals (general)
- Always `browser_snapshot` before filling.
- Always `browser_take_screenshot` before and after submit.
- Save all screenshots to `applications/tracking/{company}-{job-slug}-{step}.png`.

## Rules

1. **LinkedIn Easy Apply is AUTHORIZED for auto-submit** — use the shadow-DOM pattern above.
2. **ALWAYS screenshot before submission** on all platforms.
3. **ALWAYS check for warm-application opportunity** before applying.
4. **ALWAYS create both Application + Interaction records** after submission.
5. **NEVER retry the same failing Playwright action more than twice** — change approach.
6. **Save all screenshots** to `applications/tracking/`.
7. **Parallel resume prep via sub-agents** for batch applications (3-5x faster).
