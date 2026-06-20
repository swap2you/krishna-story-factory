from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.visuals.models import make_visual_paths
from krishna_story_factory.visuals.visual_quality import score_visual_outputs


EXPECTED = [
    "visual_brief_json",
    "line_art_prompt",
    "line_art_raw",
    "line_art_portrait",
    "coloring_page",
    "coloring_page_print_pdf",
    "poster_art_prompt",
    "poster_art_raw",
    "poster_copy_json",
    "story_poster",
    "story_poster_whatsapp",
    "visual_generation_manifest",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate story visual outputs")
    parser.add_argument("--output", required=True, help="Story output directory")
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output)
    paths = make_visual_paths(output_dir)
    missing = []
    for name in EXPECTED:
        path = getattr(paths, name)
        if not path.exists() or path.stat().st_size <= 0:
            missing.append(path.name)

    line_prompt = paths.line_art_prompt.read_text(encoding="utf-8") if paths.line_art_prompt.exists() else ""
    poster_prompt = paths.poster_art_prompt.read_text(encoding="utf-8") if paths.poster_art_prompt.exists() else ""
    score, issues = score_visual_outputs(paths, line_prompt=line_prompt, poster_prompt=poster_prompt)

    report = {
        "output_dir": str(output_dir),
        "missing_files": missing,
        "quality_score": score,
        "issues": issues,
        "ok": not missing and score >= 80,
    }
    print(json.dumps(report, indent=2))
    if args.require_all and missing:
        return 1
    if not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
