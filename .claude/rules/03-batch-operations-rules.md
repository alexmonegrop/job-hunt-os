# Batch Operations Rules

## GOLDEN RULE: "1 MESSAGE = ALL RELATED OPERATIONS"

**MANDATORY**: All concurrent operations MUST be in a SINGLE message.

**Why**: ~50% time reduction (45 min vs 90-120 min for 15 contacts).

## Batch Operation Requirements

### Task tracking (ALWAYS batch)

**NEVER** create todos one at a time.

Correct: one TaskCreate (or TodoWrite) call with 5-10+ todos.

Wrong: multiple messages with individual todos.

### File Operations (ALWAYS batch)

**ALL** reads/writes/edits in ONE message when processing related files.

Correct (single message):
```javascript
Read("research/{user-slug}/company1-analysis.md")
Read("research/{user-slug}/company2-analysis.md")
Read("research/{user-slug}/company3-analysis.md")
Write("outreach/{user-slug}/messages/company1-person1.md")
Write("outreach/{user-slug}/messages/company1-person2.md")
Write("outreach/{user-slug}/messages/company1-person3.md")
```

Wrong: message 1 reads file1, message 2 reads file2, message 3 writes…

### Bash Commands (ALWAYS batch)

Independent commands in ONE message.

Correct (single message with parallel commands):
```javascript
Bash("git status")
Bash("git log --oneline -10")
Bash("git diff --stat")
```

Wrong: separate messages for each git command.

**Exception**: sequential operations that DEPEND on previous results.
```bash
git add . && git commit -m "message" && git push
```

### Database Operations (CRITICAL for efficiency)

These examples use NocoDB MCP tool prefix `mcp__nocodb__`. The base ID, URL and token come from `.env` (`${NOCODB_BASE_ID}`, `${NOCODB_URL}`, `${NOCODB_API_TOKEN}`). Adjust to your configured backend.

#### Creating 15 Sales Pipeline Records

BEST: ONE `bulk_insert` call with all 15 records (single API call!)
```javascript
[Single message — single API call]:
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  records: [
    { pipeline_name: "Contact 1 - Company", contact_id: 101, company_id: 5, pipeline_stage: "1. Research", temperature: "Cold", notes: "Batch 2026-MM-DD" },
    { pipeline_name: "Contact 2 - Company", contact_id: 102, company_id: 5, pipeline_stage: "1. Research", temperature: "Cold", notes: "Batch 2026-MM-DD" },
    { pipeline_name: "Contact 3 - Company", contact_id: 103, company_id: 5, pipeline_stage: "1. Research", temperature: "Cold", notes: "Batch 2026-MM-DD" },
    // ...
    { pipeline_name: "Contact 15 - Company", contact_id: 115, company_id: 8, pipeline_stage: "1. Research", temperature: "Cold", notes: "Batch 2026-MM-DD" }
  ]
})
```

Also acceptable: ONE message with 15 parallel `insert_record` calls.

Wrong: 15 separate messages.

#### Creating 15 Interaction Records

BEST: ONE `bulk_insert` call (after capturing Pipeline IDs).
```javascript
[Single message after Pipeline records created]:
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "interactions",
  records: [
    { interaction_type: "Message Drafted", interaction_date: "2026-MM-DDT15:00:00.000Z", target_contact_id: 101, pipeline_entry_id: 201, interaction_summary: "Initial outreach drafted", subject_topic: "Topic A" },
    { interaction_type: "Message Drafted", interaction_date: "2026-MM-DDT15:00:00.000Z", target_contact_id: 102, pipeline_entry_id: 202, interaction_summary: "Initial outreach drafted", subject_topic: "Topic B" },
    // ...
  ]
})
```

**Time savings**:
- Sequential: 15 Pipeline + 15 Interaction = 30+ messages
- Bulk insert: **2 messages total** (1 for Pipeline, 1 for Interactions)

### Agent Spawning (Use the Agent / Task tool)

ALL agents spawned in ONE message with full instructions.

Correct:
```javascript
Agent("Research agent", "Analyze 5 companies for [region] expansion. Full instructions...", "researcher")
Agent("Coder agent", "Draft messages using insights. Full instructions...", "coder")
Agent("Reviewer agent", "Review message quality. Full instructions...", "reviewer")
Agent("Tester agent", "Validate database records. Full instructions...", "tester")
```

Wrong: message 1 spawns researcher, message 2 spawns coder, etc.

## Workflow Batch Processing Patterns

### Company-by-Company Message Creation

**ALWAYS use company-by-company, NOT contact-by-contact**:

Correct: Research all companies → Draft all Company A messages → Draft all Company B messages → etc.
Wrong: Research Company A → Draft 1 message → Research Company B → Draft 1 message → etc.

**Why**: Creates contextual consistency, deeper insights, and maintains research momentum.

**Research Pattern per Company** (3-4 WebSearch queries):
1. `[Company] recent news 2025 2026 partnerships expansion`
2. `[Company] [specific initiative: ESG/expansion/technology] 2025 2026`
3. `[Company] [target region]`
4. `[Company leadership/product] strategic developments`

Include both the current year and prior year in searches (recent news spans both).

**File Creation Batching** — write ALL files for a company in ONE message:
```javascript
[Single message for Company with 5 contacts]:
Write("outreach/{user-slug}/messages/company-person1.md")
Write("outreach/{user-slug}/messages/company-person2.md")
Write("outreach/{user-slug}/messages/company-person3.md")
Write("outreach/{user-slug}/messages/company-person4.md")
Write("outreach/{user-slug}/messages/company-person5.md")
```

