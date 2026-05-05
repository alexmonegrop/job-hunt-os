# Meeting Preparation Procedure v4.0

**Document type**: Reference (for humans + AI agents). For automatic enforcement, see `.claude/rules/`.

**Purpose**: Systematic preparation for 15-minute meetings (max 1 hour prep time). Deliver unique insights that make them immediately want you involved.

**Companion**: skill `meeting-prep`.

## Critical Success Factors

The formula that works:
1. Recent news reference (establishes relevance)
2. Vulnerability sharing (accelerates trust)
3. Natural conversation (not lecturing)
4. Intelligence extraction (learn more than you share)
5. Specific next steps (calendar, not "let's connect")

## Core Objective

Every person must leave the call thinking: *"This person understands our specific challenges better than anyone else I've talked to. I need them involved."*

How: deliver 2-3 non-obvious insights about their specific situation that demonstrate:
1. You understand their hidden challenges (not just surface goals)
2. You have relevant experience solving those exact challenges
3. You can add immediate value to their current priorities

## Pre-Meeting News Check (Day Before)

Strike while hot:
1. **Check for breaking news** (24 hours before):
   ```javascript
   WebSearch("[Company] latest news today OR yesterday")
   ```
2. **Update your hook** if major news broke.
3. **Adjust insights** if new developments shift priorities.

Why: shows you're tracking in real time; creates immediate relevance; may reveal urgent new pain points.

## Inputs Required

- Person's name (full)
- Company name
- Outreach message file path
- Meeting date / time
- Meeting duration (default: 15 min)
- **Meeting format** (office / video / transit / meal) — drives different prep strategies

## Meeting Environment Contingency Planning

### Formal office / video (traditional)
- Full prep with all materials ready
- Screen share capability for frameworks
- Note-taking visible
- Professional backdrop
- All 3 insights ready to deliver

### Transit / walking meeting (busy executive)
- 3 must-hit points memorised (no notes)
- Story-based delivery (easier while moving)
- Key numbers memorised
- Shorter, punchier insights
- Voice clarity paramount

### Meal setting (relationship focus)
- Defer detailed discussions ("Let's dig into that after lunch")
- Focus on rapport and trust building
- Save technical details for follow-up
- Use napkin / simple visuals if needed
- Vulnerability moments work best here

### Time extension (meeting goes long)
- Have 2x content ready (5-6 insights, not just 3)
- Deeper-dive materials on each insight
- Additional war stories / examples
- Specific implementation ideas
- Partnership / collaboration angles

### Time compression (cut short)
- 3 must-hit points identified (30 seconds each)
- One-line versions of each insight
- Single most important question to ask
- Clear ask ready ("Can we schedule 30 minutes next week?")

## Data Gathering Process

### STEP 1: Review your outreach message
Extract: insights you promised; value proposition you offered; what they might ask about. Note any specific hooks or angles used.

### STEP 2: LinkedIn profile data
WebFetch their profile. Extract: current role + scope; recent activity (last 30 days); career arc.

### STEP 3: Company deep dive
Read the company's `why_strong_fit` and `recent_signals` from the database. Pull recent news (last 30 days). See `company-deep-dive` skill if interview prep depth is needed.

### STEP 4: Competitive intelligence
Who do they fear? What did similar companies fail at?
```
WebSearch "[Competitor] [similar initiative] lessons learned"
WebSearch "[Industry] [region] challenges failures"
```

### STEP 5: Industry / regional pattern research
What typically goes wrong? What worked / failed regionally?

### STEP 6: Person's recent activity
Their LinkedIn posts, blog posts, podcast appearances. Specific things they've said publicly.

### STEP 7: Strategic vulnerability identification

Purpose: prepare authentic challenges to share that build trust.

Find your relevant "schlep at scale" moments:
1. What similar challenge did you face?
2. What made it harder than expected?
3. What did you learn the hard way?
4. What would you do differently?

Package as relatable vulnerability:
- "We underestimated [X] at [Past Company]"
- "The hardest part was actually [unexpected challenge]"
- "Took us [time] to figure out [non-obvious solution]"
- "Failed twice before we realised [key insight]"

Pull from `master-experience.yaml` bullets tagged `challenge_story` or `lesson_learned`.

**Timing**: share AFTER they reveal a challenge, not before.

### STEP 8: Develop unique insights (2x content model)

#### Core 3 insights (must-hit points)
Non-negotiables — must be delivered even if meeting cut to 5 minutes.

#### Extended 3 insights (if time allows)
Have these ready for when meeting extends or they ask for more.

