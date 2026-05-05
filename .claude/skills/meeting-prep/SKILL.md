---
name: "meeting-prep"
description: "Systematic meeting preparation for 15-minute job-hunt meetings (max 1 hour prep time). Generates comprehensive prep documents with 6 unique insights (3 core + 3 extended), vulnerability sharing strategy, intelligence-extraction questions, and next-step conversion tactics. Includes meeting environment strategies (office/transit/meal), 3 must-hit points for compressed meetings."
---

# Meeting Prep

Automated meeting preparation system optimised for 15-minute meetings with max 1-hour prep time.

## What This Skill Does

- **Comprehensive research** — outreach message review, LinkedIn profiles, company news
- **Insight development** — 6 insights (3 core + 3 extended)
- **3 must-hit points** — 30-second versions for compressed meetings
- **Vulnerability strategy** — prepare authentic challenges to share
- **Intelligence extraction** — 10+ questions to learn more than you share
- **Environment strategies** — office / transit / meal
- **Next-step conversion** — get specific commitments, not vague "let's connect"
- **Prep document** — complete markdown file with research and strategies

## Prerequisites

- Outreach message file at `outreach/{user-slug}/messages/[company]-[person].md`
- Operating procedures at `operating-procedures/`

MCP tools:
- `WebSearch` (research and news checking)
- `WebFetch` (LinkedIn profiles, company pages)

## Quick Start

```
"Prepare meeting with Jane Smith from Acme Renewables"
"Prepare meeting prep for Bob Jones — Initech, meeting Tuesday 2pm"
```

---

## Complete Workflow

### Step 1: Review outreach message (~5 min)

1. Read the outreach message file.
2. Extract: insights you promised, value proposition you offered, what they might ask about.
3. Note any specific hooks or angles used.

### Step 2: Pre-meeting news check (~5 min)

CRITICAL — check 24 hours before meeting for breaking news:
```javascript
WebSearch("[Company] latest news today OR yesterday")
```

If major news: update opening hook to reference it.

### Step 3: Research batch (~30 min)

Single research session (batch approach):
```javascript
WebSearch("[Person Name] LinkedIn")
WebSearch("[Company] recent news <current and prior year>")
WebSearch("[Company] [target region] expansion")
WebSearch("[Company] [specific initiative from news]")
WebSearch("[Industry] [target region] challenges failures")
WebSearch("[Competitor] [similar initiative] lessons learned")
```

Research focus:
- Person's recent LinkedIn activity (last 30 days)
- Company news (last 30 days)
- Competitive intelligence (who they fear, what others failed at)
- Industry patterns (what typically goes wrong)
- Regional precedents (what worked / failed in target region)

### Step 4: Develop 6 insights (~20 min)

**Core 3 (must deliver)** — even if cut to 5 minutes.

For each insight:
1. **30-second version** (ultra-concise for time pressure)
2. **Full version** (complete with evidence)
3. **Vulnerability bridge** (your related challenge — pull from `applications/resumes/data/{user-slug}/master-experience.yaml` flagged challenge bullets)
4. **Extraction question** (test their understanding)
5. **If resonates, go deeper** (extended talking points)

**Extended 3** — prepared but not essential, for when meeting extends to 30+ minutes.

Insight development process:
1. Their public goal (what they announced)
2. Hidden challenge (what will actually be hard)
3. Pattern (similar companies that faced this)
4. Counter-intuitive truth (what most get wrong)

Use `operating-procedures/QUICK-INSIGHT-DEVELOPMENT-GUIDE.md` for the 15-minute process.

### Step 5: Prepare vulnerability shares (~5 min)

Identify 2-3 authentic challenges from the user's resume YAML (look for bullets tagged `challenge_story` or `lesson_learned` in `master-experience.yaml`).

