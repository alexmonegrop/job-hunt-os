# Cold Outreach Operating Procedure v4.0

**Last Updated**: 2026
**Document type**: Reference (for humans + AI agents). For automatic enforcement, see `.claude/rules/`.

**Purpose**: Complete cold-outreach workflow from company selection through message sending and follow-up.

**Companion rules**: `01-database-standards.md`, `02-message-quality-standards.md`, `03-batch-operations-rules.md`, `05-file-organization-rules.md`.

---

## Version History
- **v4.0**: Elevated quality bar — deep-research dossiers + practitioner insights + peer framing + zero job-seeking language. Application-adjacent networking and contact-discovery tooling added.
- **v3.x**: Batch processing (50% time reduction), one file per person, file naming.

## What Changed in v4.0

### The problem with v3
v3 messages plateau because they read templated — generic regional insights, advisor positioning, news hooks anyone could send.

### The v4 approach
**Reference specific things the contact said publicly. Use practitioner insights from real experience. Position as peer, never advisor. Zero job-seeking language.**

### Quality comparison

| Element | v3 (Good) | v4 (Elevated) |
|---------|-----------|---------------|
| Hook | Company news ("Congrats on Series B") | Personal statement they made on a named source |
| Insight | Market pattern ("regional X paradox") | Practitioner observation from daily usage / building |
| Evidence | Competitor example ("[Competitor] in [region]") | First-person experience using / building the thing |
| Credibility | Title drop ("At [Past Co] with [Flagship Client]") | Natural weave of builder credentials |
| Ask | "15 minutes to share what's working?" | "Worth 15 minutes to compare notes?" (peer) |
| Positioning | Advisor with regional expertise | Practitioner with relevant production experience |
| Job intent | Implied but visible | Completely invisible |

### When to use which tier
- **v3 approach**: regional-expansion companies where the user's regional expertise IS the value
- **v4 approach**: tech / product / domain companies where the user has genuine practitioner experience with their product

---

## STEP 0: Deep Research Protocol (NEW in v4)

### Build a research dossier before drafting any message

Minimum research per contact (~15-20 min):

#### 1. Career arc (~5 min)
```
WebSearch "[Name] [Company] LinkedIn"
WebSearch "[Name] career history"
```
Extract: current role + scope (team size, what they own); previous companies (pattern: what trajectory?); key transitions (what themes recur?).

#### 2. Public statements (~10 min)
```
WebSearch "[Name] podcast interview"
WebSearch "[Name] [Company] blog post"
WebSearch "[Name] conference talk"
WebSearch "[Name] quote" site:linkedin.com
```
Find at least ONE specific thing they said publicly. Note their exact language. Use their vocabulary back to them. Look for tensions between what they say and what's hard.

#### 3. Key tensions (~5 min)
- What does their role / company need that's hard to deliver?
- Where does their public narrative create operational tension?
- What are they NOT saying that matters?

### Research dossier template

```markdown
## Deep Research Dossier

### Career Arc
- **Current**: [Role] at [Company] ([Scope])
- **Previous**: [Key companies and roles]
- **Pattern**: [Career theme]

### Public Statements (Sourced from [Named Source])
- [Specific quote or position with source]
- [Another specific insight with source]

### Key Tensions
- [Tension 1]: [Why this creates a conversation opportunity]
- [Tension 2]: [How the user's experience relates]
```

CRITICAL: if you can't find anything specific the person said publicly, research their COMPANY's public statements and reference those instead. Never send a generic message.

---

## STEP 1: Company Selection from the Database

```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "target_companies",
  where: "(tier,eq,Tier 1 - Highest Priority)~or(tier,eq,Tier 2 - High Priority)",
  limit: 25,
  sort: "-research_date"
})
```

Selection criteria (priority order):
1. **Application-adjacent**: companies where the user already applied (adds human-connection layer).
2. **Recent signals**: news/announcements in last 30 days.
3. **Strong fit alignment**: clear connection to user's `credibility_anchors[]`.
4. **Geographic match**: in `target_regions[]` or expanding into them.

### Application-adjacent networking

Always check if the company has active applications before outreach:
```javascript
mcp__nocodb__list_records({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "applications",
  where: "(company_id,eq,<company_id>)~and(application_status,neq,Rejected)",
  limit: 10
})
```

