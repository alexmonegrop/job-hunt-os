---
name: "warm-followup"
description: "Complex follow-up workflow for warm relationships: post-interview follow-up (positive or negative), timing-triggered re-engagement ('let's talk when X'), and multi-contact thread recovery (spoke to A, referred to B, B rejected, back to A). Prompts for missing context, researches news hooks with date validation, calibrates tone for warm relationships, and creates follow-up packages with database updates."
---

# Warm Follow-Up

Specialised follow-up system for warm relationships that require nuanced re-engagement beyond cold outreach.

## What This Skill Does

- **Relationship audit** — pull all DB history (Contact, Pipeline, Interactions)
- **Context mapping** — understand interview outcomes, referrals, rejections, commitments
- **Missing-context prompts** — ask user for information not in records
- **News-hook research** — find a current trigger justifying outreach (with strict date validation)
- **Tone calibration** — warm peer conversation (not job-seeker)
- **Callback references** — reference specific past conversations
- **Face-saving framing** — handle rejections gracefully
- **Database updates** — new Interaction, Pipeline stage updates

## Scenarios Covered

1. **Post-interview positive** — interview went well, waiting for next steps
2. **Post-interview negative (pivot)** — interview with B didn't work, return to A
3. **Timing-based re-engagement** — contact said "reach out when [event]"
4. **Post-rejection (same contact)** — single contact who rejected, but relationship worth maintaining
5. **Dormant warm lead** — previous positive interaction, conversation went cold

## Prerequisites

- Existing database records (Contact, Pipeline, or Interactions)
- Previous message files or meeting notes
- Clear understanding of relationship history

MCP tools:
- `mcp__nocodb__*`
- `WebSearch`

## Quick Start

```
"Follow up with Jane Smith at Acme Renewables"
"Follow up with Jane Smith — she said reach out when the regional team expands"
```

---

## Complete Workflow

### Phase 1: Relationship audit (~5 min)

Step 1 — Pull DB records:
```javascript
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_contacts",
  query: "[Person Name]"
})
mcp__nocodb__search_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  query: "[Person Name]"
})
```

Step 2 — Read existing files:
```javascript
Glob("**/*[person-name]*")
Read("outreach/{user-slug}/messages/company-person.md")
Read("outreach/{user-slug}/prep/company-person-prep.md")
Read("outreach/{user-slug}/analysis/person-meeting-analysis.md")
```

Step 3 — Map the relationship timeline:
- First contact date
- Interview date(s)
- Outcome of each interaction
- Last contact date and method
- Any commitments made by either party

### Phase 2: Context analysis (~5 min)

Questions to answer:
1. What was the original opportunity?
2. What happened since? (interview, rejection, referral, silence)
3. What trigger makes NOW the right time?
4. What's the face-saving framing for both parties?
5. What did they explicitly say about future contact?

If critical information is missing, ASK THE USER:
```
I need additional context to craft the right follow-up:

1. Outcome of last interaction with [Person]?
   □ Positive — waiting for next steps
   □ Referred to someone else
   □ Rejected / not a fit
   □ Went silent

2. Did they make any specific commitments?
   (e.g., "reach out when X", "stay in touch", "will introduce you to Y")

3. Trigger for reaching out now?
   □ Specific timing trigger they mentioned
   □ Company news matches their stated interest
   □ Enough time has passed
   □ Other: ___________

4. Topics to AVOID mentioning?
   (e.g., other contacts, specific interview, rejection reason)
```

### Phase 3: News-hook research (~10 min)

CRITICAL — date validation rules.

**Step 1 — establish cutoff date**:
```
CUTOFF DATE = Last Interaction Date + 1 day
```

**Step 2 — search with date constraints**:
```javascript
WebSearch("[Company] news <current month> <current year>")
WebSearch("[Company] announcement <prior month> <year>")
WebSearch("[Company] [target region] <current month> <year>")
WebSearch("[Company] hiring [role] <current year>")
```

**Step 3 — extract and validate dates**:
For EVERY news item found:
1. Extract the exact date (month + year minimum).
2. Compare to cutoff date.
3. Score freshness:

| News Date vs Last Contact | Score | Action |
|---------------------------|-------|--------|
| Within 14 days of TODAY | Ideal | Use as primary hook |
| 15-30 days old | Good | Use as hook |
| 31-60 days old | Acceptable | Use if nothing fresher |
| Before last interaction | STALE | REJECT — already discussed |
| No date found | UNUSABLE | REJECT — cannot verify |

**Step 4 — document date analysis**:
```markdown
## News Hook Analysis
| News Item | Date Found | Last Contact | Fresh? | Usable? |
```

### Hook validation criteria (ALL must pass)

- [ ] **DATE CHECK**: news occurred AFTER last interaction
- [ ] **FRESHNESS**: ideally within 30 days of today
- [ ] **RELEVANCE**: connects to their stated trigger/interest
- [ ] **SPECIFICITY**: specific enough to reference credibly
- [ ] **NOT ALREADY DISCUSSED**: wasn't mentioned in previous conversations

### NO valid hook found — fallback strategies (in order)

**Fallback 1: their timeline reference**
If they gave a timeline ("over the next year", "Q1", "by end of year"):
```
"You mentioned [timeline] back in [month] — wanted to check in as
that window approaches..."
```

