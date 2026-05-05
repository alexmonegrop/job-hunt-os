#!/usr/bin/env python3
"""mock-interview.py - get LLM recruiter feedback on an interview answer.

Sends an interview Q&A to an LLM acting as a senior recruiter for the
specific role + sector you're interviewing for. The role / sector context
is loaded from a context file (see tools/interview/contexts/) — pick the
one matching your target role, or write your own.

Candidate context is loaded from your user-config.yaml + a per-user
recruiter-context.yaml at applications/resumes/data/{user-slug}/.

Usage:
    # Default context file (program-manager-energy):
    python tools/interview/mock-interview.py \\
        --question "Tell me about yourself" \\
        --answer "I'm a PMP-certified..."

    # Specific role context:
    python tools/interview/mock-interview.py -q "..." -a "..." \\
        --context tools/interview/contexts/ai-product-manager.txt

    # Compare two models side-by-side:
    python tools/interview/mock-interview.py -q "..." -a "..." --compare

Environment:
    OPENROUTER_API_KEY  - required (https://openrouter.ai/keys)
    INTERVIEW_MODEL     - optional override (default: a fast cheap model)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit('ERROR: requests not installed. Run: pip install requests')

try:
    import yaml
except ImportError:
    sys.exit('ERROR: pyyaml not installed. Run: pip install pyyaml')


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = os.environ.get("INTERVIEW_MODEL", "google/gemini-3-flash-preview")
COMPARE_MODELS = [
    ("Gemini Flash", os.environ.get("INTERVIEW_MODEL_FAST", "google/gemini-3-flash-preview")),
    ("Sonnet 4.6",   os.environ.get("INTERVIEW_MODEL_DEEP", "anthropic/claude-sonnet-4-6")),
]


GENERIC_RECRUITER_PROMPT = """You are a senior executive recruiter and career coach with 15+ years of experience placing PM/Director-level candidates. You give direct, honest, calibrated feedback.

Your evaluation style is:
- Direct and honest - you don't sugarcoat
- Specific - you cite exact phrases from the answer that work or don't
- Constructive - every criticism comes with a concrete fix
- Calibrated - you know what "good" looks like for this level of role

Adjust your evaluation to the candidate context and the role context provided
below. If neither is provided, evaluate against typical senior-PM standards."""


EVAL_PROMPT_TEMPLATE = """Evaluate this interview answer.

ROLE CONTEXT:
{role_context}

CANDIDATE CONTEXT:
{candidate_context}

QUESTION: {question}

CANDIDATE'S ANSWER:
{answer}

Provide your evaluation as JSON with this exact structure:
{{
  "overall_score": <1-10 integer>,
  "verdict": "<STRONG|GOOD|NEEDS WORK|WEAK>",
  "strengths": ["<specific strength 1>", "<specific strength 2>", ...],
  "weaknesses": ["<specific weakness 1>", "<specific weakness 2>", ...],
  "red_flags": ["<any red flags or concerns>"],
  "specific_fixes": ["<concrete rewrite suggestion 1>", ...],
  "missing_elements": ["<what a top candidate would include that this answer doesn't>"],
  "sector_calibration": "<how this answer compares to what you'd hear from the best candidates in this sector>",
  "interviewer_reaction_prediction": "<how the specific interviewer / panel described in role context would likely react>"
}}

Be specific. Quote exact phrases. Don't be generic."""


