# Database Standards

This file describes the **default backend (NocoDB self-hosted)** and the schema/conventions the rules and skills assume. The schema can be re-implemented on Postgres, Airtable, or another tool — adjust the MCP tool prefix and field names accordingly.

## Base Configuration (read from `.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NOCODB_BASE_ID` | Base ID for the JobHunt base (returned by `tools/setup/init-nocodb.py`) | (set during init) |
| `NOCODB_URL` | NocoDB instance URL | `http://localhost:8080` |
| `NOCODB_API_TOKEN` | API token from NocoDB Account → Tokens | (set by user) |
| `NOCODB_MCP_PREFIX` | Tool prefix used in skills (e.g., `mcp__nocodb__`) | `mcp__nocodb__` |

The agent reads these at runtime. **Never hardcode them in rules, skills, or tools.**

## Tables (used in data operations)

| Table | Purpose |
|-------|---------|
| `users` | Multi-user support — each person has a `user_id` |
| `target_companies` | Companies of interest (networking + direct application) |
| `target_contacts` | People at target companies |
| `sales_pipeline` | Outreach pipeline entries (one per contact you're actively pursuing) |
| `interactions` | Audit log of every touch (message drafted, sent, replied, meeting, etc.) |
| `job_postings` | Captured job listings |
| `applications` | Submitted applications |

The init script (`tools/setup/init-nocodb.py`) creates the schema and writes the table IDs and link-field IDs into `.env` (or a local config file). Rules and skills reference tables **by name**, not by ID.

## Multi-User: `user_id` Field

All 6 data tables (everything except `users`) have a `user_id` column (Number, default 1).

- The active user slug is set by `JOB_HUNT_USER` in `.env`.
- The user record's numeric `user_id` is looked up at session start by the `session-start` skill.
- When creating records, ALWAYS include `user_id` for the active user.
- When querying, add `(user_id,eq,X)` to filter by user.
- The `users` table has: `full_name`, `slug`, `email`, `phone`, `linkedin`, `location`, `target_roles`, `notes`.
- Per-user YAML files: `applications/resumes/data/{slug}/master-experience.yaml`.

For single-user setups, `JOB_HUNT_USER` defaults to the only user and `user_id=1` is implicit.

## CRITICAL WORKFLOW RULES

### Rule 0: ALWAYS Check Existing Target Contacts First

**BEFORE researching new contacts for a company**:

1. **Search `target_contacts`** for existing contacts at that company.
2. Use `search_records` with the company name.
3. **Review existing contacts** for quality and relevance.
4. **Only research new contacts** if:
   - Existing contacts are insufficient quality
   - More contacts are needed to reach the target (9-10 per company)
   - A specific role/expertise is not covered

**Why**: Prevents duplicate research, wastes time, and shows lack of awareness of existing data.

```javascript
// CORRECT: Check existing first
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})
// Review results, then decide if new research is needed.

// WRONG: Researching new contacts without checking existing.
```

### Rule 1: Update Target Companies BEFORE Adding Contacts

ALWAYS populate the Target Companies record before adding any contacts:

1. Research the company's target-region expansion (3-4 WebSearch queries).
2. Update `why_strong_fit` (3-element formula — see Rule 4).
3. Update `recent_signals` (date-specific announcements).
4. THEN proceed to add contacts.

**Why**: Contact `why_right_person` entries depend on company context.

### Rule 2: Create Pipeline + Interaction Records Together

ALWAYS create both records when adding to the sales pipeline:

1. Create the Sales Pipeline record first.
2. Capture the returned record ID (numeric, e.g., `159`).
3. Create the Interaction record immediately after.
4. Link using `pipeline_entry_id` (numeric FK).

**Why**: Maintains bidirectional tracking and prevents orphaned records.

### Rule 3: Required Fields (NEVER Skip)

#### `target_companies`
- `company_name` — display name
- `why_strong_fit` — 3-element formula (user's background + company target-region context + strategic alignment)
- `recent_signals` — date-specific expansions/announcements (Month YYYY format)
- `industry` — pulled from `config/industries.yaml` dropdown
- `hq_location` — City, Country
- `tier` — priority level (see Rule 11)
- `research_date` — ISO format (YYYY-MM-DD)

#### `target_contacts`
- `full_name`
- `title_role`
- `linkedin_profile`
- `company_id` — numeric FK to `target_companies`
- `why_right_person` — 3-element formula (CRITICAL — see Rule 4)
- `contact_source` — default `LinkedIn`
- `contact_priority` — Primary / Secondary / Backup
- `added_date` — ISO

#### `sales_pipeline`
- `pipeline_name` — `[Contact Name] - [Company]`
- `contact_id` — numeric FK to `target_contacts`
- `company_id` — numeric FK to `target_companies`
- `pipeline_stage` — default `1. Research`
- `temperature` — default `Cold`
- `notes` — batch date and key hook

#### `interactions`
- `interaction_type` — e.g., `Message Drafted`
- `interaction_date` — ISO timestamp
- `target_contact_id` — numeric FK
- `pipeline_entry_id` — numeric FK
- `interaction_summary` — brief description
- `subject_topic` — message subject line
- `details` — additional context

### Rule 4: 3-Element Formula for `why_right_person` (MANDATORY)

MUST connect ALL THREE elements (3-5 sentences minimum):

#### 1. The user's specific relevant experience
Reference SPECIFIC role/achievement from the user's resume (read `applications/resumes/data/{user-slug}/master-experience.yaml` and `config/user-profile.yaml` `credibility_anchors[]`):
- `"<user>'s <role at Company X> overseeing $<N>M+ initiatives with <flagship client>..."`
- `"<user>'s <count>x AI/ML startup founder experience (<Startup A>, <Startup B>)..."`
- `"<user>'s robotics deployment background (<Company A>, <Company B>)..."`
- `"<user>'s <certification> and digital-transformation expertise..."`

#### 2. The company's target-region expansion context
Reference a specific expansion from the Target Companies research:
- Include dates and scale: `"during <Company>'s <region> expansion to 40-50 employees"`
- Reference key partnerships: `"managing <flagship contract> ($30M+)"`
- Reference strategic moves: `"as they establish <city> manufacturing"`
- Use Recent Signals data: `"following their <date> announcement"`

#### 3. The contact's role relevance
Explain why THIS specific role matters:
- Why the role is critical for the company's regional expansion
- How the role connects to the user's background
- What insights/opportunities the contact represents
- Geographic alignment (e.g., `"BASED IN <target city>"`)

**Example format** (fictional, illustrative):
```
Program Manager BASED IN <target city> — the most directly relevant contact for
<Company>'s <region> expansion. <Contact name> manages regional program delivery
exactly where the user is located and where <Company> is doubling operations. The
user's <role at past company> overseeing $10M+ initiatives with <flagship client>
provides peer-level credibility for discussing regional program-management challenges.
Both are PMP-aligned professionals managing large-scale technical deployments in
industrial settings. <Contact>'s on-ground experience with <flagship contract>
benefits from the user's <flagship client> partnership insights and understanding of
regional client expectations. PERFECT FIT: <Contact> leads programs in the exact
market the user knows deeply, during <Company>'s aggressive expansion phase requiring
local market expertise and operational scaling knowledge.
```

**Priority-specific guidelines**:
- **Primary contacts** (C-level, Directors, VPs): emphasize strategic alignment, decision-making authority, the user's executive/founder credibility.
- **Secondary contacts** (Managers, Engineers): emphasize technical/operational alignment, peer-level relevance, team insights.

### Rule 5: Batch Duplicate Checking

ALWAYS check for duplicates in batch (single query, not individual):

For 15 contacts, use ONE query with OR filter:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  where: "(pipeline_name,like,%Contact1 Name%)~or(pipeline_name,like,%Contact2 Name%)~or(pipeline_name,like,%Contact3 Name%)",
  limit: 20
})
```

Benefits: 1 API call vs 15, faster execution, easier to review.

For Job Postings dedup (CRITICAL — prevent double-applying):
```javascript
// ALWAYS use list_records with where filter on company_name — NOT search_records
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  where: "(company_name,like,%CompanyName%)",
  fields: "id,job_title,company_name,status",
  limit: 10
})
```

**WARNING**: `search_records` does NOT search the `company_name` field (it only indexes `job_title`). NEVER use `search_records` for job-posting dedup.

### Rule 6: Token Limit Management

ALWAYS use `search_records` for `target_contacts` (not unfiltered `list_records`):
- The Target Contacts table can grow to 500+ records — too large for unfiltered `list_records`.
- Search by company name to find specific contacts.
- Use `list_records` with a `where` filter or `limit` for controlled queries.

```javascript
// CORRECT
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})

