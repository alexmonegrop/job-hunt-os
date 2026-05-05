#!/usr/bin/env python3
"""Render a cover letter to a clean professional PDF.

Reads contact info from applications/resumes/data/{user-slug}/user-config.yaml,
or accepts CLI overrides. No hardcoded personal defaults.

Usage:
    python tools/resume-tailor/generate-cover-letter-pdf.py \
        --user jane-demo \
        --input applications/jane-demo/{company}-{job}/cover-letter.md \
        --output applications/jane-demo/{company}-{job}/cover-letter.pdf
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    sys.exit("Missing dependency: fpdf2. Install with `pip install fpdf2`.")

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pyyaml. Install with `pip install pyyaml`.")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def sanitize_text(text: str) -> str:
    """Replace unicode characters that core fonts can't handle."""
    replacements = {
        "—": "--",
        "–": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "•": "-",
        " ": " ",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


class CoverLetterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def _cell_ln(self, w, h, text, align="L", bold=False, size=10):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, size)
        self.cell(w, h, sanitize_text(text), align=align,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def header_block(self, name, email, phone, location, linkedin, date_str):
        self._cell_ln(0, 7, name, bold=True, size=14)

        self.set_font("Helvetica", "", 9)
        contact_parts = [p for p in [email, phone, location] if p]
        if contact_parts:
            self.cell(0, 5, "  |  ".join(contact_parts),
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if linkedin:
            self.cell(0, 5, linkedin, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(3)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

        self._cell_ln(0, 5, date_str, size=10)
        self.ln(6)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10.5)
        paragraphs = text.strip().split("\n\n")
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            para = re.sub(r"\n(?!\n)", " ", para)
            self.multi_cell(0, 5.5, sanitize_text(para))
            if i < len(paragraphs) - 1:
                self.ln(3)


def strip_markdown(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        if re.match(r"^#+\s", line):
            continue
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        line = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", line)
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def load_user_config(user: str | None) -> dict:
    if not user:
        return {}
    cfg_path = REPO_ROOT / "applications" / "resumes" / "data" / user / "user-config.yaml"
    if not cfg_path.exists():
        print(f"WARNING: No user-config.yaml at {cfg_path}", file=sys.stderr)
        return {}
    try:
        with open(cfg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"WARNING: Could not parse {cfg_path}: {e}", file=sys.stderr)
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate cover letter PDF")
    parser.add_argument("--input", help="Path to cover letter .md or .txt file")
    parser.add_argument("--text", help="Cover letter text directly")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--user",
                        default=os.environ.get("JOB_HUNT_USER"),
                        help="User slug. Falls back to JOB_HUNT_USER env var.")
    parser.add_argument("--name")
    parser.add_argument("--email")
    parser.add_argument("--phone")
    parser.add_argument("--location")
    parser.add_argument("--linkedin")
    parser.add_argument("--date", help="Date string (default: today)")
    args = parser.parse_args()

    cfg = load_user_config(args.user)
    name = args.name or cfg.get("full_name") or ""
    email = args.email or cfg.get("email") or ""
    phone = args.phone or cfg.get("phone") or ""
    location = args.location or cfg.get("location") or ""
    linkedin = args.linkedin or cfg.get("linkedin") or ""

    if not name:
        sys.exit(
            "ERROR: No name resolved. Pass --name or set --user with a valid "
            "user-config.yaml."
        )

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            sys.exit(f"ERROR: File not found: {input_path}")
        raw_text = input_path.read_text(encoding="utf-8")
    elif args.text:
        raw_text = args.text
    else:
        sys.exit("ERROR: Provide either --input or --text")

    body = strip_markdown(raw_text)
    date_str = args.date or datetime.now().strftime("%B %d, %Y")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = CoverLetterPDF()
    pdf.add_page()
    pdf.set_margins(25, 20, 25)
    pdf.set_y(20)
    pdf.header_block(name, email, phone, location, linkedin, date_str)
    pdf.body_text(body)
    pdf.output(str(output_path))

    print(f"Cover letter PDF generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
