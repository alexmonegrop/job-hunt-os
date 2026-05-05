---
name: "company-deep-dive"
description: "Comprehensive company-level strategic analysis for interview preparation. Creates in-depth prep packages covering business fundamentals, current strategy, future direction, competitive landscape (global + regional), industry context, and strategic-fit alignment. Use when preparing for interviews where you need deep company understanding beyond contact-level prep."
---

# Company Deep-Dive

Strategic company analysis for interview preparation. Provides depth beyond contact-focused prep.

## What This Skill Does

- **Business fundamentals** — revenue, valuation, funding, business model, customer segments
- **Current strategy** — recent moves, partnerships, leadership statements, strategic priorities
- **Future direction** — announced plans, hiring patterns, investment areas, strategic questions
- **Competitive landscape** — global + regional competitors with positioning analysis
- **Industry context** — market size, growth trends, technology shifts, regulatory environment
- **Strategic fit** — your value alignment, talking points, strategic questions, concern responses
- **Interview intelligence** — key themes, numbers, recent news, competitor insights

## When To Use

Use for:
- Scheduled interviews (not just initial outreach)
- Companies you need to deeply understand
- Demonstrating market knowledge in conversation
- Preparing strategic questions that show insight

Don't use for:
- Initial cold outreach (use `contact-population` or `cold-outreach`)
- Companies you're just researching (not interviewing with)
- Quick 15-min screening calls (`meeting-prep` is sufficient)

## Prerequisites

Required:
- Company name and context (what role/opportunity)
- WebSearch access

Helpful:
- Existing Target Companies record (for `why_strong_fit` context)
- Existing contact prep files (to complement, not duplicate)

MCP tools:
- `WebSearch`
- `mcp__nocodb__*` (optional)

## Quick Start

```
"Create company deep-dive for Acme Renewables — interview tomorrow"
"Company deep-dive for Globex Power — VP Operations interview"
```

---

## Complete Workflow

### Step 1: Business fundamentals (~10 min)

```javascript
WebSearch("[Company] business model revenue funding valuation <current and prior year>")
WebSearch("[Company] products services customers")
```

Extract:
- What they do (simple explanation)
- Business model
- Key metrics (revenue, valuation, funding, employees)
- Customer segments and verticals
- Geographic footprint

### Step 2: Current strategy (~10 min)

```javascript
WebSearch("[Company] strategy expansion partnerships <current and prior year>")
WebSearch("[Company] CEO [Name] vision strategy")
WebSearch("[Company] recent news announcements")
```

Extract:
- Strategic priorities
- Recent major moves (last 12-18 months)
- Key partnerships
- Leadership statements / quotes
- Funding / M&A activity

### Step 3: Future direction (~5 min)

```javascript
WebSearch("[Company] expansion plans hiring growth <current year>")
WebSearch("[Company] job openings careers")
```

Extract:
- Announced plans and timelines
- Hiring patterns (what roles signal what priorities)
- Investment areas
- Strategic questions they're navigating

### Step 4: Global competitors (~10 min)

```javascript
WebSearch("[Company] competitors market landscape")
WebSearch("[Industry] market leaders competitors [Company]")
```

Extract:
- Direct competitors (same solution)
- Adjacent competitors (different approach, same problem)
- Competitive moat / differentiation
- Market positioning

### Step 5: Regional landscape (~10 min)

Pulls `target_regions[]` from `config/user-profile.yaml`.

```javascript
WebSearch("[Industry] [target region] providers companies")
WebSearch("[Company] [target region] expansion")
WebSearch("[Major regional client/buyer] [industry] partnerships providers")
```

Extract:
- Regional competitors
- International competitors with regional presence
- Local partnership landscape
- Customer relationships (major regional buyers — pull from `config/regions.yaml` `flagship_buyers[]` if defined)

### Step 6: Industry context (~5 min)

```javascript
WebSearch("[Industry] market size growth trends <current year> <future year>")
WebSearch("[Industry] technology trends AI automation")
```

Extract:
- Market size and growth projections
- Key industry shifts
- Technology disruptions
- Regulatory environment (especially regional)

