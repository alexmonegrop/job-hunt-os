# Contact Population Plan v3

**Document type**: Reference. For automatic enforcement, see `.claude/rules/01-database-standards.md` and `04-contact-selection-priorities.md`.

**Purpose**: Populate 9-10 high-quality contacts per company with the 3-element "Why Right Person" formula.

**Companion**: skill `contact-population`.

## Tools & Strategy

### MCP tools

**Database (NocoDB by default)** — primary for storage:
- `mcp__nocodb__list_records` — find company records
- `mcp__nocodb__get_table_info` — schema check
- `mcp__nocodb__insert_record` / `bulk_insert` — add new contacts
- `mcp__nocodb__search_records` — search existing
- `mcp__nocodb__update_record` — update company / contact records

**LinkedIn MCP** — backup profile scraping:
- `mcp__linkedin__get_company_profile` — employee list
- `mcp__linkedin__get_person_profile` — individual profile
- `mcp__linkedin__search_jobs` — postings search

LinkedIn MCP usage: prefer `WebSearch` + `WebFetch` first; use LinkedIn MCP sparingly (2-3 queries per company max), as validation or when stuck.

### Operational role focus

| Company size | Composition |
|-------------|-------------|
| Large (5,000+) | 70-90% Directors / Senior Managers / Managers |
| Medium (500-5,000) | 60-80% operational roles |
| Small (<500) | Co-founders + early operational hires |

Acceptable operational roles: Engineering / Product / Delivery Managers, Solutions Architects, Technical Directors, Customer Success, Account Managers, Project / Program Managers, Regional Operations Directors, Zone / Country Managers.

## Lessons Learned (preserved across sessions)

### What works exceptionally well
1. **WebSearch as primary tool** — most operational-level contacts findable without LinkedIn MCP. Highly effective.
2. **Contextual "Why Right Person" formula** — 3-element connection (user's background + company target-region expansion + role relevance) creates compelling, personalised outreach rationale.
3. **Company research FIRST** — updating Target Companies record before finding contacts ensures all "Why Right Person" entries have strong contextual foundation.
4. **Recent announcements drive quality** — date-specific expansions provide perfect timing context.
5. **Batch operations** — adding 10 contacts in single `bulk_insert` maintains consistency and efficiency.

### Effective search patterns
- `"[Company] director operations LinkedIn"`
- `"[Company] engineering manager LinkedIn [target city]"`
- `"[Company] senior manager [technology] LinkedIn"`
- `site:linkedin.com/in/ "[Company]" "manager" OR "director" OR "engineer"`

### Company-specific strategies
- **Massive companies (60K+)**: focus on operational layers — avoid C-suite unless perfect match. Use specific department searches (digital transformation, AI, automation).
- **New companies (<2 years)**: emphasise timing urgency, founding-team building, immediate hiring needs.
- **Expansion announcements**: reference specific partnerships / deals (in both Target Companies and contact entries).
- **Industry sweet spots**: companies in `user-profile.yaml` `target_industries[]` aligned with `credibility_anchors[]` get strongest framing.

### Important considerations
- For massive organisations, operational mid-level contacts often have more direct hiring influence than distant C-suite.
- Regional expansion timing matters — "just announced" vs "3+ years established" changes urgency narrative.
- Active LinkedIn presence (last 30 days) is a strong quality signal.

## Workflow Per Company (Step-by-Step)

### STEP 1: Find company in the database

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  query: "Company Name"
})
// Capture the company record ID.
```

### STEP 2: Research target-region expansion (CRITICAL)

BEFORE adding contacts, research the company's relevance to the user's target region.

```javascript
WebSearch("[Company] [target region] expansion")
WebSearch("[Company] [target country] partnership")
WebSearch("[Company] [target region] announcement <year>")
WebSearch("[Company] [specific city if known]")
```

Look for:
- Recent partnerships / contracts with regional entities
- Office openings in target cities
- Funding announcements with regional investors
- Hiring for regional roles
- Major regional conference participation
- Manufacturing / expansion plans
- Government contracts

### STEP 3: Update Target Companies record (CRITICAL)

```javascript
mcp__nocodb__update_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  record_id: "<company_id>",
  data: {
    why_strong_fit: "[3-element formula]",
    recent_signals: "[date-specific, Month YYYY]",
    industry: "<from config/industries.yaml>",
    hq_location: "City, Country",
    tier: "Tier 2 - High Priority",
    research_date: "<ISO date>"
  }
})
```

`why_strong_fit` MUST include:
1. **The user's relevant background** — pull from `applications/resumes/data/{user-slug}/master-experience.yaml` and `config/user-profile.yaml` `credibility_anchors[]`.
2. **The company's target-region expansion context** — what regional operations, why need talent NOW.
3. **Strategic alignment** — why the user's specific experience matches their needs.

`recent_signals` MUST include:
- Date-specific announcements (Month YYYY format)
- Concrete expansion plans
- Partnership announcements with regional entities
- Funding / contract values
- Hiring initiatives
- Manufacturing / operational plans

Reference good examples first:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  where: "(why_strong_fit,isNot,null)~and(recent_signals,isNot,null)",
  limit: 5
})
```