**Fallback 2: time-based acknowledgment**
If significant time has passed (30+ days):
```
"It's been [X weeks] since we spoke about [topic]. Wanted to
reconnect as [reason]..."
```

**Fallback 3: value-led (no news)**
Lead with insight instead of news:
```
"Been thinking about [challenge they mentioned]. Saw a pattern
recently that might be relevant..."
```

**Fallback 4: reuse unused insight from past prep**
```javascript
Read("outreach/{user-slug}/prep/company-person-prep.md")
// Look for "Extended Insights" or insights marked "not discussed".
```

**Fallback 5: industry news affecting them**
```javascript
WebSearch("[Industry] [target region] news <current month>")
```

### Tell the user when no hook exists

If all fallbacks exhausted, explicitly inform the user:
```
NO FRESH NEWS HOOK FOUND

Last interaction: [Date]
News searched: [Date range]
Result: No company news after [cutoff date]

Recommended approach:
□ Wait for news (set alert)
□ Use time-based follow-up (Fallback 2)
□ Lead with value/insight (Fallback 3)

Proceed with a fallback approach? (y/n)
```

### Phase 4: Message crafting (~15 min)

Tone calibration:
- Peer checking in (not applicant)
- Reference specific past moments
- Lead with news/trigger (not "checking in")
- Clear, low-friction ask
- No apologising for reaching out
- No desperation or excessive enthusiasm
- No mention of avoided topics

Message structure (70-90 words):
1. **News Hook** (10-15 words) — specific recent news matching their trigger
2. **Callback** (15-20 words) — specific moment from past conversation (their words, shared insight)
3. **Bridge** (15-20 words) — connect news to what they said about timing (quote their exact words if possible)
4. **Value Add** (15-20 words) — brief insight or offer related to new context
5. **Soft Ask** (10-15 words) — low-friction next step (15-min call, quick catch-up)

### Phase 5: Database updates (~5 min)

Step 1 — create Interaction record:
```javascript
mcp__nocodb__insert_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "interactions",
  data: {
    interaction_type: "Message Drafted",
    interaction_date: "<ISO timestamp>",
    target_contact_id: <contact_id>,
    pipeline_entry_id: <pipeline_id>,
    interaction_summary: "Warm follow-up drafted — [trigger/hook]",
    subject_topic: "[Email subject]",
    details: "Follow-up after [X days]. Trigger: [news/timing]. Hook: [callback]. Avoided: [topics].",
    user_id: ${ACTIVE_USER_ID}
  }
})
```

Step 2 — update Pipeline notes:
```javascript
mcp__nocodb__update_record({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  record_id: "<pipeline_id>",
  data: {
    notes: "[existing notes]\n\n[Date]: Warm follow-up initiated. Trigger: [hook]. Context: [summary]."
  }
})
```

### Phase 6: File creation (~5 min)

File location: `outreach/{user-slug}/messages/[company]-[person]-followup.md`

Include sections:
- Relationship Context (first contact, interviews, last contact, days since, exact quoted commitments)
- Trigger for This Follow-Up (news hook, connection to their words, why now)
- Topics to Avoid
- Email Subject Line + alternatives
- Message Draft (word count)
- Callback References Used
- If They Respond Positively (topics to discuss, topics to avoid)
- If No Response: Follow-Up #2 (wait 7-10 business days, different angle, same warmth)

---

## Scenario-Specific Guidance

### Post-interview positive (waiting)
- Wait time: 5-7 business days
- Tone: confident, not anxious
- Hook: reference specific conversation moment + news
- Ask: "Any updates on timing?"

### Post-interview negative (return to sponsor)
- Wait time: match their stated trigger
- Tone: fresh start, no dwelling on past
- Hook: news matching their trigger statement
- Avoid: mentioning the rejection or other contact
- Ask: 15-minute catch-up, not job discussion

### Timing-trigger re-engagement
- Quote their exact words if possible
- Connect news to trigger explicitly
- Tone: "You mentioned X, and I see X is happening"

### Dormant warm lead
- Acknowledge time briefly ("It's been a few months")
- Lead with value (news/insight, not relationship maintenance)
- Lower friction (shorter ask, easier commitment)

---

## Quality Checklist

Before sending:
- [ ] Relationship history reviewed
- [ ] News hook found and validated (date check passed)
- [ ] Their exact words/commitments referenced
- [ ] Tone is warm and peer-level
- [ ] No mention of avoided topics
- [ ] Ask is low-friction and specific
- [ ] Message is 70-90 words
- [ ] Database updated
- [ ] File created with full context

---

## Mandatory: self-evaluation before delivery

After drafting, STOP and evaluate:

**Check 1: hook freshness** — is the news hook dated AFTER the last interaction?
**Check 2: would they care?** — would they think "this is old news" or "oh interesting, this just happened"?
**Check 3: tone test** — desperate job seeker vs. peer with relevant observations?
**Check 4: specificity test** — vague references vs. specific dates and quotes?

If ANY check fails → ITERATE. Do not deliver. Return to Phase 3 or use a fallback approach.

---

## Reference Documentation

- Operating procedures: `operating-procedures/`
- Meeting analysis examples: `outreach/{user-slug}/analysis/`
- Rules: `.claude/rules/`
