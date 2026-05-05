# Message Quality Standards

## CRITICAL: 70-90 Word Count

**Target**: 70-90 words
**Sweet spot**: 75-85 words
**Too short (<70)**: Add credibility details or expand geographic context
**Too long (>90)**: Trim fluff, combine sentences, remove redundancy

**Quick estimation**: Target 5-6 sentences total (each ~12-15 words).

## Message Structure (ALWAYS follow this 6-part formula)

### 1. News Hook (5-10 words)
- Reference specific recent news (last 30 days)
- Congratulate or acknowledge
- Examples: "Congrats on the Series B", "Saw the [region] office announcement"

### 2. Unique Insight (20-30 words)
- Counter-intuitive truth that challenges assumptions
- Pattern from competitor failures
- Regional reality
- Must surprise them with something non-obvious

### 3. Evidence/Pattern (10-15 words)
- Specific company example
- Industry statistic
- Regional precedent
- Examples: "[Competitor] learned this after 18 months", "[Big consultancy] discovered this three projects in"

### 4. Your Credibility (10-15 words)
- Specific company names (not just titles)
- Relevant achievement
- Geographic presence
- Pull from `config/user-profile.yaml` `credibility_anchors[]` and `applications/resumes/data/{user-slug}/master-experience.yaml`

### 5. Geographic Flexibility (5-10 words)
- Current location
- Flexibility across target region
- Pull from `config/user-profile.yaml` `location` and `target_regions[]`

### 6. Soft Ask (10-15 words)
- "15 minutes to discuss..."
- Value-focused (not job-seeking)
- Examples: "15 minutes to share the playbook?", "Worth a quick call to discuss?"

## Insight Quality Checklist (MUST score 4+/5)

Before using an insight, verify:
- [ ] **Counter-intuitive**: Challenges common assumption
- [ ] **Specific**: About their exact situation (not generic)
- [ ] **Evidenced**: Has proof/examples
- [ ] **Relevant**: Applies to their context
- [ ] **Valuable**: Would save time/money/pain
- [ ] **Incomplete**: Leaves them wanting more (don't give full solution)
- [ ] **Credible**: You have authority to know this

## Insight Formulas That Work

**Formula 1: The Competitor Failure**
```
"[Competitor] spent [time/money] discovering that [counter-intuitive truth].
[Your experience] taught me [solution approach]."
```

**Formula 2: The Industry Pattern**
```
"[X]% of [industry] companies fail at [specific point] because [non-obvious reason].
At [your company], we avoided this by [approach]."
```

**Formula 3: The Regional Reality**
```
"In [region], [common approach] fails because [local dynamic].
[Your experience] showed that [alternative approach] works."
```

**Formula 4: The Hidden Challenge**
```
"Most assume [obvious challenge], but in [region] it's actually [non-obvious challenge].
[Company X] learned this the hard way in [Year]."
```

## Subject Line Format

**Formula**: `[Company Initiative] - [Why/What/Pattern]`

**Examples (generic, replace with your industries/regions)**:
- "[Region] AI Expansion - Why 3 Competitors Stalled"
- "[Region] Partnership - The Hidden Stakeholder Map"
- "Series B Scaling - The [Region] Talent Paradox"
- "Government Contract - The 90-Day Adoption Trap"

**Avoid**:
- "Interested in connecting"
- "Quick question"
- "Following up"

## Operational Tension as Insight Source (Proven Pattern)

**Focus on what creates tension/paradox, not celebrating success**:

### Regulatory vs Growth Velocity
- "[Compliance regime] documentation slows deployment velocity despite enabling [strategic goal]"
- "Local content requirements extend timelines 40-60% beyond technical complexity"
- "Government approval cycles change project economics before internal approval completes"

### Compliance Mandates vs Market Timing
- "Carbon credit purchasing follows compliance deadlines, not continuous measurement capability"
- "Enterprises buy for audit requirements, not [stated public goal]"
- "Regulatory clarity increases complexity through regional interpretation differences"

### Technical Capability vs Organizational Readiness
- "[Architecture pattern] requires security that conflicts with [user-experience expectation]"
- "Platform technology ready, but enterprise purchasing follows crisis cycles, not preventative adoption"
- "AI capability advances faster than supply-chain data maturity"

### Marketing Narrative vs Operational Reality
- "[Tech X] enables [outcome Y], but marketing emphasizes [outcome Z]"
- "Leadership development creates ecosystem value but retention challenges when competitors poach"
- "Partnership velocity creates coordination debt, not execution capacity"

### Strategic Positioning vs Market Reality
- "[Sovereign tech] narrative creates market fragmentation, not technology differentiation"
- "Export licenses turn technical advantage into geopolitical dependency"
- "[Newer business line] overshadowed by legacy revenue stream"

**Formula**: Find the "X creates Y problem, not Z benefit" paradox in their operations.

**Research Years**: Use the current year AND prior year in search queries (recent news spans both).

## Counter-Intuitive Insights by Industry

These are illustrative seeds. Customise per your `config/industries.yaml` vocabulary.

### AI/Tech Companies
- "[Region] wants proven-elsewhere, not cutting-edge"
- "Ministry KPIs conflict — Transport wants less traffic, Tourism wants more"
- "POCs succeed, but scaling fails at stakeholder multiplication"

### Consultancies
- "Local partners become competitors, not enablers"
- "Government timelines are suggestions; milestones are law"
- "The real decision-maker is never on the org chart"

### Startups
- "First-mover disadvantage is real in [emerging market]"
- "Regulation follows success, not precedes it"
- "B2G becomes B2B2G through necessity"

### Scale/Growth Companies
- "Talent follows proven success, not promising opportunity"
- "3x the timeline, 0.5x the initial scope"
- "Adjacent ministry approval takes longer than primary"

## Tone Requirements

### NEVER:
- Use emojis (unless user explicitly requests)
- Sound like you're lecturing
- Give away full solution
- Make claims without evidence
- Focus on technology when problem is human
- Say "I'd love to connect" or "looking for opportunities"

### ALWAYS:
- Position as peer/advisor
- Leave them wanting more
- Frame as "pattern I've observed"
- Back up with concrete examples
- Focus on hidden human dynamics
- Value-first (help them, not ask for job)

## Batch Message Review Process

When drafting multiple messages:
1. Draft all messages first
2. Review all together for consistency
3. Check for repetitive language across messages
4. Verify each is 70-90 words
5. Ensure unique insights (no copy-paste between companies)
6. Run word count check on each

## Word Count Tips

- Each sentence ≈ 12-15 words
- News hook: 1 sentence (15 words)
- Insight + evidence: 2 sentences (30 words)
- Credibility + geography: 2 sentences (25 words)
- Ask: 1 sentence (15 words)
- **Total**: 5-6 sentences = 75-85 words

## Common Mistakes to Avoid

**Too Generic**: "Change management is important in the region"
**Too Obvious**: "Local partnerships matter"
**Too Theoretical**: "Cultural alignment drives success"
**Too Negative**: "Everything is harder in [region]"
**Too Prescriptive**: "You need to do X, Y, Z"

**Just Right**: "Mass training creates mass resistance — [Big SaaS] discovered this after losing 73% adoption at day 90"

## For Complete Examples and Insight Development

See `../../operating-procedures/`:
- `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md` (8 complete examples with analysis)
- `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md` (15-minute insight development process)
- `OUTREACH-OPERATING-PROCEDURE-v4.md` (Step 6: Message Creation)