For each insight:
1. **30-second version** — ultra-concise for time pressure
2. **Full version** — complete with evidence
3. **Vulnerability bridge** — your related challenge ("At [past company] we underestimated X")
4. **Extraction question** — test their understanding ("How are you thinking about [specific challenge]?")
5. **If resonates, go deeper** — extended talking points

Insight development process:
1. Their public goal (what they announced)
2. Hidden challenge (what will actually be hard)
3. Pattern (similar companies that faced this)
4. Counter-intuitive truth (what most get wrong)

See `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md` for the 15-minute insight development process.

## Intelligence Extraction Framework

### Question categories

**Constraint** (reveals bottlenecks):
1. "What's constraining your growth / expansion right now?"
2. "If you had unlimited resources, what would you fix first?"
3. "What's taking longer than expected?"

**Surprise** (reveals blind spots):
1. "What's been the biggest surprise so far?"
2. "What's different from what you expected?"
3. "What would you tell yourself six months ago?"

**Competition** (reveals positioning):
1. "How do you see the competitive landscape evolving?"
2. "What advantages do you have that others don't?"
3. "What are competitors doing that concerns you?"

**Timeline** (reveals pressure):
1. "What needs to happen in the next 90 days?"
2. "What milestones are non-negotiable?"
3. "When do you need to show results?"

**Stakeholder** (reveals complexity):
1. "Who else needs to be convinced?"
2. "Where does the budget come from?"
3. "Who could block this if they wanted to?"

### The golden question
**"What keeps you up at night about this?"** Opens the door to real challenges, invites vulnerability, shows you care about their success.

## Next-Step Conversion Tactics

### Convert interest to concrete action

Instead of vague:
- "Let's connect again"
- "I'll follow up"
- "Interested in chatting more"

Get specific:
- "Can we calendar 30 minutes next Tuesday?"
- "Should I send availability for this week?"
- "Would Thursday 2pm work for a deeper dive?"

### Commitment ladder
Start high, have fallbacks:
1. **Best**: "Let me introduce you to my team" → group call
2. **Good**: "Let's dive deeper next week" → calendar specific time
3. **OK**: "Send me more information" → promise framework + follow-up time
4. **Minimum**: "Keep in touch" → set specific check-in date

### Creating urgency without pressure
- "I'm in [their city] next week if helpful"
- "We're making a decision on focus by [date]"
- "I have bandwidth for one more engagement this quarter"
- "The framework I mentioned is ready — should I send it today?"

## Prep Document Output

**Location**: `outreach/{user-slug}/prep/[company]-[person]-prep.md`

The full template lives in the `meeting-prep` skill. Key sections:
- 3 Must-Hit Points (if cut short)
- Meeting Environment Strategy
- Quick Reference (2-min scan)
- Your Unique Insights (Core 3 + Extended 3)
- Meeting Flow by Duration (5 / 15 / 30+ min)
- Vulnerability Moments
- Intelligence Extraction Plan
- Post-Meeting Actions
- Next-Step Conversion

## Post-Meeting Actions

### Within 30 minutes
1. Send thank-you referencing specific moment
2. Confirm any commitments
3. Share promised resources

### Within 2 hours
1. Create / send 2-page framework discussed
2. Calendar follow-up if agreed
3. Update database with intelligence gathered

### Within 24 hours
1. LinkedIn connection if not connected
2. Introduction requests if offered
3. Prep for next conversation based on learnings

## Contingency Responses

- Running late / Uber / walking: "No problem at all — should we do this on the move? I've got my key points memorised."
- They're distracted: "Seems like a crazy day — want to do this when you have more bandwidth?"
- They want to go deeper: "I've got time if you do — this is fascinating."
- They reveal a major challenge: "We faced exactly this at [past company] — [vulnerability share]"
- They seem skeptical: "Let me send you a framework we developed for this — see if it resonates."

## Success Metrics

### During meeting
- [ ] Referenced recent news
- [ ] Shared a vulnerability moment
- [ ] Extracted 3+ intelligence points
- [ ] Delivered at least 2 insights
- [ ] Got specific next step

### Quality indicators
- They said "exactly" or "that's our challenge"
- They asked your opinion on something
- They revealed non-public information
- They extended the meeting time
- They offered to introduce you to others

## Implementation Checklist

For your next meeting prep:
1. [ ] Check news 24 hours before
2. [ ] Prepare for actual meeting format
3. [ ] Create 6 insights (3 core + 3 extended)
4. [ ] Prepare 2-3 vulnerability shares
5. [ ] Write 30-second versions of must-hit points
6. [ ] List 10+ extraction questions
7. [ ] Practice specific next-step asks
8. [ ] Create 2-page leave-behind framework (optional)
