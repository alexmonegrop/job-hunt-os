#!/usr/bin/env python3
"""recruiter-review.py - independent LLM recruiter review of a tailored resume.

Invoked as a subprocess by quality-gate.py. The contract:
    stdin:  none
    stdout: a single JSON object with shape:
        {
          "verdict": "PASS" | "FAIL" | "SKIP",
          "issues": [
            {"severity": "blocking" | "advisory", "detail": "..."}
          ],
          "error": "<reason>"        // only when verdict == "SKIP"
        }
    exit:   0 on PASS / FAIL / SKIP. Non-zero only on a hard crash.

verdict semantics:
    PASS — no blocking issues. The resume can be sent.
    FAIL — at least one blocking issue. Quality gate must surface it.
    SKIP — review could not be performed (no API key, network failure,
           parse error). Quality gate treats this as WARN, not FAIL —
           the resume isn't blocked just because the LLM was unreachable.

Usage (standalone, for debugging):
    OPENROUTER_API_KEY=sk-or-... \\
    python tools/resume-tailor/recruiter-review.py \\
        --resume applications/{user}/{co}-{job}/resume.docx \\
        --job-file applications/jobs/{co}-{job}.yaml \\
        --user jane-demo

Environment:
    OPENROUTER_API_KEY        required (https://openrouter.ai/keys)
    RECRUITER_REVIEW_MODEL    optional override (default: anthropic/claude-sonnet-4-6)
    RECRUITER_REVIEW_TIMEOUT  optional override (default: 50 — under quality-gate's 60s)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({
        "verdict": "SKIP",
        "issues": [],
        "error": "requests not installed (pip install requests)",
    }))
    sys.exit(0)

try:
    import yaml
except ImportError:
    print(json.dumps({
        "verdict": "SKIP",
        "issues": [],
        "error": "pyyaml not installed (pip install pyyaml)",
    }))
    sys.exit(0)

try:
    from docx import Document
except ImportError:
    print(json.dumps({
        "verdict": "SKIP",
        "issues": [],
        "error": "python-docx not installed (pip install python-docx)",
    }))
    sys.exit(0)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("RECRUITER_REVIEW_MODEL", "anthropic/claude-sonnet-4-6")
DEFAULT_TIMEOUT = int(os.environ.get("RECRUITER_REVIEW_TIMEOUT", "50"))


SYSTEM_PROMPT = """You are a senior executive recruiter with 15+ years placing PM/Director-level candidates at Fortune 500 companies and venture-backed scaleups. You review tailored resumes the way a hiring manager would in the first 30 seconds — direct, specific, no sugar-coating.

