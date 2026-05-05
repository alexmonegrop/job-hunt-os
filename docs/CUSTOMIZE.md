# Customize

What each config knob actually controls. Read this when you're setting up your own profile or wondering "where do I change X?".

## Where things live

| File | What it controls | Loaded by |
|------|------------------|-----------|
| `.env` | Secrets, DB connection, active user, optional API keys | All skills, all tools |
| `config/user-profile.yaml` | Identity, target roles / regions / industries, credibility anchors, excluded companies, work auth, resume variants | All skills |
| `config/fit-score.yaml` | Raw scoring criteria, penalties, bonuses, thresholds | `job-search`, `apply` |
| `config/industries.yaml` | Canonical industry vocabulary + insight seeds per industry | `cold-outreach`, `contact-population`, target_companies dropdown |
| `config/regions.yaml` | Region presets (cities, languages, flagship buyers, job boards, dynamics) | `cold-outreach`, `meeting-prep`, `job-search` |
| `applications/resumes/data/{slug}/master-experience.yaml` | Every job, achievement, metric, tag | `resume-tailor`, `cold-outreach` (3-element formula) |
| `applications/resumes/data/{slug}/skills-inventory.yaml` | Technical / management / industry / geographic skills | `resume-tailor` (`skills_override`) |
| `applications/resumes/data/{slug}/standard-answers.yaml` | Form auto-fill data + common screening Q&A | `apply` |
| `applications/resumes/data/{slug}/user-config.yaml` | Per-user resume variants, template mapping, gap-analysis-driven adjustments, tailoring notes | `resume-tailor` |
| `applications/resumes/data/{slug}/gap-analysis.yaml` | Fillable / hard / certification gaps + reframe rules | `resume-tailor`, `apply` |

## Common customisations

### "I want to target a different region"

Edit `config/user-profile.yaml`:
```yaml
home_region: "Your home region"
target_regions: ["Region A", "Region B"]
target_cities: ["City 1", "City 2", "City 3"]
```

Then add a region preset in `config/regions.yaml` for each new region:
```yaml
regions:
  - name: "Region A"
    countries: [...]
    primary_cities: [...]
    languages_required: [...]
    flagship_buyers: [...]
    job_boards: [...]
    typical_dynamics: [...]
```

The `cold-outreach`, `contact-population`, and `meeting-prep` skills will adapt.

### "I want to add or change industries"

Edit `config/user-profile.yaml`:
```yaml
target_industries: ["AI/ML Enterprise Software", "Energy Tech", "<your new industry>"]
```

Then add the industry to `config/industries.yaml` if it isn't already there:
```yaml
industries:
  - name: "<your new industry>"
    keywords: [...]
    typical_roles: [...]

insight_seeds:
  "<your new industry>":
    - "[counter-intuitive insight 1]"
    - "[counter-intuitive insight 2]"
```

### "I want different fit-score adjustments"

Open `config/fit-score.yaml`. Change the `penalties[]` and `bonuses[]` lists. The agent reads them at scoring time — no skill / rule changes needed.

If your adjustments are user-specific (not global to your fit profile), add them to `applications/resumes/data/{slug}/user-config.yaml` instead — the agent merges per-user adjustments with global config at scoring time.

Example:
```yaml
# config/fit-score.yaml — global
bonuses:
  - condition: "Native to target region or building regional practice"
    points: +1

# user-config.yaml — user-specific
fit_score_adjustments:
  bonuses:
    - condition: "Energy or industrial transformation focus"
      points: +1
      rationale: "User's strongest domain"
```

### "I want to exclude certain companies"

Edit `config/user-profile.yaml`:
```yaml
excluded_companies:
  - name: "Globex Power"
    reason: "Existing networking relationship — coordinate with [contact] first"
  - name: "Initech AI"
    reason: "Former employer"
```

The agent will refuse to apply without your explicit approval. See `06-application-standards.md` BLOCKED COMPANIES.

### "I want to change message tone / structure"

Edit `.claude/rules/02-message-quality-standards.md`. Word counts, formula, tone rules all live there.

If your changes are radical (e.g., you want LinkedIn voice messages, not text), it might be cleaner to fork a new skill — see [`EXTEND.md`](EXTEND.md).

### "I want to change resume variants"

Edit `applications/resumes/data/{slug}/user-config.yaml`:
```yaml
resume:
  variants:
    - name: "Custom"
      description: "Your description"
      source_file: "applications/resumes/source/{slug}/{slug}-resume-custom.docx"
  template_mapping:
    "Some Role Category": "Custom"
```

Drop your new `.docx` template into `applications/resumes/source/{slug}/`. The `resume-tailor` skill picks it up automatically.

### "I want different blocked / nice-to-have penalties"

Run through your gap analysis (`/onboard-user` Phase 5) — it produces `applications/resumes/data/{slug}/gap-analysis.yaml` with hard / fillable / certification gaps. Update its `fit_score_adjustments` block; the agent merges into scoring.

### "I want to use Postgres directly instead of NocoDB"

The schema is reusable. Re-implement the database MCP under a different prefix (`mcp__postgres__` or similar), set `NOCODB_MCP_PREFIX` in `.env` to your new prefix, and update `.claude/rules/01-database-standards.md` examples (the rule is named "database-standards" not "nocodb-standards" precisely so it can be re-targeted).

You'll also need to re-implement the v3 Link API pattern (`01-database-standards.md` Rule 8) if your backend has equivalent system-managed FK columns.

## What to NOT customise

- **Rule files (`.claude/rules/`)** — these are intentionally backend-agnostic and personal-data-free. If you find yourself wanting to add real values into a rule, that value belongs in `config/` instead.
- **Skill descriptions (frontmatter `description:`)** — the agent reads these to decide which skill to invoke. Changing them changes which queries trigger which skill.
- **Operating procedures (`operating-procedures/`)** — these are reference docs; the source of truth for behaviour is the rules + skills.

## Multi-user customisation

If you operate the system on behalf of multiple people: see [`MULTI-USER.md`](MULTI-USER.md).

## Tooling customisation

Coming in Phase 4:
- Resume tailoring algorithm (scoring weights, bullet-rewrite prompts) — `tools/resume-tailor/format-config.yaml`.
- Job-search defaults — `tools/job-search/defaults.yaml`.
- Mock-interview personas — `tools/interview/contexts/`.
