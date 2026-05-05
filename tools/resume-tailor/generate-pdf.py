#!/usr/bin/env python3
"""Convert a tailored resume .docx to .pdf.

Tries docx2pdf first (works on Windows with MS Word installed; macOS too).
Falls back to LibreOffice headless if available.

Usage:
    python tools/resume-tailor/generate-pdf.py --input <resume.docx> [--output <resume.pdf>]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def convert_with_docx2pdf(input_path: Path, output_path: Path) -> bool:
    try:
        from docx2pdf import convert
        convert(str(input_path), str(output_path))
        return True
    except ImportError:
        print("docx2pdf not installed. Run: pip install docx2pdf")
        return False
    except Exception as e:
        print(f"docx2pdf conversion failed: {e}")
        return False


def convert_with_libreoffice(input_path: Path, output_path: Path) -> bool:
    """Try converting with LibreOffice command line."""
    lo_commands = [
        "libreoffice", "soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for lo_cmd in lo_commands:
        try:
            result = subprocess.run(
                [lo_cmd, "--headless", "--convert-to", "pdf",
                 "--outdir", str(output_path.parent), str(input_path)],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                generated = output_path.parent / (input_path.stem + ".pdf")
                if generated != output_path and generated.exists():
                    generated.rename(output_path)
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    print("LibreOffice not found.")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert .docx to .pdf")
    parser.add_argument("--input", required=True, help="Path to .docx file")
    parser.add_argument("--output", help="Output .pdf path (defaults to same name as input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1

    output_path = Path(args.output) if args.output else input_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Converting: {input_path}")
    print(f"Output: {output_path}")

    if convert_with_docx2pdf(input_path, output_path):
        print(f"PDF generated: {output_path}")
        return 0

    if convert_with_libreoffice(input_path, output_path):
        print(f"PDF generated (via LibreOffice): {output_path}")
        return 0

    print("\nERROR: Could not convert to PDF. Options:")
    print("  1. Install docx2pdf: pip install docx2pdf (needs MS Word on Windows)")
    print("  2. Install LibreOffice: https://www.libreoffice.org/download/")
    print("  3. Open the .docx manually and Save As PDF")
    print(f"\n  .docx file is at: {input_path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
