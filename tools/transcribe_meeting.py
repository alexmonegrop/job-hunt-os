#!/usr/bin/env python3
"""transcribe_meeting.py - transcribe a meeting recording using Whisper.

Handles missing FFmpeg on PATH by searching common install locations.
Outputs both a flat transcript and a timestamped version next to the input.

Usage:
    python tools/transcribe_meeting.py <input_video_path> [--output-dir <dir>] [--model base]

Example:
    python tools/transcribe_meeting.py outreach/jane-demo/calls/jane-smith-2026-04-15.mp4

Models (size, speed for 30 min audio):
    tiny  ~39MB    ~5  min
    base  ~74MB    ~15 min  (recommended balance)
    small ~244MB   ~25 min
    medium ~769MB  ~40 min
    large ~1.55GB  ~70 min

Prerequisites:
    pip install openai-whisper
    FFmpeg installed: see operating-procedures/VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_ffmpeg() -> str | None:
    """Try common locations for ffmpeg. Returns the directory containing it,
    or None if not found."""
    if shutil.which("ffmpeg"):
        return None  # already on PATH; whisper will find it

    candidates: list[str] = []
    if sys.platform == "win32":
        candidates += [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
            r"C:\ProgramData\chocolatey\bin",
        ]
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            candidates += [
                os.path.join(local_app, "Microsoft", "WinGet", "Packages"),
                os.path.join(local_app, "Programs"),
            ]
    elif sys.platform == "darwin":
        candidates += ["/opt/homebrew/bin", "/usr/local/bin"]
    else:
        candidates += ["/usr/bin", "/usr/local/bin"]

    for base in candidates:
        if not os.path.exists(base):
            continue
        for root, _, files in os.walk(base):
            if "ffmpeg.exe" in files or "ffmpeg" in files:
                return root
    return None


def transcribe(video_path: Path, output_dir: Path, model_name: str) -> int:
    if not video_path.exists():
        print(f"ERROR: Video file not found: {video_path}", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_dir = find_ffmpeg()
    if ffmpeg_dir:
        print(f"Adding ffmpeg dir to PATH: {ffmpeg_dir}", file=sys.stderr)
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    elif not shutil.which("ffmpeg"):
        print("WARNING: ffmpeg not found - whisper will likely fail to read the audio.",
              file=sys.stderr)
        print("         Install ffmpeg: see operating-procedures/VIDEO-TRANSCRIPTION-ANALYSIS-PROCEDURE.md",
              file=sys.stderr)

    try:
        import whisper
    except ImportError:
        print("ERROR: openai-whisper not installed. Run: pip install openai-whisper",
              file=sys.stderr)
        return 1

    size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"Video: {video_path} ({size_mb:.1f} MB)", file=sys.stderr)
    print(f"Loading Whisper model: {model_name}...", file=sys.stderr)

    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"ERROR: Failed to load Whisper model: {e}", file=sys.stderr)
        return 1

    print("Transcribing... (10-30 minutes for a 30-minute video on CPU)", file=sys.stderr)
    try:
        result = model.transcribe(str(video_path))
    except Exception as e:
        print(f"ERROR during transcription: {e}", file=sys.stderr)
        print("Falling back to whisper CLI...", file=sys.stderr)
        cmd = [
            sys.executable, "-m", "whisper",
            str(video_path),
            "--model", model_name,
            "--language", "en",
            "--output_format", "txt",
            "--output_dir", str(output_dir),
        ]
        cli = subprocess.run(cmd, capture_output=True, text=True)
        if cli.returncode == 0:
            print(f"CLI fallback succeeded. Output in {output_dir}", file=sys.stderr)
            return 0
        print(f"CLI fallback also failed:\n{cli.stderr}", file=sys.stderr)
        return 1

    stem = video_path.stem
    flat_path = output_dir / f"{stem}-transcript.txt"
    flat_path.write_text(result["text"], encoding="utf-8")
    print(f"Transcript: {flat_path}", file=sys.stderr)

    timestamped_path = output_dir / f"{stem}-transcript-with-timestamps.txt"
    with open(timestamped_path, "w", encoding="utf-8") as f:
        for segment in result.get("segments", []):
            f.write(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}\n")
    print(f"Timestamped: {timestamped_path}", file=sys.stderr)

    print("\n--- TRANSCRIPT PREVIEW (first 500 chars) ---")
    print(result["text"][:500])
    print("...")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe a meeting recording with Whisper")
    parser.add_argument("input", help="Path to video / audio file")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: same as input)")
    parser.add_argument("--model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    args = parser.parse_args()

    video_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else video_path.parent
    return transcribe(video_path, output_dir, args.model)


if __name__ == "__main__":
    sys.exit(main())
