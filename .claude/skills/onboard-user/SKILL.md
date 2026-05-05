---
name: "onboard-user"
description: "Onboard a new person to the job-hunt system: intake resumes, run initial job search, build role profiles, extract experience from resumes, gap-analyse against market demands, and interview for missing info. Creates a complete user profile ready for applications."
user_invocable: true
---

# Onboard New User

End-to-end automated onboarding that takes a person from "I have a resume" to "ready to apply".

## What This Skill Does

Transforms raw resume inputs into a fully populated job-hunt profile through 8 phases:

0. **Environment Setup** — Clone repo, configure `.env`, install MCPs, verify connectivity (first time only)
1. **Intake** — Collect basic info + resume files
2. **Job Search** — Find real postings matching their target roles/market
3. **Role Profiles** — Synthesise what the market actually demands from those postings
4. **Resume Extraction** — Parse resumes into structured YAML (`master-experience`, `skills-inventory`)
5. **Gap Analysis** — Compare extracted experience vs role-profile requirements
6. **Interview** — Ask targeted questions to fill gaps the resumes don't cover
7. **Finalise** — Save config, summarise, list initial scored postings

## Workflow

### Phase 0: Environment setup (15-30 min, first time only)

Run when the user is on a NEW machine. Skip if already configured.

#### Prerequisites
- **Claude Code** installed
- **Python 3.10+** with pip
- **Docker Desktop** (for LinkedIn MCP)
- **Git** installed

#### Step 0.1: Clone the repo

```bash
git clone https://github.com/<your-org>/job-hunt-os.git
cd job-hunt-os
```

The repo contains all skills, rules, scripts, templates, and shared data.

#### Step 0.2: Install Python dependencies

```bash
pip install python-docx pyyaml docx2pdf python-jobspy fpdf2
```

#### Step 0.3: Set up `.env`

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
# Edit .env in your editor
```

Key variables (see `.env.example` for the full list and `docs/SETUP.md` for how to obtain each):

```
# Database (NocoDB self-hosted by default)
NOCODB_URL=http://localhost:8080
NOCODB_API_TOKEN=<your token from NocoDB Account → Tokens>
NOCODB_BASE_ID=<set after running tools/setup/init-nocodb.py>
NOCODB_MCP_PREFIX=mcp__nocodb__

# Active user
JOB_HUNT_USER=<your-slug>

# GitHub (optional, for repo sync)
GITHUB_PAT=<your PAT, scope: repo>

