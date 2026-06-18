#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.quality.repetition import detect_repetition


WORD_RE = re.compile(r"\b[\w']+\b")
PAUSE_RE = re.compile(r"\[\s*pause\s*\]", re.I)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_audio_quality.py <narration.mp3> [audio_script.txt]")
        return 1

    mp3_path = Path(sys.argv[1])
    script_path = Path(sys.argv[2]) if len(sys.argv) > 2 else mp3_path.parent / "audio_script.txt"

    print(f"MP3 path: {mp3_path}")
    if mp3_path.exists():
        print(f"MP3 size bytes: {mp3_path.stat().st_size}")
        duration = _mp3_duration(mp3_path)
        print(f"MP3 duration seconds: {duration if duration is not None else 'unknown'}")
    else:
        print("MP3 size bytes: missing")
        print("MP3 duration seconds: missing")

    if script_path.exists():
        script = script_path.read_text(encoding="utf-8", errors="ignore")
        print(f"Audio script path: {script_path}")
        print(f"Audio script words: {len(WORD_RE.findall(script))}")
        print(f"Contains [pause]: {bool(PAUSE_RE.search(script))}")
        report = detect_repetition(script, content_type="audio")
        print(f"Repetition errors: {len(report.errors)}")
        for err in report.errors[:5]:
            print(f"- {err}")
    else:
        print(f"Audio script path: missing ({script_path})")

    return 0


def _mp3_duration(path: Path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return round(float(MP3(path).info.length), 1)
    except Exception:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