You distinguish two issue severities:
- BLOCKING: a problem that would cause a hiring manager to reject the resume on first read (false claims, gross JD mismatch, the role on the resume doesn't match the role being applied for, dishonest framing, missing must-have qualifications that the candidate actually has but failed to surface).
- ADVISORY: a problem that weakens the resume but wouldn't get it rejected outright (weak verb choice, a metric that could be sharper, ordering issues, mild keyword gaps).

Be conservative with BLOCKING — only flag truly serious issues. Most issues are advisory.

Important calibration:
- The candidate's data is fixed (master-experience.yaml). Do not invent claims.
- If a JD requirement is unmet, but the candidate genuinely lacks that experience, that's a JD/candidate fit issue, not a resume tailoring issue. Flag it as advisory unless the resume actively misrepresents the gap.
- Do not flag stylistic preferences (semicolons vs. en-dashes, oxford comma) as issues.
- Tailored bullets that mirror JD language are GOOD, not template-y."""


REVIEW_PROMPT = """Review this tailored resume for the job posting below.

JOB POSTING ({role_category}):
Title: {job_title}
Company: {job_company}

Description:
{job_description}

Key Requirements:
{requirements}

Nice-to-haves:
{nice_to_haves}

Industry keywords:
{industry_keywords}

CANDIDATE CONTEXT:
{candidate_context}

TAILORED RESUME (full text extracted from .docx):

{resume_text}

Return your review as JSON with this exact structure:
{{
  "verdict": "PASS" | "FAIL",
  "summary": "<one-sentence overall judgment>",
  "issues": [
    {{
      "severity": "blocking" | "advisory",
      "category": "title_match" | "summary" | "skills_line" | "bullets" | "jd_coverage" | "honesty" | "other",
      "detail": "<specific issue with quoted phrase from resume>"
    }}
  ],
  "strengths": ["<what works well, 1-3 items>"]
}}

Set verdict to FAIL only if there is at least one BLOCKING issue. Otherwise PASS.
If the resume is solid, return an empty issues array and PASS.
Be specific. Quote exact phrases from the resume."""


# ---------------------------------------------------------------------------
# resume + job loading
# ---------------------------------------------------------------------------

def extract_resume_text(docx_path: Path) -> str:
    """Concatenate all paragraphs from the .docx into a plain-text blob.

    Keeps section structure visible to the LLM by joining with newlines and
    preserving uppercase section headers (WORK EXPERIENCE, EDUCATION, etc.).
    """
    doc = Document(str(docx_path))
    lines: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        is_bullet = para.style and "Bullet" in (para.style.name or "")
        lines.append(f"  • {text}" if is_bullet else text)
    return "\n".join(lines)


def load_job(job_path: Path) -> dict:
    with open(job_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_candidate_context(user: str | None) -> str:
    """Render a brief candidate-context block from per-user config files.

    Mirrors the pattern in tools/interview/mock-interview.py so a single user
    file works for both tools.
    """
    if not user:
        user = os.environ.get("JOB_HUNT_USER")
    if not user:
        return "No candidate context provided."

    base = REPO_ROOT / "applications" / "resumes" / "data" / user
    parts: list[str] = []

    cfg_path = base / "user-config.yaml"
    if cfg_path.exists():
        try:
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if cfg.get("full_name"):
                parts.append(f"Candidate: {cfg['full_name']}")
            if cfg.get("location"):
                parts.append(f"Location: {cfg['location']}")
            if cfg.get("target_roles"):
                roles = cfg["target_roles"]
                parts.append("Target roles: " + (", ".join(roles) if isinstance(roles, list) else str(roles)))
            if cfg.get("tailoring_notes"):
                parts.append(f"Self-positioning notes:\n{cfg['tailoring_notes']}")
        except yaml.YAMLError:
            pass

    rc_path = base / "recruiter-context.yaml"
    if rc_path.exists():
        try:
            rc = yaml.safe_load(rc_path.read_text(encoding="utf-8")) or {}
            if isinstance(rc, dict):
                for k, v in rc.items():
                    if isinstance(v, str) and v.strip():
                        parts.append(f"{k}: {v.strip()}")
                    elif isinstance(v, list) and v:
                        parts.append(f"{k}: " + ", ".join(str(x) for x in v))
        except yaml.YAMLError:
            pass

    return "\n".join(parts) if parts else "No candidate context provided."


def format_list(items, fallback: str = "(none specified)") -> str:
    if not items:
        return fallback
    if isinstance(items, str):
        return items
    return "\n".join(f"- {item}" for item in items)


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def call_openrouter(prompt: str, model: str, api_key: str, timeout: int) -> dict:
    """Single-shot call. Returns either the parsed feedback dict or
    {"_skip": True, "error": "..."} on transport failure."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "Resume Recruiter Review",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.Timeout:
        return {"_skip": True, "error": f"OpenRouter request timed out after {timeout}s"}
    except Exception as e:
        return {"_skip": True, "error": f"OpenRouter request failed: {str(e)[:200]}"}

    if resp.status_code != 200:
        return {"_skip": True,
                "error": f"OpenRouter returned {resp.status_code}: {resp.text[:200]}"}

    content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        return {"_skip": True, "error": "OpenRouter returned empty content"}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        return {"_skip": True,
                "error": f"Could not parse LLM JSON. First 200 chars: {content[:200]}"}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def review(resume_path: Path, job_path: Path, user: str | None,
           model: str, timeout: int) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return {"verdict": "SKIP", "issues": [],
                "error": "OPENROUTER_API_KEY not set"}

    job = load_job(job_path)
    resume_text = extract_resume_text(resume_path)
    if not resume_text:
        return {"verdict": "SKIP", "issues": [],
                "error": f"Could not extract any text from {resume_path}"}

    prompt = REVIEW_PROMPT.format(
        role_category=job.get("role_category", "general"),
        job_title=job.get("job_title", job.get("title", "(unspecified)")),
        job_company=job.get("company_name", job.get("company", "(unspecified)")),
        job_description=(job.get("job_description") or job.get("description") or "(none)")[:4000],
        requirements=format_list(job.get("requirements")),
        nice_to_haves=format_list(job.get("nice_to_haves")),
        industry_keywords=format_list(job.get("industry_keywords")),
        candidate_context=load_candidate_context(user),
        resume_text=resume_text[:12000],
    )

    feedback = call_openrouter(prompt, model=model, api_key=api_key, timeout=timeout)
    if feedback.get("_skip"):
        return {"verdict": "SKIP", "issues": [],
                "error": feedback.get("error", "unknown")}

    issues = feedback.get("issues") or []
    cleaned: list[dict] = []
    for raw in issues:
        if not isinstance(raw, dict):
            continue
        sev = str(raw.get("severity", "advisory")).lower().strip()
        if sev not in ("blocking", "advisory"):
            sev = "advisory"
        detail = raw.get("detail") or raw.get("description") or ""
        if not detail:
            continue
        cleaned.append({"severity": sev, "detail": str(detail).strip(),
                        "category": str(raw.get("category", "other"))})

    has_blocking = any(i["severity"] == "blocking" for i in cleaned)
    raw_verdict = str(feedback.get("verdict", "")).upper().strip()

    if has_blocking:
        verdict = "FAIL"
    elif raw_verdict == "FAIL":
        # LLM said FAIL but didn't mark any issue blocking — promote the first
        # advisory so the user sees what's wrong.
        verdict = "FAIL"
        if cleaned:
            cleaned[0]["severity"] = "blocking"
        else:
            cleaned.append({"severity": "blocking", "category": "other",
                            "detail": feedback.get("summary",
                                "LLM returned FAIL with no specific issue.")})
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "issues": cleaned,
        "summary": feedback.get("summary", ""),
        "strengths": feedback.get("strengths", []),
        "model": model,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM recruiter review for a tailored resume")
    parser.add_argument("--resume", required=True, help="Path to tailored resume.docx")
    parser.add_argument("--job-file", required=True, help="Path to job posting YAML")
    parser.add_argument("--user", default=os.environ.get("JOB_HUNT_USER"),
                        help="User slug. Falls back to JOB_HUNT_USER env var.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"OpenRouter model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    args = parser.parse_args()

    resume_path = Path(args.resume)
    job_path = Path(args.job_file)

    if not resume_path.exists():
        print(json.dumps({"verdict": "SKIP", "issues": [],
                          "error": f"Resume not found: {resume_path}"}))
        return 0
    if not job_path.exists():
        print(json.dumps({"verdict": "SKIP", "issues": [],
                          "error": f"Job file not found: {job_path}"}))
        return 0

    result = review(resume_path, job_path, user=args.user,
                    model=args.model, timeout=args.timeout)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
