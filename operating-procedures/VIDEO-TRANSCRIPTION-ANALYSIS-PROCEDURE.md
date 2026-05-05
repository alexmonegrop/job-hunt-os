# Video Transcription & Meeting Analysis Procedure

**Document type**: Reference. Tool setup + post-meeting analysis workflow.

**Purpose**: transcribe meeting recordings and analyse them against prep documents to extract lessons and follow-ups.

## Phase 1: Video Transcription Setup

### Prerequisites (one-time)

Install OpenAI Whisper:
```bash
pip install openai-whisper
```

Install FFmpeg (required for video processing):
```bash
# Windows (via winget)
winget install ffmpeg

# macOS (via Homebrew)
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt-get install ffmpeg
```

After FFmpeg installation, **restart your terminal** so PATH updates.

### Verify

```bash
python -m whisper --help
ffmpeg -version
```

### Common issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: The system cannot find the file specified` | FFmpeg not in PATH | Restart terminal, or use the custom Python script below |
| `FP16 is not supported on CPU` | Normal warning for CPU processing | Ignore — expected |
| Unicode encoding errors | Special characters in output | Use the custom script that handles encoding |

## Phase 2: Transcription Process

### Option A: Direct command line
```bash
python -m whisper "path/to/video.mp4" \
  --model base --language en \
  --output_format txt --output_dir "output/directory"
```

### Option B: Custom Python script (recommended)

Save as `tools/transcribe_meeting.py` (template ships with the repo). Handles PATH issues and encoding errors. Run with:
```bash
python tools/transcribe_meeting.py "path/to/video.mp4"
```

### Whisper model selection

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | 39 MB | 5 min/hr video | Lowest |
| `base` | 74 MB | 10-20 min/hr | Balanced (recommended) |
| `small` | 244 MB | 20-30 min/hr | Better |
| `medium` | 769 MB | 30-45 min/hr | Even better |
| `large` | 1550 MB | 45-90 min/hr | Best |

Expected processing times: 30-min video with `base` model: ~10-15 min. 1-hour video: ~20-30 min. CPU-intensive — close other applications.

## Phase 3: Pre-Meeting Preparation Review

### Locate prep document
`outreach/{user-slug}/prep/[contact-name]-prep.md`

### Extract key elements to track
1. **Unique insights / hooks** (usually 3): did they come up in conversation? How did contact respond?
2. **Hidden challenges identified**: validated? New challenges discovered?
3. **Prepared questions**: which got asked? Answers received?
4. **Competitive intelligence**: new information? Confirmed assumptions?

## Phase 4: Meeting Analysis Framework

Save as: `outreach/{user-slug}/analysis/[contact-name]-meeting-analysis.md`.

### Required sections

#### 1. Executive summary
- Overall assessment (Success / Neutral / Concern)
- Key outcome in one line
- Next steps secured (Y/N)

#### 2. Prep vs reality comparison
```markdown
### Insights That Landed
1. **[Insight Name]** — VALIDATED / INVALIDATED / NOT DISCUSSED
   - **Prep**: [What you prepared]
   - **Reality**: [What actually happened]
   - **Impact**: [How it affected conversation]
```

#### 3. Key information gathered
- Pain points revealed
- Budget indicators
- Timeline mentions
- Decision-making process
- Stakeholders identified

#### 4. Your performance metrics
- Rapport building (1-10)
- Value communication (1-10)
- Question effectiveness (1-10)
- Listening vs talking ratio
- Technical credibility established

#### 5. Their engagement signals
- Questions they asked
- Follow-up commitments
- Introduction offers
- Information sharing level

#### 6. Competitive intelligence
- Other vendors mentioned
- Internal build vs buy signals
- Previous solution failures
- Success criteria discussed

#### 7. Action items
```markdown
### Immediate (24 hours)
- [ ] Thank-you message
- [ ] LinkedIn connection if not connected
- [ ] Calendar invite if meeting scheduled

### Short-term (3-5 days)
- [ ] Follow-up with promised information
- [ ] Introduction requests executed
- [ ] Research homework completed

### Long-term (1-2 weeks)
- [ ] Check-in if no response
- [ ] Parallel-path development
- [ ] Network expansion in their organisation
```

## Phase 5: Follow-Up Message Creation

### Template
```markdown
Hi [Name],

[Reference specific moment from meeting — shows attention]

[Callback to their main pain point with your relevant experience]

[One specific value-add or insight not discussed in meeting]

[Clear next step aligned with what they committed to]

Best,
[user]
```

### Key elements
- 50-75 words maximum
- One specific quote or moment referenced
- One new piece of value (don't just rehash the meeting)
- Clear call-to-action based on their commitment

## Phase 6: Database Update

### Sales Pipeline updates
1. **Stage**: move from "Drafted/Sent" to "Meeting completed"
2. **Last interaction**: update date and type
3. **Notes**: key points in bullets
4. **Next step**: specific action with date
5. **Temperature**: update based on meeting (Cold / Warm / Hot)
6. **Pain points**: add discovered challenges
7. **Decision timeline**: add if mentioned

### Interactions entry
```
Date: [Meeting date]
Type: Video Call (or Voice / In Person)
Duration: [X minutes]
Topics Discussed: [bullets]
Follow-up Required: [Y/N]
Follow-up Date: [Date]
Outcome: [Next steps]
```

## Phase 7: Success Metrics Tracking

### Meeting quality indicators

**High success**: next meeting scheduled / introduction to team offered / specific role / project discussed / budget / timeline revealed.

**Moderate success**: general interest / follow-up welcomed / information exchange / connection maintained.

**Low success**: no clear next steps / defensive responses / rushed / misaligned expectations.

## File Structure Standard

```
outreach/{user-slug}/
├── prep/
│   └── [contact-name]-[company]-prep.md
├── calls/
│   ├── [contact-name]-[company]-[date].mp4
│   ├── [contact-name]-transcript.txt
│   └── [contact-name]-transcript-with-timestamps.txt
├── analysis/
│   └── [contact-name]-meeting-analysis.md
└── messages/
    └── [company]-[contact-name]-followup.md
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Transcription runs but fails at the end | Encoding issue — check if transcript files were created despite the error |
| Video file too large (>1 GB) | Extract audio first: `ffmpeg -i meeting.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 meeting.wav` |
| Transcript quality poor | Try `small` or `medium` model; ensure good audio quality; consider manual review for critical sections |
| Can't install tools on work computer | Use Google Colab as fallback (requires Google account only) |

## Time Estimates

| Phase | Duration |
|-------|----------|
| Setup (first time) | 15-20 min |
| Transcription (30-min video) | 10-15 min |
| Analysis document | 20-30 min |
| Follow-up message | 5-10 min |
| Database update | 5 min |
| **Total per meeting** | **45-75 min** |

## Quick Checklist

### Pre-meeting
- [ ] Prep document created
- [ ] Recording tool tested
- [ ] Backup recording method ready

### During meeting
- [ ] Recording started
- [ ] Key points noted
- [ ] Next steps confirmed

### Post-meeting
- [ ] Video file saved to `calls/`
- [ ] Transcription script run
- [ ] Analysis document created (prep vs reality compared)
- [ ] Follow-up message sent
- [ ] Database updated
- [ ] Calendar marked for follow-up