If an active application exists:
- Outreach should NEVER mention the application.
- Position as genuine interest in their work / product.
- The application creates urgency; the message creates relationship.
- After a positive response, mention the application only if asked.

---

## STEP 2: Contact Selection

Find the best contacts per company (see `04-contact-selection-priorities.md` for size-based composition rules).

### v4 contact prioritisation

In addition to role / seniority criteria:
1. **Has public content** — they've written, spoken, or posted something findable (strongest messages reference their words).
2. **Direct product / domain alignment** — they work on something the user has built / used / deployed.
3. **Peer-level credibility** — their background creates natural conversation (both founders, both builders, both PMs).
4. **Recent activity** — active on LinkedIn in the last 30 days.

### Contact-information discovery (optional tools)

- **Apollo.io** (free credits): search by company + role; reveals email + phone; good when LinkedIn DM unavailable.
- **ContactOut** (Chrome extension): works on LinkedIn profile pages; reveals personal email + phone.

Preferred channels (priority):
1. **LinkedIn DM** — best for initial outreach.
2. **Email** — for senior contacts who may not check LinkedIn.
3. **Twitter / X DM** — for tech / product people active there.

---

## STEP 3: Create Database Records

Per `01-database-standards.md`, create Pipeline + Interaction records together (Rule 2).

```javascript
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "sales_pipeline",
  records: [
    {
      pipeline_name: "Contact Name - Company",
      contact_id: 101,
      company_id: 5,
      pipeline_stage: "1. Research",
      temperature: "Cold",
      notes: "Batch <date>. [Key hook/insight]",
      user_id: <active_user_id>
    }
    // ...
  ]
})

// After capturing pipeline IDs:
mcp__nocodb__bulk_insert({
  base_id: "${NOCODB_BASE_ID}",
  table_name: "interactions",
  records: [
    {
      interaction_type: "Message Drafted",
      interaction_date: "<ISO timestamp>",
      target_contact_id: 101,
      pipeline_entry_id: 201,
      interaction_summary: "Initial outreach drafted",
      subject_topic: "Email subject line",
      user_id: <active_user_id>
    }
    // ...
  ]
})
```

Always batch-duplicate-check first (Rule 5).

---

## STEP 4: Message Creation (Elevated Quality Bar)

### The v4 message formula

**Structure**: Deep Hook → Practitioner Insight → Builder Credibility → Peer Ask

#### Part 1: Deep Hook (10-15 words)
**Reference something THEY specifically said or did** — not just company news.

| Source | Example |
|--------|---------|
| Podcast | "Your point on [Host]'s podcast about [topic] resonated." |
| Blog post | "Your [Company] blog on [topic] — [specific observation]" |
| LinkedIn post | "Your post about [topic] — [genuine reaction]" |
| Conference talk | "Your [Event] talk on [topic] — [specific insight]" |
| Product they built | "I built [thing] with [product you created]" |

If no personal content found, reference a specific company initiative with detail showing genuine knowledge.

#### Part 2: Practitioner Insight (25-35 words)
**Show you've DONE the work, not just observed it.**

| v3 (Observer) | v4 (Practitioner) |
|---------------|-------------------|
| "Pattern I've noticed: [region] wants proven-elsewhere" | "I built a production SaaS using [product] for ~90% of the code" |
| "Most companies find that stakeholder multiplication stalls scaling" | "Three months of daily use surfaced clear patterns about where the collaboration model breaks" |
| "[Competitor] spent 18 months discovering this" | "Managing 15 concurrent projects across 5 [region] countries taught me where the coordination model fails" |

Key principle: first-person experience > third-person observation > industry pattern.

#### Part 3: Builder Credibility (15-20 words)
**Specific, quantified, naturally woven — never a title drop.**

Good: "14 years helping enterprises adopt emerging tech taught me where the adoption gap will hit."
Bad: "As a former Program Manager at [Past Co]..."

Good: "Built production search systems (semantic search with vector embeddings and RAG pipelines)"
Bad: "I have experience with AI/ML technologies"

#### Part 4: Peer Ask (10-15 words)
**"Compare notes" framing — never "pick your brain" or "learn from you."**

| v3 Ask | v4 Ask |
|--------|--------|
| "15 minutes to share what's working?" | "Worth 15 minutes to compare notes?" |
| "Happy to share the playbook" | "Worth connecting as fellow [role]s?" |
| "15 minutes to discuss how to avoid the trap?" | "Worth 15 minutes of feedback from someone building real things with your [product]?" |

