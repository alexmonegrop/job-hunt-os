# Operating Procedures — Reference Documentation

**Purpose**: Comprehensive workflow documentation for human + AI-agent reference.

These documents complement the auto-loaded rules in `.claude/rules/`. Rules are concise, declarative, and always active. Procedures are detailed walkthroughs with rationale and examples.

## Rules vs Procedures

| Rules (`.claude/rules/`) | Procedures (this directory) |
|--------------------------|------------------------------|
| Critical standards that MUST be followed | Complete workflows with context and examples |
| Concise, declarative bullets | Comprehensive explanations with rationale |
| Auto-loaded every session | Referenced when needed |
| Enforce consistency and quality | Train, explain, and improve |

## Documents in This Directory

### `OUTREACH-OPERATING-PROCEDURE-v4.md`
Complete cold-outreach workflow from company selection through message sending and follow-up.
- Step 0: deep research dossier protocol
- Steps 1-7: company selection, contact selection, DB records, message creation, follow-up, file creation
- Use when: planning outreach campaigns, training new operators, reviewing examples.

### `MEETING-PREP-PROCEDURE-v4.md`
Systematic preparation for 15-minute meetings (max 1 hour prep).
- Meeting environment contingencies (office / video / transit / meal)
- 6 insights (3 core + 3 extended)
- Vulnerability strategy and intelligence-extraction questions
- Use when: preparing for scheduled meetings, structuring follow-up.

### `RESUME-TAILORING-PROCEDURE-v1.md`
Detailed workflow for creating role-specific resume versions and cover letters.
- Master YAML structure
- Achievement scoring algorithm
- Bullet-rewrite rules and quality gate
- Use when: tailoring a resume, debugging a quality-gate FAIL.

### `DIRECT-APPLICATION-PROCEDURE-v1.md`
End-to-end workflow for discovering, preparing, and submitting applications.
- Multi-source job discovery
- Two-pass fit scoring
- Cross-workstream integration with networking
- Use when: running an application sprint, integrating direct applications with networking.

### `contact-population-plan-v3.md`
Populate 9-10 high-quality contacts per company.
- 7-step workflow per company
- Quality criteria by company size
- 3-element "Why Right Person" formula with examples
- Use when: adding new companies to the pipeline.

### `QUICK-INSIGHT-DEVELOPMENT-GUIDE.md`
Develop unique counter-intuitive insights in 15 minutes per company.
- 15-minute research process (5 phases)
- Counter-intuitive truth formulas
- Insight quality scorecard
- Use when: drafting outreach messages and need an insight angle fast.

### `UNIQUE-INSIGHT-MESSAGE-EXAMPLES.md`
8 worked message examples (70-90 words each) with analysis.
- Demonstrates the 6-part formula in action
- Pattern + evidence + credibility + ask
- Use when: looking for inspiration or sanity-checking message structure.

### `APPLICATION-SPEED-LESSONS-v1.md`
Bottlenecks discovered during high-volume application sessions and the fixes.
- Two-pass fit scoring
- Parallel sub-agent resume prep
- Standardised LinkedIn Easy Apply shadow-DOM template
- Use when: optimising a batch application sprint.

### `VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md`
Transcribe meeting recordings and analyse against prep documents.
- Whisper / FFmpeg setup
- Prep-vs-reality comparison framework
- Follow-up message creation from analysis
- Use when: reviewing a video meeting and producing a structured analysis.

## How AI Agents Should Use These

1. Default behaviour: follow `.claude/rules/` automatically. Don't read procedures unless asked.
2. When the user references a procedure by name ("follow OUTREACH-OPERATING-PROCEDURE-v4"), read it.
3. When you need an example or rationale that the rules don't fully explain, read the corresponding procedure.
4. When a workflow has substantive context the rules can't capture (e.g., research patterns, A/B-test learnings), procedures are the source.

## Maintenance

Each procedure tracks version + last-updated date at the top. Update procedures when:
- A workflow improves materially (efficiency, response rate, error reduction)
- A new lesson is learned in a real session worth preserving
- A new tool / integration changes the steps
- A best practice changes

Update the corresponding rule(s) in `.claude/rules/` when:
- A procedure rule becomes critical enough to be auto-enforced
- A frequently-missed requirement needs hardening into a rule
- A data-integrity invariant must be enforced
