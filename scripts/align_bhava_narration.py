#!/usr/bin/env python3
"""Generate sync.json for a Bhāva story package.

Writes a sync.json with ``status: needs_alignment`` for real stories.
This CLI does **not** fabricate timings — it only creates the scaffold so
the web UI can honestly display "Follow-along cues pending review".

Usage
-----
    python scripts/align_bhava_narration.py 007
    python scripts/align_bhava_narration.py 007 --web-assets-dir data/web-assets

Once a real aligner (Whisper forced-alignment, manual spreadsheet, etc.)
is available, this script should be extended to call it and populate the
cues list with reviewed timings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))


def _split_sentences(text: str) -> list[str]:
    """Naive sentence splitter for reader text."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate sync.json for Bhāva narration alignment",
    )
    parser.add_argument("story_no", help="Story number (e.g. 007)")
    parser.add_argument(
        "--package-dir",
        type=Path,
        default=ROOT / "output",
        help="Root directory containing story packages",
    )
    parser.add_argument(
        "--web-assets-dir",
        type=Path,
        default=ROOT / "data" / "web-assets",
        help="Output directory for web-asset files",
    )
    args = parser.parse_args()

    padded = args.story_no.zfill(3)

    reader_path = args.web_assets_dir / padded / "reader.txt"
    narration_path = args.web_assets_dir / padded / "narration.txt"

    reader_sentences: list[str] = []
    narration_txt = ""
    duration_sec = 0.0

    if reader_path.exists():
        reader_sentences = _split_sentences(reader_path.read_text(encoding="utf-8"))
    if narration_path.exists():
        narration_txt = narration_path.read_text(encoding="utf-8")

    try:
        from bhava_api.web_assets.alignment import align_sentences
        sync = align_sentences(reader_sentences, narration_txt, duration_sec)
    except ImportError:
        sync = {
            "status": "needs_alignment",
            "method": "none",
            "confidence": 0,
            "duration_sec": 0,
            "cues": [],
        }

    dest = args.web_assets_dir / padded
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "sync.json"
    out.write_text(json.dumps(sync, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out} (status={sync['status']}, sentences={len(reader_sentences)})")


if __name__ == "__main__":
    main()
