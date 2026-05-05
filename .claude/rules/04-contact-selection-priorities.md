# Contact Selection Priorities

## Target: 9-10 High-Quality Contacts Per Company

**Quality over quantity**: Better 3 excellent contacts than 10 mediocre ones.

## Priority by Company Size

### Large Companies (5,000+ employees)

**Target composition**: 70-90% Directors / Senior Managers / Managers

**Why**: Operational layers have more direct hiring influence than distant C-suite.

**Focus departments** (defaults — override per role via `config/user-profile.yaml`):
- Digital Transformation
- AI / Automation
- Engineering / Product
- Regional Operations

**Avoid**: C-suite (unless perfect match with the active user's founder/executive background — see `credibility_anchors[]` in `config/user-profile.yaml`).

**Example pattern**: A 60K-employee enterprise — focus on Directors of Digital, Senior Managers of AI, Managers of Automation; not the CEO.

### Medium Companies (500-5,000 employees)

**Target composition**: 60-80% operational roles

**Include**:
- VPs with budget authority
- Directors of key departments
- Senior Managers with hiring influence

**Focus**: Department heads who directly build teams.

### Small Companies (<500 employees)

**Target composition**: Co-founders + early operational hires

**Include**:
- C-level when appropriate
- Founding team members
- Early employees (#5-#20)

**Why**: In startups, everyone shapes culture and hiring.

## Acceptable Operational Roles

### Always good
- Engineering / Product / Delivery Managers
- Solutions Architects / Technical Directors
- Customer Success / Account Managers (enterprise focus)
- Project / Program Managers
- Regional Operations Directors
- Zone / Country Managers (operational focus)
- Technical Leads / Principal Engineers

### Case-by-case
- Sales roles (only if regionally focused or enterprise sales leadership)
- Marketing roles (only if growth/expansion focus)
- HR roles (only if talent acquisition leadership for technical roles)

### Generally avoid
- Pure sales roles without operational connection
- Marketing roles without regional responsibility
- Finance roles (unless CFO at small companies with hiring authority)
- Administrative roles

## Geographic Prioritization

Reads `target_regions[]` from `config/user-profile.yaml`. Preference order (highest to lowest):

1. **Target-region-based roles** — based in the cities listed in `target_regions[]`.
2. **Regional roles** — broader region covering the target (e.g., "EMEA Director" if targeting a sub-region).
3. **International with regional mandate** — based elsewhere but manages the target region.
4. **HQ with expansion oversight** — at headquarters, responsible for international expansion that includes the target region.

## Contact Priority Designation

### Primary Contacts (3-4 per company)

**Criteria**:
- Direct decision-making authority
- Based in the target region OR explicitly responsible for it
- Strong alignment with the active user's `credibility_anchors[]`
- Active on LinkedIn (posts in last 30 days)

**"Why Right Person" emphasis**: Strategic alignment, decision authority, the user's executive/founder credibility.

### Secondary Contacts (4-5 per company)

**Criteria**:
- Strong operational relevance
- Can influence hiring decisions
- Good alignment with the user's experience
- Regional or department oversight

**"Why Right Person" emphasis**: Technical/operational alignment, peer-level relevance, team insights.

### Backup Contacts (2-3 per company)

**Criteria**:
- Indirect relevance
- May provide introductions
- Adjacent departments
- Future opportunities as company grows

**"Why Right Person" emphasis**: Network value, future potential, adjacent expertise.

## Research Tool Priority

### Use BOTH WebSearch and LinkedIn MCP together

**For researching Target Contacts, ALWAYS use WebSearch AND a LinkedIn MCP together**:

#### 1. WebSearch (start here)
```
"[Company] director operations LinkedIn"
"[Company] engineering manager LinkedIn [target city]"
"[Company] senior manager [technology] LinkedIn [target city]"
"[Company] program manager [region] LinkedIn"
site:linkedin.com/in/ "[Company]" "manager" OR "director"
```

#### 2. LinkedIn MCP (alongside WebSearch)

Use for every company when researching contacts:
- Search for people at specific companies
- Get detailed profile information
- Verify LinkedIn URLs found via WebSearch
- Find contacts WebSearch missed

**Tool prefix**: `mcp__linkedin__*` (configure your LinkedIn MCP per `docs/SETUP.md`).

**If LinkedIn MCP is not available or returns errors**:
1. Check Docker is running (required by most LinkedIn MCPs)
2. Verify LinkedIn cookie hasn't expired
3. Restart Claude Code if MCP shows "Connected" but tools fail
4. **Ask the user** before proceeding with WebSearch-only fallback

## Companies with <10 Existing Contacts

Flexible quality-based approach:

- **8-9 contacts**: Select the best 3-5 by quality
- **5-7 contacts**: Select the best 3 if all high-quality
- **<5 contacts**: Select all if Primary/Secondary priority
- **Backup plan**: Research additional via WebSearch / LinkedIn MCP

Not every company will have 10 contacts — that's acceptable if quality is high.

## Role Alignment with the Active User's Background

The active user's `credibility_anchors[]` (from `config/user-profile.yaml`) drives this. The list maps focus areas → anchor tags. When prioritising contacts at a company, prefer contacts whose role is in the company's focus areas that are also anchored in the user's profile.

Example structure (illustrative):
- If user has `robotics_deployment` anchor → prioritise Engineering Managers, Solutions Architects, Deployment Leads at robotics companies.
- If user has `ai_ml_founder` anchor → prioritise Product Managers, Technical Directors, Implementation Leads at AI/ML companies.
- If user has `digital_transformation` anchor → prioritise Program Managers, Transformation Directors, Technology Leads at consultancies.
- If user has `industrial_construction` anchor → prioritise Project Managers, Operations Directors, Site Technology Leads at infrastructure firms.
- If user has `energy_renewable` anchor → prioritise Operations Managers, Technical Directors, Regional Leads at energy firms.

## Quality Indicators

**Strong contact signals**:
- Recent LinkedIn activity (last 30 days)
- Posts about company growth/hiring
- Mentions of the target region
- Operational role title (not purely strategic)
- Direct reports (team builder)
- Based in target geography
- Relevant certifications (peer alignment with user's `credentials[]`)

**Weak contact signals**:
- No LinkedIn activity (6+ months)
- Pure sales focus
- No geographic relevance
- Too junior (individual contributor, no team)
- Too senior (CEO at 10K+ employee company, unless user has C-level credibility)

## For Complete Contact Population Workflow

See `../../operating-procedures/`:
- `contact-population-plan-v3.md` (7-step workflow, quality criteria, lessons learned)
- `OUTREACH-OPERATING-PROCEDURE-v4.md` (Step 2: Contact Selection)
