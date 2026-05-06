#!/usr/bin/env python3
"""quality-gate.py — validate a tailored resume .docx before submission.

Outputs a JSON scorecard with PASS / WARN / FAIL verdict.

Usage:
    python tools/resume-tailor/quality-gate.py \\
        --resume applications/{user}/{company}-{job}/resume.docx \\
        --job-file applications/jobs/{company}-{job}.yaml \\
        [--user jane-demo]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

try:
    from docx import Document
except ImportError:
    sys.exit("ERROR: python-docx not installed. Run: pip install python-docx")


# Thresholds — keep in sync with format-config.yaml `thresholds` if you tune them.
MIN_BULLETS = 22
HARD_FAIL_MIN_BULLETS = 17
MIN_HARD_TOOLS = 4
PREFERRED_HARD_TOOLS = 6
MIN_SUMMARY_KEYWORDS = 3
MIN_KEYWORD_DENSITY = 0.30
PREFERRED_KEYWORD_DENSITY = 0.40
MAX_BULLET_OVERLAP = 0.70
MIN_COMPANY_COVERAGE = 3
PREFERRED_COMPANY_COVERAGE = 4

HARD_TOOLS = {
    "jira", "confluence", "asana", "monday.com", "trello", "notion",
    "power bi", "powerbi", "tableau", "looker", "google analytics",
    "sql", "python", "r", "javascript", "typescript",
    "aws", "azure", "gcp", "docker", "kubernetes",
    "sap", "oracle", "salesforce", "hubspot", "dynamics",
    "figma", "miro", "visio", "lucidchart",
    "git", "github", "gitlab", "bitbucket",
    "n8n", "zapier", "make", "power automate",
    "airtable", "nocodb", "supabase", "firebase",
    "openai", "claude", "langchain", "hugging face",
    "tensorflow", "pytorch", "scikit-learn",
    "react", "angular", "vue", "next.js", "node.js",
    "postgresql", "mysql", "mongodb", "redis",
    "snowflake", "databricks", "bigquery", "redshift",
    "excel", "power query", "dax", "vba",
    "autocad", "revit", "bim", "primavera", "ms project",
    "claude code", "mcps",
    "denodo", "informatica", "talend", "dbt",
    "servicenow", "zendesk", "intercom",
    "smartsheet", "wrike", "basecamp",
    "pmp", "cspo", "csm", "safe", "prince2", "itil",
    "agile", "scrum", "kanban", "lean", "six sigma",
    "ci/cd", "jenkins", "terraform", "ansible",
}

SOFT_CAPABILITIES = {
    "strategic partnership", "cross-functional leadership", "stakeholder management",
    "strategy & execution", "strategic planning", "change management",
    "team leadership", "executive communication", "business development",
    "thought leadership", "digital transformation", "innovation management",
    "go-to-market", "market expansion", "revenue growth",
    "organizational design", "talent management", "culture building",
}

CREDENTIAL_TERMS = {
    "pmp", "cspo", "csm", "safe", "prince2", "itil", "six sigma",
    "scrum master", "certified", "certification",
}


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_resume_content(docx_path: Path) -> dict:
    doc = Document(str(docx_path))
    all_text, bullets, companies = [], [], []
    title_text = summary_text = skills_text = ""
    in_experience = found_title = found_summary = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        all_text.append(text)

        if not found_title and not in_experience:
            runs = para.runs
            if runs and runs[0].bold and runs[0].font.size and runs[0].font.size >= 100000:
                if text.upper() != text and "WORK EXPERIENCE" not in text and "EDUCATION" not in text:
                    if any(kw in text for kw in ("|", "Manager", "Director", "Lead", "Founder", "Consultant")):
                        title_text = text
                        found_title = True
                        continue

        if found_title and not found_summary and not in_experience:
            if not text.startswith("Technical Skills") and text.upper() != text:
                summary_text = text
                found_summary = True
                continue

        if text.startswith("Technical Skills"):
            skills_text = text
            continue

        if text == "WORK EXPERIENCE":
            in_experience = True
            continue
        if text in ("EDUCATION", "CERTIFICATIONS"):
            in_experience = False
            continue

        if in_experience and para.runs and para.runs[0].bold:
            m = re.match(r"^([A-Z][A-Z\s&/\-\.]+)", text)
            if m:
                cn = m.group(1).strip()
                if cn and cn != "CAREER BREAK" and len(cn) > 2:
                    companies.append(cn)

        if para.style and "Bullet" in (para.style.name or ""):
            bullets.append(text)
        elif in_experience and not (para.runs and para.runs[0].bold) and len(text) > 30:
            if not (para.runs and para.runs[0].italic and len(text) < 100):
                bullets.append(text)

    return {
        "all_text": "\n".join(all_text),
        "bullets": bullets,
        "companies": list(set(companies)),
        "title": title_text,
        "summary": summary_text,
        "skills_line": skills_text,
    }


def check_bullet_count(content: dict, job: dict | None = None) -> dict:
    count = len(content["bullets"])
    job = job or {}
    min_bullets = int(job.get("min_bullets", MIN_BULLETS))
    hard_fail = int(job.get("hard_fail_min_bullets", min(HARD_FAIL_MIN_BULLETS, max(min_bullets - 5, 1))))
    if count < hard_fail:
        return {"check": "bullet_count", "status": "FAIL", "value": count,
                "threshold": f">= {min_bullets} (hard fail < {hard_fail})",
                "detail": f"Only {count} bullets found. Add more text_overrides or lower min_bullets in job YAML."}
    if count < min_bullets:
        return {"check": "bullet_count", "status": "FAIL", "value": count,
                "threshold": f">= {min_bullets}",
                "detail": f"{count} bullets found, target is {min_bullets}+. Page 2 will be thin."}
    return {"check": "bullet_count", "status": "PASS", "value": count,
            "threshold": f">= {min_bullets}", "detail": f"{count} bullets found."}


def check_skills_line(content: dict) -> dict:
    skills = content["skills_line"]
    if not skills:
        return {"check": "skills_line", "status": "FAIL", "value": 0,
                "threshold": f">= {MIN_HARD_TOOLS} hard tools",
                "detail": "No skills line found in resume."}

    skills_body = re.sub(r"^Technical Skills:\s*", "", skills, flags=re.IGNORECASE)
    items = [item.strip().rstrip(".") for item in re.split(r"[,|;]", skills_body) if item.strip()]

    hard_count = soft_count = 0
    hard_found, soft_found = [], []
    for item in items:
        lo = item.lower().strip()
        if any(tool in lo for tool in HARD_TOOLS):
            hard_count += 1
            hard_found.append(item)
        elif any(cap in lo for cap in SOFT_CAPABILITIES):
            soft_count += 1
            soft_found.append(item)
        else:
            if len(item.split()) <= 3:
                hard_count += 1
                hard_found.append(item)
            else:
                soft_count += 1
                soft_found.append(item)

    if hard_count < MIN_HARD_TOOLS:
        return {"check": "skills_line", "status": "FAIL", "value": hard_count,
                "threshold": f">= {PREFERRED_HARD_TOOLS} hard tools",
                "detail": f"Only {hard_count} hard tools found. Soft: {soft_found}. Hard: {hard_found}"}
    if hard_count < PREFERRED_HARD_TOOLS:
        return {"check": "skills_line", "status": "WARN", "value": hard_count,
                "threshold": f">= {PREFERRED_HARD_TOOLS} hard tools",
                "detail": f"{hard_count} hard tools (target {PREFERRED_HARD_TOOLS}+)."}
    return {"check": "skills_line", "status": "PASS", "value": hard_count,
            "threshold": f">= {PREFERRED_HARD_TOOLS} hard tools",
            "detail": f"{hard_count} hard tools, {soft_count} soft items."}


def check_title_match(content: dict, job: dict) -> dict:
    rt = content["title"].lower()
    jt = job.get("job_title", job.get("title", "")).lower()
    if not rt:
        return {"check": "title_match", "status": "WARN", "value": "",
                "threshold": "Title aligns with job",
                "detail": "Could not extract title from resume."}
    if not jt:
        return {"check": "title_match", "status": "WARN", "value": rt,
                "threshold": "Title aligns with job",
                "detail": "No job_title in YAML to compare against."}

    role_words = {"manager", "director", "lead", "consultant", "analyst", "architect",
                  "engineer", "specialist", "coordinator", "founder", "vp", "head",
                  "product", "program", "project", "digital", "transformation", "ai",
                  "innovation", "operations", "strategy", "data", "technical", "owner"}
    rrw = set(re.findall(r"\b\w+\b", rt)) & role_words
    jrw = set(re.findall(r"\b\w+\b", jt)) & role_words
    overlap = rrw & jrw
    if not overlap and rrw and jrw:
        return {"check": "title_match", "status": "FAIL", "value": content["title"],
                "threshold": f"Should align with: {job.get('job_title', '')}",
                "detail": f"No role-word overlap. Resume: {rrw}, Job: {jrw}"}
    return {"check": "title_match", "status": "PASS", "value": content["title"],
            "threshold": f"Aligns with: {job.get('job_title', '')}",
            "detail": f"Overlapping role words: {overlap}"}


def check_summary_keywords(content: dict, job: dict) -> dict:
    summary = content["summary"].lower()
    if not summary:
        return {"check": "summary_keywords", "status": "WARN", "value": 0,
                "threshold": f">= {MIN_SUMMARY_KEYWORDS} keywords",
                "detail": "Could not extract summary from resume."}

    all_keywords = job.get("requirements", []) + job.get("industry_keywords", [])
    found = []
    for kw in all_keywords:
        kw_words = kw.lower().split()
        if any(re.search(r"\b" + re.escape(w) + r"\b", summary) for w in kw_words if len(w) > 2):
            found.append(kw)
    found = list(set(found))
    if len(found) < MIN_SUMMARY_KEYWORDS:
        return {"check": "summary_keywords", "status": "WARN", "value": len(found),
                "threshold": f">= {MIN_SUMMARY_KEYWORDS} keywords",
                "detail": f"Summary contains {len(found)} keywords: {found}."}
    return {"check": "summary_keywords", "status": "PASS", "value": len(found),
            "threshold": f">= {MIN_SUMMARY_KEYWORDS} keywords",
            "detail": f"Summary contains {len(found)} keywords: {found}"}


def check_keyword_density(content: dict, job: dict) -> dict:
    full_text = content["all_text"].lower()
    all_items = job.get("requirements", []) + job.get("nice_to_haves", []) + job.get("industry_keywords", [])
    if not all_items:
        return {"check": "keyword_density", "status": "WARN", "value": 0,
                "threshold": f">= {PREFERRED_KEYWORD_DENSITY*100:.0f}%",
                "detail": "No requirements/keywords in job YAML."}

    found = []
    missing = []
    for item in all_items:
        item_words = item.lower().split()
        matched = any(re.search(r"\b" + re.escape(w) + r"\b", full_text) for w in item_words if len(w) > 2)
        (found if matched else missing).append(item)

    density = len(found) / len(all_items) if all_items else 0
    if density < MIN_KEYWORD_DENSITY:
        return {"check": "keyword_density", "status": "WARN", "value": f"{density:.0%}",
                "threshold": f">= {PREFERRED_KEYWORD_DENSITY*100:.0f}%",
                "detail": f"{density:.0%} found ({len(found)}/{len(all_items)}). Missing: {missing[:5]}"}
    if density < PREFERRED_KEYWORD_DENSITY:
        return {"check": "keyword_density", "status": "WARN", "value": f"{density:.0%}",
                "threshold": f">= {PREFERRED_KEYWORD_DENSITY*100:.0f}%",
                "detail": f"{density:.0%} found ({len(found)}/{len(all_items)}). Missing: {missing[:5]}"}
    return {"check": "keyword_density", "status": "PASS", "value": f"{density:.0%}",
            "threshold": f">= {PREFERRED_KEYWORD_DENSITY*100:.0f}%",
            "detail": f"{density:.0%} keywords found ({len(found)}/{len(all_items)})."}


def check_duplicate_bullets(content: dict) -> dict:
    bullets = content["bullets"]
    duplicates = []
    for i in range(len(bullets)):
        wi = set(bullets[i].lower().split())
        if len(wi) < 3:
            continue
        for j in range(i + 1, len(bullets)):
            wj = set(bullets[j].lower().split())
            if len(wj) < 3:
                continue
            ov = len(wi & wj) / min(len(wi), len(wj))
            if ov > MAX_BULLET_OVERLAP:
                duplicates.append((i, j, f"{ov:.0%}"))
    if duplicates:
        details = [f"Bullets {d[0]+1} & {d[1]+1} ({d[2]} overlap)" for d in duplicates[:3]]
        return {"check": "duplicate_bullets", "status": "FAIL", "value": len(duplicates),
                "threshold": f"No pairs > {MAX_BULLET_OVERLAP*100:.0f}% overlap",
                "detail": f"{len(duplicates)} duplicate pair(s): {'; '.join(details)}"}
    return {"check": "duplicate_bullets", "status": "PASS", "value": 0,
            "threshold": f"No pairs > {MAX_BULLET_OVERLAP*100:.0f}% overlap",
            "detail": "No near-duplicate bullets found."}


def check_company_coverage(content: dict) -> dict:
    cs = content["companies"]
    n = len(cs)
    if n < MIN_COMPANY_COVERAGE:
        return {"check": "company_coverage", "status": "WARN", "value": n,
                "threshold": f">= {PREFERRED_COMPANY_COVERAGE} employers",
                "detail": f"Only {n} companies detected: {cs}."}
    if n < PREFERRED_COMPANY_COVERAGE:
        return {"check": "company_coverage", "status": "WARN", "value": n,
                "threshold": f">= {PREFERRED_COMPANY_COVERAGE} employers",
                "detail": f"{n} companies detected: {cs}"}
    return {"check": "company_coverage", "status": "PASS", "value": n,
            "threshold": f">= {PREFERRED_COMPANY_COVERAGE} employers",
            "detail": f"{n} companies detected: {cs}"}


def check_cross_section_repetition(content: dict) -> dict:
    summary = content["summary"].lower()
    skills = content["skills_line"].lower()
    title = content["title"].lower()
    issues = []

    skills_body = re.sub(r"^technical skills:\s*", "", skills, flags=re.IGNORECASE)
    skill_items = [i.strip().rstrip(".").lower() for i in re.split(r"[,|;]", skills_body) if i.strip()]

    for cred in CREDENTIAL_TERMS:
        if re.search(r"\b" + re.escape(cred) + r"\b", summary):
            issues.append(f"Summary contains credential '{cred}' - belongs in skills line + certs section only")
        if re.search(r"\b" + re.escape(cred) + r"\b", title):
            issues.append(f"Title contains credential '{cred}' - belongs in skills line + certs section only")

    for item in skill_items:
        if len(item) < 3 or item in {"agile", "scrum", "lean"}:
            continue
        if item in summary:
            issues.append(f"Summary repeats '{item}' from skills line - summary should describe impact, skills line lists tools")

    if issues:
        return {"check": "cross_section_repetition", "status": "FAIL", "value": len(issues),
                "threshold": "No unnecessary repetition across sections",
                "detail": f"{len(issues)} repetition(s): " + "; ".join(issues[:5])}
    return {"check": "cross_section_repetition", "status": "PASS", "value": 0,
            "threshold": "No unnecessary repetition across sections",
            "detail": "No cross-section repetition found."}


def run_recruiter_review(resume_path: Path, job_path: Path, user: str) -> dict:
    """Optional independent LLM recruiter review.

    Returns WARN if recruiter-review.py is not installed (it's deferred to a
    later release — see docs/PLAN.md).
    """
    script = Path(__file__).parent / "recruiter-review.py"
    if not script.exists():
        return {"check": "recruiter_review", "status": "WARN", "value": "SKIPPED",
                "threshold": "Independent LLM review",
                "detail": "recruiter-review.py not yet shipped (see docs/PLAN.md Phase 4 deferred items)"}
    try:
        result = subprocess.run(
            [sys.executable, str(script),
             "--resume", str(resume_path),
             "--job-file", str(job_path),
             "--user", user],
            capture_output=True, text=True, timeout=60,
        )
        review = json.loads(result.stdout) if result.stdout.strip() else {"verdict": "SKIP"}
        verdict = review.get("verdict", "SKIP")
        if verdict == "SKIP":
            return {"check": "recruiter_review", "status": "WARN", "value": "SKIPPED",
                    "threshold": "Independent LLM review",
                    "detail": f"Skipped: {review.get('error', 'unknown')}"}
        issues = review.get("issues", [])
        blocking = [i for i in issues if i.get("severity") == "blocking"]
        advisory = [i for i in issues if i.get("severity") == "advisory"]
        status = "FAIL" if verdict == "FAIL" else "PASS"
        detail = f"{len(blocking)} blocking, {len(advisory)} advisory."
        if blocking:
            detail += " Blocking: " + "; ".join(i.get("detail", "?") for i in blocking[:3])
        return {"check": "recruiter_review", "status": status,
                "value": {"blocking": len(blocking), "advisory": len(advisory)},
                "threshold": "No blocking issues from recruiter review",
                "detail": detail}
    except subprocess.TimeoutExpired:
        return {"check": "recruiter_review", "status": "WARN", "value": "TIMEOUT",
                "threshold": "Independent LLM review",
                "detail": "Recruiter review timed out (60s)"}
    except Exception as e:
        return {"check": "recruiter_review", "status": "WARN", "value": "ERROR",
                "threshold": "Independent LLM review",
                "detail": f"Review failed: {str(e)[:100]}"}


def run_quality_gate(resume_path: Path, job_path: Path, user: str) -> dict:
    job = load_yaml(job_path)
    content = extract_resume_content(resume_path)
    checks = [
        check_bullet_count(content, job),
        check_skills_line(content),
        check_title_match(content, job),
        check_summary_keywords(content, job),
        check_keyword_density(content, job),
        check_duplicate_bullets(content),
        check_company_coverage(content),
        check_cross_section_repetition(content),
        run_recruiter_review(resume_path, job_path, user=user),
    ]
    fails = [c for c in checks if c["status"] == "FAIL"]
    warns = [c for c in checks if c["status"] == "WARN"]
    passes = [c for c in checks if c["status"] == "PASS"]
    verdict = "FAIL" if fails else ("WARN" if warns else "PASS")
    return {
        "resume": str(resume_path),
        "job_file": str(job_path),
        "user": user,
        "verdict": verdict,
        "summary": f"{len(passes)} PASS, {len(warns)} WARN, {len(fails)} FAIL",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume quality gate")
    parser.add_argument("--resume", required=True, help="Path to tailored resume.docx")
    parser.add_argument("--job-file", required=True, help="Path to job posting YAML")
    parser.add_argument("--user", default=os.environ.get("JOB_HUNT_USER", "default"),
                        help="User slug. Falls back to JOB_HUNT_USER env var.")
    args = parser.parse_args()

    resume_path = Path(args.resume)
    job_path = Path(args.job_file)
    if not resume_path.exists():
        print(json.dumps({"verdict": "FAIL", "error": f"Resume not found: {resume_path}"}))
        return 1
    if not job_path.exists():
        print(json.dumps({"verdict": "FAIL", "error": f"Job file not found: {job_path}"}))
        return 1

    result = run_quality_gate(resume_path, job_path, user=args.user)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