# OpenRouter / LLM (optional, for tools that call out to a model)
OPENROUTER_API_KEY=<your key>
```

#### Step 0.4: Configure MCP servers

Edit `~/.claude.json` and add the MCP server entries you need under `projects > <path-to-job-hunt-os> > mcpServers`. Examples:

```json
{
  "projects": {
    "<path-to-job-hunt-os>": {
      "mcpServers": {
        "nocodb": {
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-nocodb"],
          "env": {
            "NOCODB_BASE_URL": "http://localhost:8080",
            "NOCODB_API_TOKEN": "<your token>"
          }
        },
        "context7": {
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-context7"]
        },
        "playwright": {
          "command": "npx",
          "args": ["-y", "@anthropic/mcp-playwright"]
        },
        "linkedin": {
          "command": "docker",
          "args": ["run", "-i", "--rm",
            "-e", "LINKEDIN_SESSION_COOKIE=<your li_at cookie>",
            "ghcr.io/anthropic/mcp-linkedin:latest"
          ]
        }
      }
    }
  }
}
```

Notes per MCP:

- **NocoDB**: each user has their own self-hosted NocoDB instance by default (via `infrastructure/docker-compose.yml`). The token is per-instance.
- **Context7**: free documentation lookup, no auth.
- **Playwright**: each user needs their own installation. CRITICAL — close all Chrome instances before launching Claude Code (Playwright tools register at startup). Install: `npx playwright install chromium`.
- **LinkedIn**: each user MUST use their own `li_at` session cookie (using someone else's will get the account flagged). Requires Docker running. Cookie expires periodically.

How to get your LinkedIn `li_at`:
1. Log in to LinkedIn in Chrome.
2. DevTools (F12) → Application → Cookies → `linkedin.com`.
3. Copy the value of `li_at`.

#### Step 0.5: Initialise the database schema

Run:
```bash
python tools/setup/init-nocodb.py
```

This creates the 7 tables (`users`, `target_companies`, `target_contacts`, `sales_pipeline`, `interactions`, `job_postings`, `applications`), discovers link-field IDs, and writes them to `.env` (`NOCODB_BASE_ID` and link-field IDs).

#### Step 0.6: Verify connectivity

Launch Claude Code in the `job-hunt-os` directory and run `/session-start`. The MCP status table will show which services are connected.

If any fail, troubleshoot per `docs/SETUP.md` "Troubleshooting" section.

#### Step 0.7: Configure local git

```bash
git config user.name "<Your Full Name>"
git config user.email "<your email>"
```

This is repo-local only.

---

### Phase 1: Intake (~5 min)

Gather basic info via `AskUserQuestion`:

- **Q1**: name, email, phone, LinkedIn URL, location
- **Q2**: target roles (free text — e.g., "Software Engineering Manager", "Data Science Lead")
- **Q3**: target markets / cities, remote preference
- **Q4**: industries to specifically want or avoid

Then:
1. Generate a slug from the name (e.g., "Jane Doe" → "jane").
2. Create the database user record:
```javascript
mcp__nocodb__insert_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "users",
  data: {
    full_name: "<name>",
    slug: "<slug>",
    email: "<email>",
    phone: "<phone>",
    linkedin: "<url>",
    location: "<location>",
    target_roles: "<roles>",
    notes: "Onboarded <date>. Markets: <Q3>. Industries: <Q4>."
  }
})
```
3. Create the per-user directory structure:
```
applications/resumes/data/{slug}/
applications/resumes/source/{slug}/
applications/{slug}/
applications/jobs/{slug}/
applications/cover-letters/{slug}/
applications/tracking/{slug}/
outreach/{slug}/messages/
outreach/{slug}/prep/
interviews/{slug}/
research/{slug}/
```
4. Set `JOB_HUNT_USER={slug}` in `.env`.
5. Ask the user to provide their resume(s):
   - "Please share your resume file(s). Drop them into chat or tell me the file path."
   - Accept PDF, DOCX, or plain text.
   - Save originals to `applications/resumes/source/{slug}/`.
   - Multiple resumes (e.g., technical vs management) — save all; they represent different angles.

### Phase 2: Initial job search (~10 min)

Using target roles + markets from Phase 1, run a broad job search:

1. **Construct 4-6 search queries** from `target_roles[]` × `target_regions[]`.
2. **Capture 15-25 job postings** — for each extract:
   - Job title, company, key requirements (must-haves), nice-to-haves, industry keywords, seniority level.
3. **Save raw postings** to `applications/jobs/{slug}/` as YAML.
4. Do NOT score or filter yet — we need the full spread to build role profiles.

### Phase 3: Build role profiles (~10 min)

Synthesise the 15-25 postings into 2-4 role profiles.

For each role category:
1. Count frequency of each requirement across postings.
2. Rank requirements by frequency (top 10-15 = "market demands this").
3. Identify the standard toolkit — tools / platforms / certifications in 50%+ of postings.
4. Note differentiators — requirements that appear in top postings but not all.

Save to `applications/resumes/data/{slug}/role-profiles.yaml`:
```yaml
role_profiles:
  - name: "Software Engineering Manager"
    postings_analyzed: 8
    must_have_skills:
      - "5+ years engineering management" (8/8 postings)
      - "Agile/Scrum leadership" (7/8)
      - "System design" (6/8)
    common_tools:
      - "JIRA" (7/8)
      - "GitHub" (6/8)
      - "AWS/GCP" (5/8)
    differentiators:
      - "ML/AI experience" (3/8)
    typical_seniority: "Senior Manager / Director"
    typical_team_size: "8-25 direct/indirect"
```

Present the profiles: "Based on 25 postings, here's what the market demands. Does this look right?"

### Phase 4: Resume extraction (~15 min)

Read the user's resume(s) and extract structured data into:

**`applications/resumes/data/{slug}/master-experience.yaml`**:
1. Contact info — name, location, phone, email, linkedin
2. Summary — 2-3 variants matching their role profiles
3. Experience — for each role: company, title, location, dates, achievement bullets (preserve exact wording), tags, metrics, functional_areas, better_for/avoid_for, priority (10 = flagship, 5 = filler), variant tags
4. Education — degrees, institutions, dates
5. Certifications — name, issuer, date

**`applications/resumes/data/{slug}/skills-inventory.yaml`**:
- Technical skills with role_relevance tags
- Management skills with evidence
- Industry knowledge with depth ratings
- Geographic expertise

**`applications/resumes/data/{slug}/standard-answers.yaml`**:
- Personal info for form auto-fill
- Professional details (years experience, current title)
- `common_questions` and `screening_patterns` left as TBD (filled in interview)

**`applications/resumes/data/{slug}/user-config.yaml`**:
- Pre-populate from Phase 1 intake
- `gap_analysis` section empty (filled in Phase 5)

Save all to `applications/resumes/data/{slug}/`.

### Phase 5: Gap analysis (~10 min)

Compare extracted resume data (Phase 4) against role profiles (Phase 3).

For each role profile, check every must-have requirement:
- **COVERED**: clear evidence (specific bullet, metric, or skill)
- **PARTIAL**: hinted at but not explicit
- **GAP**: no evidence

Build the gap matrix and categorise:
- **Fillable gaps** — user probably HAS this experience but didn't put it on their resume (interview question needed)
- **Hard gaps** — user genuinely doesn't have this (note for fit-scoring penalties)
- **Certification gaps** — missing cert that could be obtained (note as nice-to-have)

Save to `applications/resumes/data/{slug}/gap-analysis.yaml`:
```yaml
fillable_gaps:
  - requirement: "Budget management experience"
    appears_in: ["SEM", "PM"]
    frequency: "6/15 postings"
    interview_question: "Have you managed budgets in any of your roles? Even informal P&L ownership counts."

