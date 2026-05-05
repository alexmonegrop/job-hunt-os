---
name: "cold-outreach"
description: "Complete cold outreach workflow: company selection from the database, target-region expansion research, contact population with the 3-element 'Why Right Person' formula, unique-insight development, and 70-90 word message drafting with individual file creation. Includes batch processing (50% time reduction) and Sales Pipeline + Interaction record creation. Use when starting outreach campaigns or processing multiple companies."
---

# Cold Outreach

Automated cold-outreach workflow for value-first messaging in the user's target region.

## What This Skill Does

Automates the complete cold-outreach process from company selection through message creation:

- **Company selection** — find uncontacted companies in the database
- **Target-region expansion research** — WebSearch for recent partnerships/expansions
- **Contact population** — add 9-10 high-quality contacts per company
- **Insight development** — counter-intuitive insights in 15 minutes (see `operating-procedures/QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`)
- **Message drafting** — 70-90 word messages with unique insights
- **Database integration** — create Sales Pipeline + Interaction records
- **Batch processing** — process 15 contacts in 45 minutes (50% time reduction)
- **Individual files** — ONE FILE PER PERSON (`outreach/{user-slug}/messages/company-firstname-lastname.md`)

## Prerequisites

Required:
- Database access via configured MCP (default `mcp__nocodb__*`, base id `${NOCODB_BASE_ID}`).
- Active user's master-experience YAML at `applications/resumes/data/{user-slug}/master-experience.yaml`.
- Active user's user-config YAML at `applications/resumes/data/{user-slug}/user-config.yaml`.
- Operating procedures at `operating-procedures/`.
- **Multi-user**: load the active user from `JOB_HUNT_USER` (env var). Filter all DB queries by `(user_id,eq,{active_user_id})`.

MCP tools:
- `mcp__nocodb__*` (database operations) — or whatever `NOCODB_MCP_PREFIX` you set.
- `WebSearch` (company research).

## Quick Start

Process 5 companies with 3 contacts each:
```
"Run cold outreach for 5 companies"
```

With specific companies:
```
"Run cold outreach for: Acme Renewables, Globex Power, Initech AI"
```

---

## Complete Workflow

### Phase 1: Company Selection (~5 min)

Find 5 uncontacted companies from the database.

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  where: "(sales_pipelines,eq,0)~and(user_id,eq,${ACTIVE_USER_ID})"
})
```

Filter further by:
- Recent news (last 2 weeks)
- Strong fit with the user's `credibility_anchors[]` (from `config/user-profile.yaml`)
- Target region focus (from `config/user-profile.yaml` `target_regions[]`)

Select 5 companies.

### Phase 2: Target-Region Expansion Research (~20 min for all 5)

Research all companies BEFORE proceeding (batch approach).

For each company:
1. Read `why_strong_fit` and `recent_signals` from the database.
2. Run 3-4 WebSearch queries (parametrise `${TARGET_REGION}` from `config/user-profile.yaml`):
   - `"[Company] ${TARGET_REGION} expansion 2025 2026"`
   - `"[Company] ${TARGET_REGION_COUNTRIES} partnership"`
   - `"[Company] ${TARGET_REGION} announcement"`
3. Develop a counter-intuitive insight using `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`.
4. Document insights BEFORE moving to contacts.

Update the Target Companies record:
```javascript
mcp__nocodb__update_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  record_id: "<company_id>",
  data: {
    why_strong_fit: "[user background + company target-region context + strategic alignment]",
    recent_signals: "[date-specific expansions, Month YYYY format]",
    industry: "<from config/industries.yaml>",
    research_date: "2026-MM-DD"
  }
})
```

### Phase 3: Contact Selection (~10 min)

Find the best 3 contacts per company (15 total).

For each company:
1. Search Target Contacts:
   ```javascript
   mcp__nocodb__search_records({
     base_id: "${NOCODB_BASE_ID}",
     table_name: "target_contacts",
     query: "Company Name"
   })
   ```
2. Use WebSearch as the primary tool:
   - `"[Company] director operations LinkedIn"`
   - `"[Company] engineering manager LinkedIn ${TARGET_CITY}"`
   - `"[Company] senior manager [technology] LinkedIn"`
3. Prioritise per `04-contact-selection-priorities.md`:
   - Large (5,000+): 70-90% Directors / Senior Managers
   - Medium (500-5,000): 60-80% operational roles
   - Small (<500): co-founders + early hires

Batch duplicate check (ONE query for all 15):
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  where: "(pipeline_name,like,%Contact1%)~or(pipeline_name,like,%Contact2%)~or...~or(pipeline_name,like,%Contact15%)",
  limit: 20
})
```

