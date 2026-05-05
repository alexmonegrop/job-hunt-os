---
name: "application-tracker"
description: "Track and manage job applications: check status of all applications, identify follow-up opportunities (7+ days no response), cross-reference networking contacts, generate action lists, and draft follow-up messages. Use for application dashboard, follow-up checks, and weekly application reviews."
---

# Application Tracker

Application status monitoring, follow-up scheduling, and cross-workstream intelligence.

## What This Skill Does

- **Status dashboard** — overview of all applications by status
- **Follow-up detection** — identify applications needing follow-up (7+ days)
- **Cross-workstream intelligence** — link applications to networking contacts
- **Action list generation** — prioritised next actions across all applications
- **Follow-up drafting** — draft follow-up messages for stale applications
- **Weekly review** — comprehensive weekly application status report

## Prerequisites

- Database access via configured MCP (`mcp__nocodb__*`, `${NOCODB_BASE_ID}`)
- `applications` table populated
- All queries filtered by `(user_id,eq,${ACTIVE_USER_ID})`

## Quick Start

```
"Check my applications" / "Application dashboard"
"Which applications need follow-up?"
"Run weekly application review"
```

## Workflow

### Dashboard view

Query the applications table and display:

```
| Company | Job Title | Applied | Status | Days | Follow-Up? | Contact? |
|---------|-----------|---------|--------|------|------------|----------|
| Acme    | Sr PM     | Jan 15  | Submitted    | 20 | OVERDUE   | Yes (3) |
| Globex  | AI PM     | Jan 28  | Acknowledged | 7  | Due today | No      |
| Initech | Product   | Feb 1   | Preparing    | 3  | N/A       | Yes (1) |
```

### Follow-up detection

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "applications",
  where: "(application_status,eq,Submitted)~and(user_id,eq,${ACTIVE_USER_ID})",
  sort: "application_date",
  limit: 100
})
// Filter in post-processing for date math (>= 7 days since application_date).
```

Categorise:
- **First follow-up** (7-13 days): professional check-in
- **Second follow-up** (14-20 days): value-add follow-up with new insight
- **Past due** (21+ days): final follow-up or mark as no-response

### Cross-workstream check

For each application needing follow-up:
1. Check if the company has networking contacts in `target_contacts`.
2. Check if `sales_pipeline` entries exist.
3. If warm: recommend following up through the contact instead of cold follow-up.
4. If the contact recently responded: leverage the warm connection.

### Action list generation

```
## Priority Actions (Today)
1. Follow up on Acme Sr PM (20 days, warm — contact: Jane Smith)
2. Follow up on Globex AI PM (7 days, cold)

## This Week
3. Prepare application for Initech Product Manager (score: 8)
4. Check Acme career page for new postings

## Monitoring
5. Globex — acknowledged 3 days ago, check again in 4 days
6. Initech — interview scheduled
```

### Follow-up message drafting

Cold follow-up (no networking contact):
```
Subject: Re: [Job Title] Application — [New Value Add]

[Name],

Quick follow-up on my application for [Job Title]. Since applying,
[new relevant development — company news, industry insight, or
personal achievement].

[Brief value reminder — 1-2 sentences about fit].

Happy to discuss at your convenience.

Best,
[user full name]
```

Warm follow-up (via networking contact):
```
Recommend reaching out to [Contact Name] instead:
"Hi [Contact], I applied for the [Job Title] role on your team
[X days ago]. Any insight into the timeline? Happy to provide
additional context if helpful."
```

### Weekly review report

```markdown
# Application Weekly Review — Week of [Date]

## Summary
- Total active applications: X
- New applications this week: Y
- Responses received: Z
- Follow-ups sent: W

## By Status
- Preparing: X
- Submitted (awaiting): Y
- Acknowledged: Z
- Screening: W
- Interview Scheduled: V
- Rejected: R

## Actions Taken This Week
1. ...

## Priority Actions Next Week
1. ...

## Pipeline Health
- Average response time: X days
- Response rate: Y%
- Warm application rate: Z%
```

## Rules

1. **ALWAYS check cross-workstream** — flag warm-application opportunities.
2. **Follow-up timing**: 7 days first, 14 days second, then close.
3. **Never follow up more than twice** on cold applications.
4. **Warm follow-ups through contacts** are preferred over cold follow-ups.
5. **Update the database** after each follow-up action.
6. **Create Interaction records** for all follow-up activities.

## Integration with other skills

- `job-search`: feeds new Job Postings → triggers application prep
- `apply`: creates Application records → tracked here
- `resume-tailor`: generates resume versions → linked to applications
- `cold-outreach`: networking contacts → warm-application opportunities
- `warm-followup`: handles warm follow-ups at networked companies

## Reference Documentation

`operating-procedures/DIRECT-APPLICATION-PROCEDURE-v1.md`