// ALSO CORRECT: list_records with filter
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  where: "(company_id,eq,159)",
  limit: 25
})

// WRONG — will exceed token limits
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts"
})
```

## NocoDB MCP Tool Usage (CRITICAL)

### Rule 7: Creating Records — No Character Limit

NocoDB has no 500-char limit per field. Include all fields (long text included) in a single `insert_record`.

**Single record**:
```javascript
mcp__nocodb__insert_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  data: {
    "company_name": "Acme Renewables",
    "industry": "Energy Tech",
    "hq_location": "Northgate, Demoland",
    "tier": "Tier 2 - High Priority",
    "research_date": "2026-MM-DD",
    "employee_count": 500,
    "why_strong_fit": "[long text]",
    "recent_signals": "[long text]"
  }
})
```

**Multiple records (use `bulk_insert`)**:
```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  records: [
    { "full_name": "Contact 1", "title_role": "Director", "company_id": 159 },
    { "full_name": "Contact 2", "title_role": "VP", "company_id": 159 },
    { "full_name": "Contact 3", "title_role": "Manager", "company_id": 159 }
  ]
})
```

For very large batches (15+ records with long text), consider splitting into 2-3 `bulk_insert` calls to avoid request timeouts.

### Rule 8: Correct Parameter Names

MUST use snake_case parameters (NocoDB convention):
- `base_id` (not `baseId`)
- `table_name` (used for data ops)
- `table_id` (used ONLY for schema operations: `get_table_info`, `add_column`, `list_views`)
- `data` (for `insert_record`, not `fields`)
- `records` (array for `bulk_insert`)
- `record_id` (for update/delete, not `id`)
- `query` (for `search_records`, not `searchTerm`)
- `where` (for filtering, not `filterByFormula`)
- `limit` (not `maxRecords`)

NocoDB uses **snake_case field names** (Postgres column names), not display-name style:
- `company_name` (not `Company Name`)
- `why_strong_fit` (not `Why Strong Fit`)
- `linkedin_profile` (not `LinkedIn Profile`)

When unsure of a field name, use `get_table_info` (with the table ID, not name) to check the schema.

## Foreign Key Linking Format (CRITICAL)

NocoDB uses **numeric foreign-key fields** instead of linked-record arrays.

Pattern: the FK field is named `{related_table}_id` and takes a **numeric** record ID.

```javascript
// CORRECT
"company_id": 159
"contact_id": 42
"pipeline_entry_id": 87
"target_contact_id": 42
"job_posting_id": 15

