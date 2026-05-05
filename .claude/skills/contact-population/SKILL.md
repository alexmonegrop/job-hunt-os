---
name: "contact-population"
description: "Populate 9-10 high-quality contacts per company with 3-element 'Why Right Person' formula connecting the user's background + company's target-region expansion + contact's role relevance. Includes target-region expansion research, Target Companies record update, operational role prioritization by company size, and batch duplicate checking."
---

# Contact Population

Add 9-10 high-quality contacts per company to the database.

## What This Skill Does

- **Target-region expansion research** — find recent partnerships, expansions, hiring
- **Target Companies update** — populate `why_strong_fit` and `recent_signals` FIRST
- **Contact selection** — find 9-10 operational contacts prioritised by company size
- **3-element formula** — comprehensive `why_right_person` entries
- **Quality focus** — 70-90% Directors/Managers for large companies
- **WebSearch primary** — LinkedIn MCP only as backup (~95% effective with WebSearch alone)
- **Batch operations** — process all contacts efficiently

## Prerequisites

Required:
- Database access via configured MCP (`mcp__nocodb__*`, `${NOCODB_BASE_ID}`)
- Active user's master-experience YAML at `applications/resumes/data/{user-slug}/master-experience.yaml`
- Active user's user-config YAML at `applications/resumes/data/{user-slug}/user-config.yaml`
- **Multi-user**: include `user_id` in all record creation, filter all queries by `(user_id,eq,{active_user_id})`

MCP tools:
- `mcp__nocodb__*`
- `WebSearch` (primary research tool)
- `mcp__linkedin__*` (backup, sparingly)

## Quick Start

```
"Populate contacts for Acme Renewables"
"Populate contacts for: Acme Renewables, Globex Power, Initech AI"
```

---

## Complete Workflow (7 Steps)

### Step 1: Find company in database (~2 min)

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  query: "Company Name"
})
// Capture the company record ID.
```

### Step 2: Research target-region expansion (~10 min)

CRITICAL — do this BEFORE adding contacts.

```javascript
WebSearch("[Company] ${TARGET_REGION} expansion")
WebSearch("[Company] ${TARGET_REGION_COUNTRIES} partnership")
WebSearch("[Company] ${TARGET_REGION} announcement 2025 2026")
```

Look for:
- Recent partnerships/contracts with regional entities
- Office openings in target cities (read `config/user-profile.yaml` `target_regions[]`)
- Funding with regional investors
- Hiring for regional roles
- Major regional conference participation
- Government / state-owned contracts

### Step 3: Update Target Companies record (~5 min)

MANDATORY before adding contacts:

```javascript
mcp__nocodb__update_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  record_id: "<company_id>",
  data: {
    why_strong_fit: "[3-element: user background + company target-region context + strategic alignment]",
    recent_signals: "[date-specific, Month YYYY format]",
    industry: "<from config/industries.yaml>",
    hq_location: "[City, Country]",
    tier: "Tier 2 - High Priority",
    research_date: "2026-MM-DD"
  }
})
```

`why_strong_fit` MUST include:
1. The user's relevant background — pull from `config/user-profile.yaml` `credibility_anchors[]` and resume YAML
2. The company's target-region expansion context (what operations, why need talent NOW)
3. Strategic alignment (why the user's experience matches their needs)

`recent_signals` MUST include:
- Date-specific announcements (Month YYYY)
- Concrete expansion plans
- Partnership values/scales
- Hiring initiatives

Reference good existing examples first:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  where: "(why_strong_fit,isNot,null)~and(recent_signals,isNot,null)",
  limit: 5
})
```

### Step 4: Check existing contacts (~2 min)

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})
// Count results, determine how many more needed (target: 10 total).
```

### Step 5: Research contacts (~20 min)

Primary tool — WebSearch (~95% effective):
```
"[Company] director operations LinkedIn"
"[Company] engineering manager LinkedIn [target city]"
"[Company] senior manager [technology] LinkedIn"
"[Company] program manager [region] LinkedIn"
site:linkedin.com/in/ "[Company]" "manager" OR "director"
```

Backup — LinkedIn MCP (sparingly, 2-3 queries max):
```javascript
mcp__linkedin__get_company_profile({
  company_name: "company-slug",
  get_employees: true
})
```

Contact prioritisation per `04-contact-selection-priorities.md`.

Acceptable roles: Engineering / Product / Delivery Managers, Solutions Architects / Technical Directors, Customer Success / Account Managers, Project / Program Managers, Regional Operations Directors.

Generally avoid: pure sales (unless regionally focused), marketing (unless growth/expansion), HR (unless talent-acquisition leadership).

### Step 6: Add contacts to the database (~15 min)

Reference good existing examples first:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  where: "(why_right_person,isNot,null)",
  limit: 5
})
```

For each contact:
```javascript
mcp__nocodb__insert_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  data: {
    full_name: "Jane Smith",
    title_role: "Director of Engineering",
    linkedin_profile: "https://linkedin.com/in/username",
    company_id: 159,                       // numeric FK
    why_right_person: "[3-element formula]",
    contact_source: "LinkedIn",
    contact_priority: "Primary",
    added_date: "2026-MM-DD",
    user_id: ${ACTIVE_USER_ID}
  }
})
```

`why_right_person` 3-element formula (CRITICAL — see `01-database-standards.md` Rule 4 for full template):

1. **The user's specific relevant experience** — reference a SPECIFIC role/achievement from their resume YAML.
2. **The company's target-region expansion context** — reference a specific expansion from Step 3 research, with date and scale.
3. **The contact's role relevance** — why THIS role is critical for the regional expansion, how it connects to the user's background, geographic alignment.

Use bulk_insert for efficiency when adding many contacts at once:
```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  records: [ /* up to 10 contact records */ ]
})
```

### Step 7: Verify completion (~2 min)

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})
// If count >= 10: DONE.
// If count < 10: continue research.
```

---

## Quality Checklist

- [ ] Target Companies record updated (`why_strong_fit` + `recent_signals`)
- [ ] 9-10 contacts added (or 8-9 if all high-quality)
- [ ] All `why_right_person` entries use 3-element formula (3-5 sentences)
- [ ] Operational focus (70-90% Directors/Managers for large companies)
- [ ] Geographic relevance (target-region-based or focused)
- [ ] Mix of Primary / Secondary / Backup priorities
- [ ] All FK fields use numeric IDs (not arrays)

---

## Companies with <10 Existing Contacts

Flexible approach:
- 8-9 contacts: select best 3-5 by quality
- 5-7 contacts: select best 3 if all high-quality
- <5 contacts: select all if Primary/Secondary priority
- Backup: research additional via WebSearch

Not all companies will have 10 contacts — acceptable if quality is high.

---

## Reference Documentation

- Full workflow: `operating-procedures/contact-population-plan-v3.md`
- Rules: `.claude/rules/01-database-standards.md`, `04-contact-selection-priorities.md`