### Word count: 70-90 (same as v3)

### Zero job-seeking language

NEVER include in any outreach message:
- "I'm exploring opportunities"
- "Your team is hiring"
- "I noticed the [role] opening"
- "I'd love to be part of"
- "I'm available for"
- "My background makes me a fit for"

The message should read identically whether you've applied or not.

---

## STEP 5: Follow-Up Strategy (Elevated)

### Follow-Up #1 (5-7 business days): add new value

Don't just "circle back". Provide a SPECIFIC, USEFUL observation they can't get elsewhere.

Examples:
- "Quick specific example: [real experience detail that expands on original message]"
- "One pattern from [specific project]: [observation that adds value]"
- Offer something concrete: "Built a [tool / framework / system] that solved this. Happy to share."

### Follow-Up #2 (7-10 business days after #1): last note + compliment

Keep it brief (2-3 sentences). Reference their public work positively. "Here if a conversation would be useful." No pressure, no guilt.

### Follow-up rules
- Maximum 2 follow-ups (3 total touches including initial)
- Each follow-up must add new value — never just "following up"
- If no response after 3 touches: move on, revisit in 3-6 months with new context

---

## STEP 6: File Creation (ONE FILE PER PERSON)

**Location**: `outreach/{user-slug}/messages/`
**Naming**: `{company}-{firstname}-{lastname}.md`

File structure (full template in `.claude/rules/05-file-organization-rules.md`).

In v4, include the Deep Research Dossier section (career arc, public statements, key tensions) ahead of the message body.

---

## Batch Processing Workflow

### Phase 1: Company research & dossier building (~25 min for 5 companies)
- Research all 5 companies deeply
- Build dossier for each top contact
- Find public statements / content for each contact
- Develop practitioner angles

### Phase 2: Contact selection & discovery (~10 min)
- Select top 3 contacts per company
- Run Apollo / ContactOut for email discovery (optional)
- Batch duplicate check in the database

### Phase 3: Database records (~5 min)
- `bulk_insert` pipeline records
- `bulk_insert` interaction records

### Phase 4: Message drafting & file creation (~20 min)
- Draft all messages using dossiers from Phase 1
- Create individual files (ONE PER PERSON)
- Verify 70-90 word count
- Cross-check for repetitive language

**Total**: ~60 min for 15 contacts (vs ~45 min for v3 — significantly higher quality).

---

## Message Quality Checklist (v4)

Before sending ANY message:
- [ ] References something specific about THEM (not just their company)
- [ ] Shows practitioner experience (not observer insight)
- [ ] Uses peer framing ("compare notes" not "share the playbook")
- [ ] Zero job-seeking language
- [ ] Quantified credibility (numbers, names, scale — not just titles)
- [ ] 70-90 words (counted, not estimated)
- [ ] Follow-ups add new value (not just "following up")
- [ ] Deep research dossier completed (career arc + public statements + tensions)

---

## When the v3 Insight Approach Still Works

The v3 approach (regional market insights, counter-intuitive regional truths) remains effective for:
- **Regional-expansion companies** where the user's regional expertise IS the differentiator.
- **Contacts without public content** where the practitioner angle isn't possible.
- **Regional operations roles** where market knowledge matters more than product experience.
- **Government / semi-government** connections where regional dynamics drive the conversation.

**Rule**: use the highest-quality approach the research supports. v4 when you can find personal content; v3 when you can't.

---

## The Golden Rules v4.0

1. Always research the person deeply before writing (career arc + public statements).
2. Always reference something specific about THEM (not generic company news).
3. Always show practitioner experience (you've done it, not just observed it).
4. Always use peer framing ("compare notes" not "share insights").
5. Never use job-seeking language (zero mentions of roles, openings, applications).
6. Never give away the full solution (leave them wanting more).
7. Always keep to 70-90 words (verified count).
8. Always create individual files (one per person, never batch).
9. Always check for existing applications before outreach (application-adjacent networking).
10. Each follow-up must add new specific value (never just "following up").

---

## Supporting Documents

- `.claude/rules/02-message-quality-standards.md` — automated quality enforcement
- `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md` — worked examples
- `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md` — 15-minute insight process