// WRONG (Airtable-style)
"Company": ["recXXXXXXXXXXXX"]
"Contact": ["recXXXXXXXXXXXX"]
```

**Finding record IDs**: use `search_records` or `list_records` to look up the numeric ID before linking.

### CRITICAL: Setting Links on System FK Columns

Some FK columns are SYSTEM-MANAGED (uidt: `ForeignKey`) and CANNOT be set via `insert_record` or `update_record`. The MCP `update_record` will return success but silently fail to set the link.

Use the v3 Link API instead:
```bash
# POST ${NOCODB_URL}/api/v3/data/${NOCODB_BASE_ID}/{tableId}/links/{linkFieldId}/{recordId}
curl -s -X POST "${NOCODB_URL}/api/v3/data/${NOCODB_BASE_ID}/{tableId}/links/{linkFieldId}/{recordId}" \
  -H "Content-Type: application/json" \
  -H "xc-token: ${NOCODB_API_TOKEN}" \
  -d '[{"id": "TARGET_RECORD_ID"}]'
```

**Link Field IDs** (LinkToAnotherRecord fields that control the system FK) — discovered by `tools/setup/init-nocodb.py` and stored in `.env` or `config/.nocodb-link-fields.yaml`:
- `JOB_POSTINGS_TO_TARGET_COMPANIES_LINK`
- `APPLICATIONS_TO_TARGET_COMPANIES_LINK`
- `APPLICATIONS_TO_JOB_POSTINGS_LINK`

IMPORTANT:
- Body is an **array** of objects: `[{"id": "211"}]` (string ID).
- Existing links are preserved — new links are added, not replaced.
- Setting the Link field automatically populates the system FK column (e.g., setting the `target_companies` link auto-sets `company_id`).
- For bulk operations, use a bash loop with curl calls (efficient: 50+ links in ~30 seconds).

## Reference Examples

Before creating `why_right_person` entries, review existing good examples:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  where: "(why_right_person,isNot,null)",
  limit: 5,
  sort: "-Id"
})
```

Before creating `why_strong_fit` entries, review existing Target Companies:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  where: "(why_strong_fit,isNot,null)~and(recent_signals,isNot,null)",
  limit: 5,
  sort: "-Id"
})
```

### Rule 9: MCP Troubleshooting (CRITICAL)

**Problem**: MCP shows "Connected" in `claude mcp list` but all operations fail with "fetch failed".

**Root cause**: `claude mcp list` only checks if the process is alive, not if it can communicate with the backend. The MCP internal connection can become stale/broken.

**Diagnosis steps** (do these BEFORE removing/re-adding):
1. Test with a direct API call (curl) to verify the API token and NocoDB service work.
2. If curl works but the MCP fails → MCP internal state is broken.
3. If curl also fails → API token / network / server issue, not an MCP issue.

```bash
curl -H "xc-token: ${NOCODB_API_TOKEN}" \
  "${NOCODB_URL}/api/v2/meta/bases/${NOCODB_BASE_ID}/tables"