def load_user_context(user: str | None) -> dict:
    """Load candidate context from per-user files, fall back to empty if none."""
    if not user:
        user = os.environ.get("JOB_HUNT_USER")
    if not user:
        return {}
    base = REPO_ROOT / "applications" / "resumes" / "data" / user
    out: dict = {}
    rc_path = base / "recruiter-context.yaml"
    if rc_path.exists():
        try:
            out["recruiter_context"] = yaml.safe_load(rc_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            pass
    cfg_path = base / "user-config.yaml"
    if cfg_path.exists():
        try:
            out["user_config"] = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            pass
    return out


def format_candidate_context(ctx: dict) -> str:
    """Render the candidate context dict as a flat text block for the prompt."""
    if not ctx:
        return "No candidate context provided."
    lines: list[str] = []
    cfg = ctx.get("user_config", {})
    if cfg.get("full_name"):
        lines.append(f"Candidate: {cfg['full_name']}")
    if cfg.get("location"):
        lines.append(f"Location: {cfg['location']}")
    if cfg.get("tailoring_notes"):
        lines.append(f"Self-positioning notes:\n{cfg['tailoring_notes']}")
    rc = ctx.get("recruiter_context", {})
    if isinstance(rc, dict):
        for k, v in rc.items():
            if isinstance(v, str):
                lines.append(f"{k}: {v}")
            elif isinstance(v, list):
                lines.append(f"{k}: {', '.join(str(x) for x in v)}")
    return "\n".join(lines) if lines else "No candidate context provided."


def load_role_context(context_path: Path | None) -> str:
    """Load the role / sector / interviewer context from a .txt file."""
    if not context_path:
        return "No role context provided. Evaluate against typical senior-PM standards."
    if not context_path.exists():
        sys.exit(f"ERROR: Role context file not found: {context_path}")
    return context_path.read_text(encoding="utf-8").strip()


def call_openrouter(question: str, answer: str, model: str,
                    role_context: str, candidate_context: str) -> dict:
    if not OPENROUTER_API_KEY:
        return {"error": "No OPENROUTER_API_KEY set", "verdict": "SKIP"}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "Mock Interview Feedback",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": GENERIC_RECRUITER_PROMPT},
            {"role": "user", "content": EVAL_PROMPT_TEMPLATE.format(
                role_context=role_context,
                candidate_context=candidate_context,
                question=question,
                answer=answer,
            )},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    start = time.time()
    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
    except requests.exceptions.Timeout:
        return {"error": "Request timed out after 60s", "verdict": "TIMEOUT", "model": model}
    except Exception as e:
        return {"error": str(e), "verdict": "ERROR", "model": model}

    if resp.status_code != 200:
        return {
            "error": f"API returned {resp.status_code}: {resp.text[:300]}",
            "verdict": "ERROR",
            "model": model,
            "elapsed_seconds": round(elapsed, 1),
        }

    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})

    try:
        feedback = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        feedback = json.loads(m.group(1)) if m else {"raw_response": content, "verdict": "PARSE_ERROR"}

    feedback["_meta"] = {
        "model": model,
        "elapsed_seconds": round(elapsed, 1),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }
    return feedback


def format_feedback(feedback: dict, model_label: str = "") -> str:
    if "error" in feedback:
        return f"ERROR ({model_label}): {feedback['error']}"

    lines = []
    header = f"=== {model_label} ===" if model_label else "=== FEEDBACK ==="
    lines.append(header)
    lines.append(f"Score: {feedback.get('overall_score', '?')}/10 - {feedback.get('verdict', '?')}")
    lines.append("")

    sections = [
        ("STRENGTHS", "strengths", "+"),
        ("WEAKNESSES", "weaknesses", "-"),
        ("RED FLAGS", "red_flags", "!"),
        ("SPECIFIC FIXES", "specific_fixes", ">"),
        ("MISSING ELEMENTS", "missing_elements", "?"),
    ]
    for label, key, marker in sections:
        if feedback.get(key):
            lines.append(f"{label}:")
            for item in feedback[key]:
                lines.append(f"  {marker} {item}")
            lines.append("")

    if feedback.get("sector_calibration"):
        lines.append(f"SECTOR CALIBRATION: {feedback['sector_calibration']}")
        lines.append("")
    if feedback.get("interviewer_reaction_prediction"):
        lines.append(f"INTERVIEWER REACTION: {feedback['interviewer_reaction_prediction']}")
        lines.append("")

    meta = feedback.get("_meta", {})
    if meta:
        lines.append(f"--- {meta.get('model', '?')} | {meta.get('elapsed_seconds', '?')}s | "
                     f"{meta.get('total_tokens', '?')} tokens ---")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mock Interview Feedback Engine")
    parser.add_argument("--question", "-q", required=True, help="Interview question")
    parser.add_argument("--answer", "-a", required=True, help="Candidate's answer")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                        help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--context", "-c", default=None,
                        help="Path to role-specific context .txt file (e.g., tools/interview/contexts/program-manager-energy.txt)")
    parser.add_argument("--user", default=os.environ.get("JOB_HUNT_USER"),
                        help="User slug for candidate context (falls back to JOB_HUNT_USER)")
    parser.add_argument("--compare", action="store_true",
                        help="Run two models side-by-side")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    role_context = load_role_context(Path(args.context) if args.context else None)
    user_ctx = load_user_context(args.user)
    candidate_context = format_candidate_context(user_ctx)

    if args.compare:
        results = {}
        for label, model in COMPARE_MODELS:
            print(f"Calling {label} ({model})...", file=sys.stderr)
            results[label] = call_openrouter(args.question, args.answer, model,
                                              role_context, candidate_context)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for label, fb in results.items():
                print(format_feedback(fb, label))
                print()
    else:
        feedback = call_openrouter(args.question, args.answer, args.model,
                                    role_context, candidate_context)
        if args.json:
            print(json.dumps(feedback, indent=2))
        else:
            print(format_feedback(feedback, args.model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