hard_gaps:
  - requirement: "PhD in Computer Science"
    appears_in: ["ML Research Lead"]
    frequency: "3/15 postings"
    impact: "Cannot fill — adjust scoring"

fit_score_adjustments:
  penalties:
    - condition: "PhD required"
      points: -3
  bonuses:
    - condition: "Startup experience valued"
      points: +1
```

These adjustments feed into `config/fit-score.yaml` (or are merged at scoring time — see `06-application-standards.md`).

### Phase 6: User interview (~15-30 min)

For each fillable gap, ask the user a targeted question via `AskUserQuestion`.

Approach:
- 3-5 questions at a time (batched).
- Frame to elicit specific, metric-rich answers.
- Avoid yes/no — ask "tell me about a time when…" / "what was the scope of…".

Question format:
```
"X% of your target postings require [REQUIREMENT]. Your resume doesn't mention this explicitly.

Have you done any of the following?
- [Specific scenario A]
- [Specific scenario B]
- [Specific scenario C]

If yes, give me details: company, what you did, scope/metrics, outcome."
```

After each answer:
1. Relevant experience → create new achievement entries in `master-experience.yaml`.
2. Partial experience → add as a bullet with lower priority.
3. Confirmed gap → move from `fillable_gaps` to `hard_gaps`.
4. Update `user-config.yaml` `fit_score_adjustments` based on confirmed hard gaps.

Continue until all fillable gaps are addressed or the user says "that's enough for now".

### Phase 7: Finalise (~5 min)

1. Update `user-config.yaml` with finalized gap analysis and fit-score adjustments.
2. Create `role-type-schemas.yaml` for the user (which bullets prefer/deprioritise per role).
3. Summary to user:
   - "Profile set up with X achievement bullets across Y roles."
   - "N role profiles matching M postings found."
   - "Ready to start tailoring resumes and applying."
   - "Z postings from the initial search scored 7+ — start with those?"
4. Save initial job postings to the database (now scored with finalised fit criteria).

## Rules

1. **NEVER fabricate achievements** — only add bullets the user explicitly confirms.
2. **Preserve resume wording** — when extracting, keep their language. Rewriting happens at tailoring time.
3. **Save frequently** — write YAML files after each phase, don't wait until the end.
4. **Phase 2 is broad on purpose** — diverse postings → accurate role profiles.
5. **Interview questions must be specific** — "Have you managed budgets?" is bad. "In your role at [Company], what was the budget you were responsible for?" is good.
6. **Batch operations** — use `bulk_insert` for DB records, parallel `WebSearch` for job searches.
7. **Include `user_id`** on all DB records created during onboarding.
8. **The user's slug** is used everywhere — directory names, DB queries, script flags.
9. **Never write a real `li_at` cookie or PAT into a tracked file.** Only `.env` (gitignored).

## Time Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| 0. Environment Setup | 15-30 min | First time only |
| 1. Intake | 5 min | Info + resumes |
| 2. Job Search | 10 min | Automated WebSearch |
| 3. Role Profiles | 10 min | Analysis + confirmation |
| 4. Resume Extraction | 15 min | Parsing + structuring |
| 5. Gap Analysis | 10 min | Comparison + categorisation |
| 6. Interview | 15-30 min | Depends on gap count |
| 7. Finalise | 5 min | Save + summarise |
| **Total (first time)** | **~90-120 min** | Includes env setup |
| **Total (returning)** | **~60-90 min** | Skip Phase 0 |

## Triggering This Skill

- From `/session-start` when user selects "New user (onboard someone new)".
- Directly via `/onboard-user`.
- Can be resumed mid-phase if a session is interrupted (phases save state to disk).