Examples (illustrative — generate from user's actual experience):
- "[Past employer]'s [region] expansion was harder than expected — the talent wasn't there."
- "[Project] taught me stakeholder alignment takes 3x longer than the work."
- "At [startup], we learned 90-day adoption windows are fantasy in enterprise."

Timing: share AFTER they reveal a challenge, not before.

### Step 6: Create intelligence-extraction plan (~5 min)

Must-learn items:
- Actual constraints (people, money, time, politics)
- Real timeline (not the public version)
- Decision process (who, how, when)
- Competition concerns (who they fear)
- Success metrics (how they're measured)

Question categories:
- **Constraint**: "What's constraining growth right now?"
- **Surprise**: "What's been the biggest surprise so far?"
- **Competition**: "How do you see the competitive landscape?"
- **Timeline**: "What needs to happen in the next 90 days?"
- **Stakeholder**: "Who else needs to be convinced?"

Golden question: "What keeps you up at night about this?"

### Step 7: Generate prep document (~10 min)

Output: `outreach/{user-slug}/prep/[company]-[person]-prep.md`

```markdown
# Meeting Prep: [Person Name] - [Company Name]
**Meeting Date**: [Date/Time] | **Duration**: 15 minutes | **Format**: [Office/Video/Transit/Meal]
**Prepared**: [Date] | **Last News Check**: [Date/Time]

---

## 3 Must-Hit Points (If Meeting Cut Short)
1. [30-second version of best insight]
2. [30-second version of second insight]
3. [30-second version of third insight]

---

## Meeting Environment Strategy
**Setting**: [Office/Video/Transit/Meal]
**Approach**: [Specific strategy]
**Materials**: [What you can/cannot use]
**Delivery Style**: [Formal/Conversational/Story-based]

---

## Quick Reference (2-Minute Scan)

### What [Company] Does
[1-2 sentences]

### Person Overview
- **Role**: [Title] (since [Date])
- **Recent Win**: [Achievement]
- **Strategic Focus**: [Priorities]

### Recent Company Signals
- [Date]: [News]

### Your Outreach Hook
- [What you emphasized]
- [Value proposition]

---

## Your Unique Insights (Core 3 + Extended 3)

### PRIMARY SET (Must Deliver)

#### Insight #1: [Title]
- **30-Second Version**: [Ultra-concise]
- **Full Version**: [Complete with evidence]
- **Vulnerability Bridge**: [Your related challenge]
- **Extraction Question**: [Test understanding]
- **If Resonates**: [Extended points]

[Repeat for #2 and #3]

### EXTENDED SET (If Time Allows)
[#4, #5, #6 with same structure]

---

## Meeting Flow by Duration

### If 5 minutes (compressed)
0:00-0:30   Quick rapport
0:30-4:00   Three must-hit points
4:00-5:00   Get commitment for full discussion

### If 15 minutes (standard)
0:00-2:00   Opening & rapport
2:00-8:00   Core discussion & extraction
8:00-13:00  Deliver insights with vulnerability
13:00-15:00 Next steps with specificity

### If 30+ minutes (extended)
0:00-3:00   Deeper rapport building
3:00-10:00  Thorough challenge exploration
10:00-20:00 All 6 insights with discussion
20:00-25:00 Partnership exploration
25:00-30:00 Concrete next steps

---

## Vulnerability Moments

### Prepared Shares
1. [Challenge story]
2. [Failure learning]
3. [Humility moment]

**When to deploy**: after they share, when too theoretical, to create connection.

---

## Intelligence Extraction Plan

### Must-learn
- [ ] Constraints
- [ ] Real timeline
- [ ] Decision process
- [ ] Competition concerns
- [ ] Success metrics
- [ ] Political dynamics

### Questions
[10+ specific questions]

---

## Post-Meeting Actions

### Within 30 minutes
1. Send thank-you referencing specific moment
2. Confirm commitments
3. Share promised resources

### Within 2 hours
1. Create/send framework discussed
2. Calendar follow-up if agreed
3. Update database

---

## Next-Step Conversion

Instead of vague:
- "Let's connect again"

Get specific:
- "Can we calendar 30 minutes next Tuesday?"
- "Should I send availability for this week?"
- "Would Thursday 2pm work for a deeper dive?"

**Commitment Ladder**:
1. Best: "Let me introduce you to my team" → group call
2. Good: "Let's dive deeper next week" → calendar time
3. OK: "Send more information" → framework + follow-up time
4. Minimum: "Keep in touch" → specific check-in date
```

---

## Meeting Environment Strategies

### Office / video (traditional)
- Full prep with all materials
- Screen-share capability
- All 3 insights ready
- Professional backdrop

### Transit / walking (busy exec)
- 3 must-hit points memorised (no notes)
- Story-based delivery
- Key numbers memorised
- Shorter, punchier insights

### Meal (relationship focus)
- Defer detailed discussions
- Focus on rapport and trust
- Save technical for follow-up
- Vulnerability moments work best

---

## Quality Checklist

Before meeting:
- [ ] Outreach message reviewed
- [ ] News check completed (24 hours before)
- [ ] 6 insights prepared
- [ ] 3 must-hit points ready
- [ ] Vulnerability shares prepared
- [ ] 10+ extraction questions ready
- [ ] Prep document created

During meeting:
- [ ] Referenced recent news
- [ ] Shared a vulnerability moment
- [ ] Extracted 3+ intelligence points
- [ ] Delivered at least 2 insights
- [ ] Got a specific next step

---

## Reference Documentation

- Full workflow: `operating-procedures/MEETING-PREP-PROCEDURE-v4.md`
- Insight development: `operating-procedures/QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`
