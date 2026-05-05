# Quick Insight Development Guide

**Time required**: 15 minutes per company.

**Document type**: Reference. For automatic enforcement, see `.claude/rules/02-message-quality-standards.md` (Insight Quality section).

**Purpose**: rapidly develop counter-intuitive insights for outreach messages.

## The 15-Minute Insight Research Process

### Minute 1-3: Identify their public goal

Quick search: `"[Company] [announcement/news] <current and prior year>"`.

Extract:
- What they're trying to achieve
- Timeline they've committed to
- Metrics they've mentioned

Example (illustrative, fictional):
- Goal: deploy AI across [region] government
- Timeline: 3-year agreement
- Metric: 50+ applications across 6 ministries

### Minute 4-7: Find the hidden pattern

Quick searches (run in parallel):
```
"[Competitor] [same goal] failed OR struggled OR challenges"
"[Industry] [region] common mistakes OR failures OR lessons"
"[Similar company] [region] what went wrong OR problems"
```

Look for: repeated failures, unexpected bottlenecks, time / cost overruns, adoption issues.

Example findings:
- "[Competitor A] struggled with ministry silos in [region]"
- "[Competitor B]'s [country] deal stalled on stakeholder alignment"
- "94% of government IT projects fail globally"

### Minute 8-10: Identify the counter-intuitive truth

Formula: "Most think X, but actually Y"

Common counter-intuitive patterns (illustrative):

| Obvious assumption | Counter-intuitive reality |
|-------------------|--------------------------|
| Technology is the challenge | Stakeholder alignment is the challenge |
| Innovation wins | Proven-elsewhere wins |
| Money solves problems | Relationships solve problems |
| Fast execution matters | Right sequence matters |
| Central approval is key | Distributed buy-in is key |
| Features drive adoption | Change management drives adoption |
| Global talent is best | Local champions are best |
| First-mover advantage | Second-mover advantage |

Example insight:
"Most think ministry integration is technical, but it's actually political — conflicting KPIs make data sharing threatening, not difficult."

### Minute 11-13: Find your authority angle

Quick audit of your experience (from `applications/resumes/data/{user-slug}/master-experience.yaml`):
- Which of your experiences relates to this pattern?
- What similar complexity have you navigated?
- What parallel challenge have you solved?

Connection types:
- **Direct**: same industry / challenge
- **Parallel**: similar complexity / dynamics
- **Pattern**: same failure mode / solution type
- **Scale**: similar size / scope / timeline

### Minute 14-15: Package the insight

Structure: Evidence + Pattern + Your Authority

Templates:

**The Competitor Failure**:
"[Competitor] spent [time / money] discovering that [counter-intuitive truth]. [Your experience] taught me [solution approach]."

**The Industry Pattern**:
"[X]% of [industry] companies fail at [specific point] because [non-obvious reason]. At [your company], we avoided this by [approach]."

**The Regional Reality**:
"In [region], [common approach] fails because [local dynamic]. [Your experience] showed that [alternative approach] works."

**The Timeline Truth**:
"The critical window is [timeframe], not [what they think]. [Evidence]. [Your experience] proved [what actually matters]."

## Insight Quality Scorecard

Rate your insight (must score 4+ to use):

| Criterion | Score (1-5) |
|-----------|------------|
| Surprising — would they say "I didn't know that"? | __ |
| Specific — is it about their exact situation? | __ |
| Evidenced — do you have proof / examples? | __ |
| Valuable — would this save them time / money / pain? | __ |
| Credible — do you have authority to know this? | __ |

Total: __/25 (need 20+ for strong insight).

## Quick Insight Formulas by Industry

These are seeds — adapt to your `target_industries[]` and `target_regions[]` from config.

### AI / Tech
"In <region>, government validation precedes private adoption, reversing typical B2B sequence."

### Consultancies
"Regional projects fail at stakeholder multiplication, not strategy formulation."

### FinTech
"Local trust architectures matter more than global technology platforms."

### E-commerce
"Last-mile relationships with traditional distributors determine digital success."

### HealthTech
"Regulatory approval follows precedent, creating circular dependency loops."

### EdTech
"Accreditation requirements are unpublished and country-specific."

### Enterprise software
"Mass training creates mass resistance; cascade adoption works."

### Cybersecurity
"Sovereignty requirements outweigh security features in decisions."

## Common Insight Mistakes

- **Too generic**: "Change management is important in the region"
- **Too obvious**: "Local partnerships matter"
- **Too theoretical**: "Cultural alignment drives success"
- **Too negative**: "Everything is harder in [region]"
- **Too prescriptive**: "You need to do X, Y, Z"

**Just right**: "Mass training creates mass resistance — [Big SaaS Co] discovered this after losing 73% adoption at day 90."

## The Speed Research Stack

Tools for 15-minute research:
1. **Google** — "[Company] [Competitor] failed [region]"
2. **LinkedIn** — check company updates / articles
3. **Google News** — filter by past month
4. **Your memory** — what patterns have you seen?
5. **Industry reports** — quick scan for failure rates

Search shortcuts:
- Add "despite" to find failures: "despite investment"
- Add "learned" to find lessons: "[Big SaaS] learned [region]"
- Add "mistake" to find problems: "common mistake [country]"
- Add "actually" to find truths: "what actually works [country]"

## Building Your Insight Bank

Maintain a spreadsheet (or YAML file under `research/{user-slug}/insight-bank.yaml`) with:
1. **Company**: target company name
2. **Challenge**: what they're trying to do
3. **Pattern**: what typically goes wrong
4. **Insight**: the counter-intuitive truth
5. **Evidence**: proof points / examples
6. **Connection**: your relevant experience
7. **Message**: actual insight text
8. **Response**: did it work? (track results)

Reusable insights by category:
- Government stakeholder complexity
- Regional talent acquisition
- Regulatory navigation
- Cultural change management
- Competitor dynamics
- Timeline realities
- Partnership structures
- Adoption patterns

## The 5-Minute Emergency Insight

When you need something fast:

1. **Their newest news** (30 sec)
2. **Industry + region + "challenges"** (2 min)
3. **Find one competitor failure** (1 min)
4. **Connect to any of your experience** (1 min)
5. **Write: "Like [competitor], you'll discover [truth]"** (30 sec)

Example: "Like [Big SaaS Co], you'll discover that [region] regulatory approval follows success, not precedes it."

## Testing Your Insights

A/B test different angles:
- Week 1: competitor failure angle
- Week 2: timeline reality angle
- Week 3: stakeholder complexity angle
- Week 4: regional pattern angle

Track:
- Which insights get responses
- Which get "tell me more"
- Which lead to meetings
- Which get forwarded

Iterate based on data.

---

*The best insights feel simultaneously surprising and obvious — they make people think "Of course! Why didn't I see that?"*

**Time investment**: 15 min.
**Expected response-rate improvement**: 2-3x.
