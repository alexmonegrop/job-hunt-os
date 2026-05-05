# Employer Extension Example

> **Status: stub.** The full Python implementation is deferred to Phase 4. This README documents the *pattern* so you can build your own employer extension today, even before the example code lands.

## What an Employer Extension Is

When you have a specific employer for whom you're building heavy custom artefacts — a uniquely styled resume, a deck deliverable, an engagement-tracker spreadsheet — you don't want that one-off work polluting the main system. The **employer extension pattern** is how to namespace that work cleanly.

A typical employer extension contains:
- `content.py` — employer-specific bullet rewrites, summary overrides, deck talking points (constants + small data classes).
- `render_resume.py` — employer-specific Word styling (colours, fonts, layout).
- `render_ppt.py` (or `render_deck.py`) — slide template generator if a deck deliverable is part of the application.
- `render_engagement_tracker.py` — engagement-tracker spreadsheet (xlsx).
- `README.md` — what this employer needs and how the extension delivers it.

## Why a Separate Pattern (Not Just Tools or Skills)

- The standard `resume-tailor` skill works for almost every application, but a particular employer might have:
  - Brand-strict resume formatting (specific colour palette, specific font, specific section ordering).
  - A required deck deliverable you don't want generic agent code to handle.
  - A unique engagement-tracking spreadsheet template they expect you to use during interviews.
- Forking `resume-tailor` for one employer is a maintenance burden.
- Building these as a separate, namespaced extension keeps the standard tooling clean.

## Directory Convention

```
tools/
└── employer-extension-example/         ← This stub
    ├── README.md                        ← This file
    ├── content.example.py               ← Pattern: employer-specific data
    ├── render_resume.example.py         ← Pattern: custom .docx generator
    ├── render_ppt.example.py            ← Pattern: deck generator (Phase 4)
    └── render_engagement_tracker.example.py  ← Pattern: tracker generator (Phase 4)
```

For your own extensions:
```
tools/
└── employer-extensions/
    ├── acme-consulting/                 ← Your fictional or real employer slug
    │   ├── content.py
    │   ├── render_resume.py
    │   └── README.md
    └── globex-energy/
        └── ...
```

**Critical**: never commit real employer names tied to a real person's hunt. The shipped example uses fictional employers ("ACME Consulting", "Generic Energy Co"). Your real extensions live in a private fork.

## How a Skill Calls an Employer Extension

Inside an outreach or apply workflow:

```python
# Pseudocode — what a skill would do when it detects an employer extension
import importlib

employer_slug = "acme-consulting"
extension = importlib.import_module(f"tools.employer_extensions.{employer_slug.replace('-', '_')}.content")

# Pull employer-specific overrides
custom_summary = extension.SUMMARY_OVERRIDE
custom_skills = extension.SKILLS_OVERRIDE
custom_bullets = extension.BULLET_REWRITES  # dict: bullet_id → custom text

# Run the standard resume-tailor flow with these overrides applied
```

The `apply` skill checks for `tools/employer-extensions/{slug}/` at the start of an application; if found, it routes through the extension instead of the generic `resume-tailor`.

## Pattern Documented (Phase 4 will ship the working code)

### `content.py` shape

```python
"""Employer-specific content for ACME Consulting.

This module exports constants the resume-tailor and apply skills can pull in
when an application targets ACME Consulting. Keep purely declarative — no
side effects.
"""

EMPLOYER_NAME = "ACME Consulting"
EMPLOYER_SLUG = "acme-consulting"

# Summary override (used in place of the default summary variant)
SUMMARY_OVERRIDE = """\
Senior consultant and program operator. 14 years delivering industrial
transformation engagements with a focus on multi-stakeholder regulatory
environments. Strong track record turning POCs into deployed enterprise
systems.
"""

# Skills line override
SKILLS_OVERRIDE = (
    "JIRA | SAP | SQL | AWS | Power BI | Python | Tableau | "
    "Agile/Scrum | PMP, CSPO Certified"
)

# Bullet rewrites — keyed by bullet ID from master-experience.yaml
BULLET_REWRITES = {
    "acme-01": (
        "Led $35M digital-twin engagement across 3 client sites, delivering "
        "predictive-maintenance models with 22% downtime reduction in year one."
    ),
    # ... more bullets
}

# Deck talking points (if a deck is required)
DECK_TALKING_POINTS = [
    "Why ACME Consulting in 2026: ...",
    "Three engagement priorities I'd bring: ...",
    # ...
]
```

### `render_resume.py` shape

Use `python-docx` to apply ACME-specific styling:
- Custom colour palette (set on `RGBColor` for headers).
- Custom font (Aptos / Calibri / their brand font, fallback to system default).
- Section ordering they expect (Summary → Experience → Education vs Summary → Skills → Experience).

The renderer reads from `master-experience.yaml`, applies `BULLET_REWRITES` from `content.py`, then writes to `applications/{user-slug}/{employer-slug}-{job-slug}/resume.docx`.

### `render_ppt.py` shape

Use `python-pptx` to generate a deck following ACME's slide-template conventions: section dividers, content grids, footer branding. Slides driven by the structure in `content.DECK_TALKING_POINTS`.

### `render_engagement_tracker.py` shape

Use `openpyxl` to generate a structured `.xlsx` with the columns ACME expects (engagement name, partner, target date, current status, risks, dependencies). Pre-populated with the user's pipeline data.

## When to Build an Employer Extension

✅ Build one when:
- The employer requires a specific resume style your generic templates don't match.
- The employer expects a deck or supplementary deliverable as part of the application.
- The employer has a multi-step engagement process where you'll generate similar artefacts repeatedly (5+ applications / engagements over a quarter).

❌ Don't build one when:
- It's a one-shot application — just tweak the generated resume manually.
- The customisation is small (a different summary line) — that fits in the standard `summary_override` mechanism.
- The employer is in your `excluded_companies[]` list — you shouldn't be applying anyway.

## Ship Discipline

- Never commit a real employer's brand assets (logos, brand font files, internal templates) to a public repo.
- Use placeholder colours and fonts in the example; document where to drop the real ones in the user's private fork.
- Treat employer-extension code the same as resume content — opinionated, fictional in the public template, real only in your private fork.