### STEP 4: Check existing contacts

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})
// Count results. Target: 10 total per company.
```

### STEP 5: Research contacts

**Option A: Web research (PRIMARY)**:
- WebSearch: `"[Company] director operations LinkedIn"`
- WebSearch: `"[Company] engineering manager LinkedIn"`
- WebSearch: `"[Company] [city] VP engineering LinkedIn"`
- Extract names, titles, LinkedIn URLs

**Option B: LinkedIn MCP (if web search fails — max 2-3 queries)**:
```javascript
mcp__linkedin__get_company_profile({
  company_name: "company-slug",
  get_employees: true
})
```

### STEP 6: Add contacts to the database

CRITICAL: always include the `why_right_person` field.

Reference good examples first:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  where: "(why_right_person,isNot,null)",
  limit: 5,
  sort: "-Id"
})
```

Use `bulk_insert` for efficiency:
```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  records: [
    {
      full_name: "Jane Smith",
      title_role: "Director of Engineering",
      linkedin_profile: "https://linkedin.com/in/janesmith",
      company_id: <numeric>,
      why_right_person: "[3-element formula — see below]",
      contact_source: "LinkedIn",
      contact_priority: "Primary",
      added_date: "<ISO>",
      user_id: <active_user_id>
    }
    // ...up to 10
  ]
})
```

`why_right_person` 3-element formula (3-5 sentences):

**Element 1: The user's specific relevant experience**
Reference SPECIFIC role / achievement from the user's resume YAML. Examples (illustrative, generate from real data):
- "<user>'s [past role at past company] overseeing $10M+ initiatives with [flagship client]..."
- "<user>'s 2x AI/ML startup founder experience ([startup A], [startup B])..."
- "<user>'s robotics deployment background ([past employer A], [past employer B])..."

**Element 2: The company's target-region expansion context**
Reference the specific expansion from Step 2 research:
- "during [Company]'s [region] expansion to 40-50 employees"
- "managing [flagship client] contracts ($30M+)"
- "as they establish [city] manufacturing"

**Element 3: The contact's role relevance**
- How their specific role connects to the user's background
- How their role is critical for the regional expansion
- What insights / opportunities this contact represents

Example format (fictional — replace with real research):
```
Program Manager BASED IN <target city> — the most directly relevant contact for
[Company]'s <region> expansion. <Contact> manages regional program delivery exactly
where the user is located and where [Company] is doubling operations. The user's
[past role] overseeing $10M+ initiatives with [flagship client] provides peer-level
credibility for discussing regional program-management challenges. Both are
PMP-aligned professionals managing large-scale technical deployments in industrial
settings. <Contact>'s on-ground experience with [flagship contract] benefits from
the user's [related partnership] insights and understanding of regional client
expectations. PERFECT FIT: <Contact> leads programs in the exact market the user
knows deeply, during [Company]'s aggressive expansion phase requiring local-market
expertise and operational scaling knowledge.
```

Priority-specific guidelines:
- **Primary contacts** (C-level, Directors, VPs): emphasise strategic alignment, decision-making authority, executive / founder credibility.
- **Secondary contacts** (Managers, Engineers): emphasise technical / operational alignment, peer-level relevance, team insights.

### STEP 7: Verify completion

```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "Company Name"
})
// If count >= 10: DONE.
// If count < 10: continue research.
```

## Quality Criteria

### Acceptable operational roles
- Engineering / Product / Delivery Managers
- Solutions Architects / Technical Directors
- Customer Success / Account Managers
- Project / Program Managers
- Regional Operations Directors
- Zone / Country Managers

### Companies with <10 existing contacts
Flexible quality-based approach:
- 8-9 contacts: select best 3-5
- 5-7 contacts: select best 3 if all high-quality
- <5 contacts: select all if Primary/Secondary
- Backup: research additional via WebSearch

## Quick Reference

For each company specified by user:
1. Find company in DB → get record ID
2. Research target-region expansion (WebSearch 3-4 queries)
3. Update Target Companies: `why_strong_fit` + `recent_signals` + metadata
4. Check existing contacts → determine how many needed
5. Research contacts (WebSearch, targeted operational roles)
6. Add contacts with contextual `why_right_person` (3-element formula)
7. Verify completion (10 total contacts)

Quality checklist:
- [ ] Target Companies updated BEFORE adding contacts
- [ ] `why_right_person` connects user + company expansion + role (3-5 sentences)
- [ ] Recent dates in `recent_signals` (Month YYYY format)
- [ ] Operational focus (Directors / Managers for large cos, co-founders for small)
- [ ] Up to 10 contacts per company (flexible if <10 high-quality available)