```

**Solution**: if curl works but MCP fails, remove and re-add the MCP (with user approval — see Rule 10).

### Rule 10: MCP Removal Requires User Approval

NEVER remove or re-add MCP servers without explicit user approval.

**Why**:
- Removing MCPs can lose API tokens stored in config.
- Re-adding requires the correct configuration.
- The user may have customized the MCP setup.

**Process**:
1. Diagnose the issue first (Rule 9).
2. Explain to the user what the problem is.
3. ASK for permission to remove/re-add.
4. SAVE the API token before removing.
5. Re-add with the saved token.

### Rule 11: Key Dropdown Field Values

Most dropdowns are **user-configurable** via `config/*.yaml`. The schema ships with sane defaults but you should customise.

**Industry** (`target_companies.industry`) — read from `config/industries.yaml`. Default seed values:
- AI/ML Enterprise Software
- Energy Tech
- Robotics & Automation
- Industrial / Construction Tech
- Data & Analytics
- (add your own)

**Tier** (`target_companies.tier`):
- Tier 1 - Highest Priority
- Tier 2 - High Priority
- Tier 3 - Medium Priority

**Region Expansion Status** (`target_companies.expansion_status`) — replace `region` with your `target_regions[]`:
- Announced Expansion (last 12 months)
- First-time at major regional event (last 12-24 months)
- Recent Partnership (last 12 months)
- Series A/B in region (last 18 months)
- Hiring for regional roles
- Exploring market
- Established (3+ years in region)

**Contact Priority** (`target_contacts.contact_priority`):
- Primary
- Secondary
- Backup

**Pipeline Stage** (`sales_pipeline.pipeline_stage`):
- 1. Research
- 2. Drafted
- 3. Sent
- 4. Reply received
- 5. Meeting scheduled
- 6. Meeting completed
- 7. Application submitted
- 8. Closed (no fit)
- 9. Closed (offer received)

**Temperature** (`sales_pipeline.temperature`):
- Cold
- Warm
- Hot

### Rule 12: MCP Usage Patterns (REFERENCE)

#### Pattern 1: Single record insert
```javascript
mcp__nocodb__insert_record({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_companies",
  "data": { "company_name": "Acme Renewables", "industry": "Energy Tech" }
})
```

#### Pattern 2: Bulk insert
```javascript
mcp__nocodb__bulk_insert({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_contacts",
  "records": [
    { "full_name": "Contact 1", "title_role": "Director", "company_id": 159, "contact_priority": "Primary" },
    { "full_name": "Contact 2", "title_role": "VP Engineering", "company_id": 159, "contact_priority": "Secondary" }
  ]
})
```

#### Pattern 3: Update
```javascript
mcp__nocodb__update_record({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_companies",
  "record_id": "159",
  "data": { "why_strong_fit": "Updated value", "recent_signals": "Updated signals" }
})
```
`record_id` is passed as a **string** (even though the value is numeric).

#### Pattern 4: Search
```javascript
mcp__nocodb__search_records({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_contacts",
  "query": "Search Term"
})
```

#### Pattern 5: List with filter
```javascript
mcp__nocodb__list_records({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "sales_pipeline",
  "where": "(company_id,eq,159)",
  "limit": 25,
  "sort": "-Id"
})
```

#### Pattern 6: Advanced query
```javascript
mcp__nocodb__query({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_contacts",
  "where": "(company_id,eq,159)~and(contact_priority,eq,Primary)",
  "fields": ["full_name", "title_role", "why_right_person"],
  "sort": ["-Id"],
  "limit": 10
})
```

#### Pattern 7: Aggregation
```javascript
mcp__nocodb__aggregate({
  "base_id": "${NOCODB_BASE_ID}",
  "table_name": "target_contacts",
  "column_name": "Id",
  "function": "count",
  "where": "(company_id,eq,159)"
})
```

#### Pattern 8: Foreign-key linking (numeric only)
```javascript
"company_id": 159
"contact_id": 42
"pipeline_entry_id": 87
"target_contact_id": 42
```

#### Pattern 9: Retry on "fetch failed"
1. Wait 2-3 seconds.
2. Retry the EXACT same call.
3. If it fails 3x, use the curl fallback (Rule 9).

### NocoDB Filter Syntax Quick Reference

**Operators**:
- `eq`, `neq` — equals / not equals
- `like`, `nlike` — contains (use `%` wildcards)
- `gt`, `gte`, `lt`, `lte` — numeric comparison
- `is,null`, `isNot,null` — null checks

**Combining**:
- AND: `(field1,eq,val1)~and(field2,eq,val2)`
- OR: `(field1,eq,val1)~or(field2,eq,val2)`

**Examples**:
```
(tier,eq,Tier 1 - Highest Priority)
(pipeline_name,like,%Acme%)
(why_strong_fit,isNot,null)
(company_id,eq,159)~and(contact_priority,eq,Primary)
(industry,eq,AI/ML Enterprise Software)~or(industry,eq,Robotics & Automation)
(fit_score,gte,6)
```

### Rule 13: Contact Population Workflow (STANDARD)

DEFAULT WORKFLOW (unless user specifies otherwise):

1. **Target Companies**: create/update the company record first.
2. **Target Contacts**: add 9-10 contacts per company.
3. **Sales Pipeline**: select the TOP 3 from those contacts for outreach.
4. **Interactions**: create interaction records for the top 3.
5. **Messages**: draft and save individual message files for the top 3.

**Quantities**:
- Target Contacts: **9-10 per company**
- Sales Pipeline: **top 3** from those contacts
- Message files: **one per Sales Pipeline contact** (individual files, never batch)

**Selection criteria for top 3**:
1. Highest relevance to the user's `credibility_anchors[]`.
2. Most senior / decision-making authority.
3. Based in target region or focused on it.
4. Recent LinkedIn activity.
5. Direct alignment with the company's regional expansion.

### Rule 14: Direct Application Workstream Tables

#### `job_postings`
- `company_name` — REQUIRED. Plain text. ALWAYS populate (used for dedup).
- `job_title`, `company_id` (FK), `job_board`, `job_url`, `location`, `remote_status`
- `posted_date`, `discovered_date` (ISO)
- `job_description`, `key_requirements` (long text)
- `role_category` — values from `config/user-profile.yaml` `target_roles[]`
- `fit_score` (1-10), `fit_analysis` (long text)
- `status` — New / Reviewing / Applying / Applied / Interview / Rejected / Withdrawn / Expired
- `resume_version_used`, `notes`

#### `applications`
- `application_name` — `{Company} - {Job Title}`
- `job_posting_id`, `company_id` (FK)
- `application_date`, `application_method`
- `resume_version`, `cover_letter` (boolean)
- `application_status` — Preparing / Submitted / Acknowledged / Screening / Interview Scheduled / Interview Completed / Offer / Rejected / Withdrawn
- `response_date`, `networking_contact_id` (FK), `pipeline_entry_id` (FK)
- `follow_up_date`, `notes`

#### `target_companies` workstream field
- `workstream` — Networking / Direct Application / Both

#### `interactions` application-type values
- `Application Submitted`
- `Application Follow-Up`
- `Resume Tailored`
- `Job Posting Saved`

### Rule 15: Cross-Workstream Linking

When creating Job Posting records:
1. ALWAYS search Target Companies first.
2. If the company exists: link to it (set `company_id`).
3. If it has networking contacts: flag in notes as "Warm Application".
4. If it does not exist: create the Target Companies record first (with `workstream = "Direct Application"`).

When creating Application records:
1. Link to the Job Posting (`job_posting_id`).
2. Link to the Company (`company_id`).
3. If a networking contact exists: set `networking_contact_id` and `pipeline_entry_id`.
4. Create an Interaction record with type `Application Submitted`.

**Warm Application Detection**:
```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  query: "Company Name"
})
// If results found → Warm Application.
```

## NocoDB-Specific Capabilities

### Aggregation
```javascript
mcp__nocodb__aggregate({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  column_name: "Id",
  function: "count",
  where: "(company_id,eq,159)"
})
```

### Group by
```javascript
mcp__nocodb__group_by({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  column_name: "pipeline_stage"
})
```

### Schema inspection
```javascript
mcp__nocodb__get_table_info({
  table_id: "<table-id>"   // not table name
})
```

## For Complete Workflows

See `../../operating-procedures/`:
- `OUTREACH-OPERATING-PROCEDURE-v4.md` (Steps 1-7)
- `contact-population-plan-v3.md` (full workflow)
- `DIRECT-APPLICATION-PROCEDURE-v1.md` (direct-application workflow)
- `RESUME-TAILORING-PROCEDURE-v1.md` (resume customisation)