### Outreach Batch Processing (15 contacts, 4 phases)

**Phase 1 — Research All Companies First** (~20 min):
```
[Single session]:
FOR EACH of 5 companies:
  - Read "why_strong_fit" from Target Companies
  - Run 3-4 WebSearch queries (see pattern above)
  - Develop counter-intuitive insights using operational tension patterns
  - Document insights BEFORE proceeding to next company
```

**Phase 2 — Contact Selection + Duplicate Check** (~10 min):
```
[Single session]:
FOR EACH company:
  - Search Target Contacts for 3 best contacts

[Single batch duplicate check]:
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  where: "(pipeline_name,like,%Contact1%)~or(pipeline_name,like,%Contact2%)~or...~or(pipeline_name,like,%Contact15%)",
  limit: 20
})
```

**Phase 3 — Database Record Creation** (~5 min):
```
[Message 1 — All 15 Pipeline records via bulk_insert]:
mcp__nocodb__bulk_insert({ base_id: "${NOCODB_BASE_ID}", table_name: "sales_pipeline", records: [...15 records...] })
// Capture ALL returned Pipeline IDs

[Message 2 — All 15 Interaction records via bulk_insert]:
mcp__nocodb__bulk_insert({ base_id: "${NOCODB_BASE_ID}", table_name: "interactions", records: [...15 records...] })
```

**Phase 4 — Message Drafting + File Creation** (~15 min):
```
[Single session, individual files]:
FOR EACH of 15 contacts:
  - Use company insight from Phase 1
  - Apply 70-90 word formula
  - CREATE INDIVIDUAL FILE: outreach/{user-slug}/messages/company-firstname-lastname.md
  - (Not a batch file! See 05-file-organization-rules.md)
```

### Meeting Prep Batch Processing

Correct (single comprehensive research session):
```javascript
[One session]:
  Read("outreach/{user-slug}/messages/company-person.md")
  WebSearch("[Person Name] LinkedIn")
  WebSearch("[Company] recent news")
  WebSearch("[Company] [target region] expansion")
  WebSearch("[Industry] [region] challenges")
  WebSearch("[Competitor] [similar initiative] lessons learned")
  Write("outreach/{user-slug}/prep/company-person-prep.md")
```

Wrong: separate sessions for each research query.

## Performance Targets

| Operation | Sequential | Batch | Time Savings |
|-----------|-----------|-------|--------------|
| 15 contacts | 90-120 min | 45 min | **50%** |
| 5 file reads | 5 messages | 1 message | **80%** |
| 10 todos | 10 calls | 1 call | **90%** |
| 15 Pipeline + 15 Interaction records | 30 messages | 2 bulk_insert calls | **93%** |
| 10 Job Posting records | 10 messages | 1 bulk_insert call | **90%** |

`bulk_insert` creates multiple records in a single API call — even more efficient than parallel individual creates.

## Exception: When to Use Sequential

Use sequential ONLY when operations DEPEND on previous results:

Sequential when needed:
- Git workflow: `git add . && git commit -m "msg" && git push`
- File creation before git commit
- Pipeline records before Interaction records (need Pipeline IDs)

Parallel when independent:
- Multiple WebSearch queries
- Multiple file reads
- Multiple database inserts for different tables (when no ID dependency)

## Common Batch Processing Pitfalls

- Don't: Research company → Draft message → Create records → Next company
- Do: Research ALL companies → Draft ALL messages → Create ALL records

- Don't: Create Pipeline records one at a time across 15 messages
- Do: Create all 15 Pipeline records in a single `bulk_insert` call

- Don't: Develop insights while drafting messages
- Do: Develop all insights first, then draft all messages

- Don't: Check for duplicates one contact at a time
- Do: Check all 15 contacts in a single `where` clause with `~or` operators

## Direct Application Batch Patterns

### Job Search Session (batch all searches)

```javascript
[Single message]:
  JobSpy search "Program Manager [target city 1]"
  JobSpy search "AI Product Manager [target country]"
  JobSpy search "Digital Transformation Director [target city 2]"
  WebSearch "site:[regional job board] program manager [region]"
  WebSearch "site:[regional job board] AI product manager [target city]"
```

### Job Posting Record Creation (batch all creates)

BEST: score all results, then create all records with one bulk_insert:
```javascript
[Single message — all qualifying postings]:
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "job_postings",
  records: [
    { job_title: "Senior PM", company_name: "[CompanyA]", company_id: 5, job_board: "LinkedIn", job_url: "https://...", location: "[City], [Country]", remote_status: "Hybrid", discovered_date: "2026-MM-DD", fit_score: 8, status: "New" },
    // ...
  ]
})
```

### Application Preparation (batch by company)

```javascript
[Single message per company]:
  Read(job posting details)
  Read(applications/resumes/data/{user-slug}/master-experience.yaml)
  Write(tailored resume)
  Write(cover letter)
  Write(application package)
```

### Application Tracking Check (single query)

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "applications",
  where: "(application_status,eq,Submitted)~and(follow_up_date,is,null)",
  sort: "application_date",
  limit: 50
})
```

## For Complete Batch Workflows

See `../../operating-procedures/`:
- `OUTREACH-OPERATING-PROCEDURE-v4.md` (Batch Processing Workflow section)
- `contact-population-plan-v3.md` (Phase-based batch processing)
- `DIRECT-APPLICATION-PROCEDURE-v1.md` (Application batch patterns)