### Step 7: Synthesise strategic fit (~10 min)

For each strategic priority, map:
1. What they need
2. Your relevant experience (pull from `applications/resumes/data/{user-slug}/master-experience.yaml`)
3. Evidence/example
4. Talking point for interview

Develop:
- 4-5 strategic questions that show insight
- Proactive responses to potential concerns
- Key themes to weave into conversation
- Numbers/facts to reference naturally

### Step 8: Generate deep-dive document (~10 min)

Output: `outreach/{user-slug}/prep/company-deep-dive-[company].md`

---

## Output File Structure

```markdown
# Company Deep-Dive: [Company Name]
## Strategic Interview Prep Package

**Prepared**: [Date]
**Interview**: [Date/Context]
**Purpose**: Deep company understanding for strategic conversation

---

## 1. BUSINESS FUNDAMENTALS

### What They Do (Simple Version)
[1-2 sentences]

### Business Model
| Component | Description | Revenue Type |

### Key Metrics
| Metric | Value | Context |

### Customer Segments
| Segment | Key Customers | % of Business |

### Geographic Footprint
| Region | Status | Key Activity |

---

## 2. CURRENT STRATEGY (last 24 months)

### Strategic Priorities
1. ...

### Recent Major Moves
| Date | Event | Significance |

### Leadership Statements
**On [Topic]** ([Source, Date]):
> "[Quote]"

**Key Insight**: ...

---

## 3. FUTURE DIRECTION

### Announced Plans
| Initiative | Timeline | Details |

### Hiring Patterns (Indicate Priorities)
- ...

### Strategic Questions for the Company
1. ...

---

## 4. COMPETITIVE LANDSCAPE

### Global Competitors
| Competitor | Type | Strengths | Weaknesses vs [Company] |

### [Company]'s Competitive Moat
...

### Regional Competitors
| Competitor | Focus | Relationship | Threat Level |

### [Key Regional Buyer] Landscape
| Player | Status | Notes |

---

## 5. INDUSTRY CONTEXT

### Market Size & Growth
| Market | <year> Size | <future year> Projection | CAGR |

### Technology Shifts
| Shift | Impact | [Company] Position |

### Regional Dynamics
1. ...

---

## 6. STRATEGIC FIT (User → Company)

### Where You Add Value
| Their Need | Your Experience | Evidence |

### Talking Points Aligned to Their Priorities
**For [Topic] Discussion:**
> "[Prepared talking point]"

### Questions That Show Strategic Understanding
1. ...

### Potential Concerns to Address Proactively
| Concern | Your Response |

---

## 7. INTERVIEW INTELLIGENCE

### Key Themes to Weave Into Conversation
1. ...

### Numbers/Facts to Reference Naturally
- "[Metric]"

### Recent News to Mention
- [Date]: [News item]

### Competitor Insights
- "[Observation]"

---

## Quick Reference Card

### The Company in 30 Seconds
[Paragraph]

### Your Pitch in 30 Seconds
[Your value prop for this specific company]

### 3 Things They Need
1. ...

### 3 Things You Offer
1. ...
```

---

## Quality Checklist

Before finalising:
- [ ] Business model clearly explained
- [ ] Key metrics accurate and sourced
- [ ] Strategy reflects CURRENT priorities (not old news)
- [ ] Global competitors identified with positioning
- [ ] Regional competitors researched specifically
- [ ] Industry context includes market size and trends
- [ ] Strategic fit maps your experience to their needs
- [ ] 4-5 strategic questions prepared
- [ ] Recent news included (last 30 days)
- [ ] Quick-reference card completed

---

## Relationship to Other Skills

| Skill | Focus | When to Use |
|-------|-------|-------------|
| **company-deep-dive** | Company strategy | Before interviews requiring depth |
| **meeting-prep** | Contact + conversation | Before any meeting |
| **contact-population** | Finding contacts | Building pipeline |
| **cold-outreach** | Initial messages | Reaching out first time |

Best practice: use `company-deep-dive` FIRST for strategic understanding, then `meeting-prep` for conversation-specific preparation.