### Phase 4: Database Record Creation (~10 min)

Create all 15 Sales Pipeline + 15 Interaction records.

Step 1 — bulk_insert all 15 Pipeline records (single message):
```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  records: [ /* 15 records */ ]
})
// Capture all returned record IDs.
```

Step 2 — bulk_insert all 15 Interaction records (single message):
```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "interactions",
  records: [ /* 15 records, with target_contact_id and pipeline_entry_id from Step 1 */ ]
})
```

### Phase 5: Message Drafting + File Creation (~15 min)

For each of the 15 contacts:
1. Use the company insight from Phase 2.
2. Apply the 70-90 word formula (`02-message-quality-standards.md`):
   - News Hook (5-10 words)
   - Unique Insight (20-30 words)
   - Evidence/Pattern (10-15 words)
   - Your Credibility (10-15 words) — pull from `config/user-profile.yaml` `credibility_anchors[]`
   - Geographic Flexibility (5-10 words) — pull from `config/user-profile.yaml` `location` and `target_regions[]`
   - Soft Ask (10-15 words)
3. Create an INDIVIDUAL FILE (CRITICAL):
   - Location: `outreach/{user-slug}/messages/`
   - Format: `company-firstname-lastname.md`
   - Example: `acme-renewables-jane-smith.md`
4. Use the message file structure from `05-file-organization-rules.md`.

NEVER create batch files. Each person gets their own file.

---

## Batch Processing Optimisation

Time comparison:
- Sequential: 90-120 min for 15 contacts
- Batch: 45 min for 15 contacts
- Savings: 50%

Key efficiency rules:
- Research ALL companies first (Phase 2)
- Select ALL contacts, then batch duplicate check (Phase 3)
- Create ALL Pipeline records in ONE bulk_insert (Phase 4)
- Create ALL Interaction records in ONE bulk_insert (Phase 4)
- Draft messages together, save to individual files (Phase 5)

---

## Quality Checkpoints

After Phase 2 (Research):
- [ ] All 5 companies have `why_strong_fit` updated
- [ ] All 5 have `recent_signals` with dates
- [ ] All 5 have counter-intuitive insights documented

After Phase 3 (Contacts):
- [ ] 15 contacts selected (3 per company)
- [ ] Batch duplicate check completed (no duplicates)
- [ ] Mix of Primary / Secondary priorities

After Phase 4 (Database):
- [ ] 15 Sales Pipeline records created
- [ ] 15 Interaction records created
- [ ] All linked properly (Company, Contact, Pipeline)
- [ ] All `why_right_person` entries use the 3-element formula

After Phase 5 (Messages):
- [ ] 15 individual files created (NOT batch file)
- [ ] All files named: `company-firstname-lastname.md`
- [ ] All messages 70-90 words
- [ ] All messages include unique insights

---

## Reference Documentation

- Full workflow: `operating-procedures/OUTREACH-OPERATING-PROCEDURE-v4.md`
- Insight development: `operating-procedures/QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`
- Message examples: `operating-procedures/UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md`
- Contact population: `operating-procedures/contact-population-plan-v3.md`

Rules automatically enforced:
- `.claude/rules/01-database-standards.md`
- `.claude/rules/02-message-quality-standards.md`
- `.claude/rules/03-batch-operations-rules.md`
- `.claude/rules/04-contact-selection-priorities.md`
- `.claude/rules/05-file-organization-rules.md`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database token-limit errors | Use `search_records` for `target_contacts`, not `list_records` |
| Missing `why_right_person` context | Ensure Target Companies updated FIRST in Phase 2 |
| Created batch file instead of individual files | Create 15 separate Write calls, one per contact |
| Messages too long (>90 words) | Trim fluff, combine sentences, remove redundancy |
