from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import read_plan_by_chapter
from krishna_story_factory.images.generator import generate_coloring
from krishna_story_factory.paths import make_package_paths
from krishna_story_factory.pipeline import _content_from_story_md
from krishna_story_factory.work import cleanup_work, new_work_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and QA one temporary poster-referenced coloring candidate.")
    parser.add_argument("--chapter", required=True, help="Chapter number, for example 001")
    parser.add_argument("--debug", action="store_true", help="Keep temporary candidate and QA files under .work.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings(PROJECT_ROOT)
    plan = read_plan_by_chapter(PROJECT_ROOT, args.chapter)
    if not plan:
        print(json.dumps({"status": "FAILED", "error": f"Chapter {args.chapter} not found."}, indent=2))
        return 1
    paths = make_package_paths(settings.output_root, plan)
    if not paths.story_md.exists() or not paths.story_poster.exists():
        print(json.dumps({"status": "FAILED", "error": "Existing story.md and story_poster.png are required."}, indent=2))
        return 1

    story_md = paths.story_md.read_text(encoding="utf-8")
    content = _content_from_story_md(story_md, plan)
    work = new_work_paths(PROJECT_ROOT, debug=True)
    temporary_output = work.root / "smoke_coloring.png"
    started = time.monotonic()
    try:
        score, poster_used, style_used, identity_score = generate_coloring(
            settings, story_md=story_md, content=content, output_path=temporary_output,
            work_candidates=work.coloring_candidates, work_reviews=work.reviews,
            poster_path=paths.story_poster, mode="prod", max_candidates=1,
        )
        elapsed = round(time.monotonic() - started, 1)
        result = {
            "status": "PASS", "chapter": plan.chapter_no, "story": content.title,
            "elapsed_seconds": elapsed, "poster_reference_used": poster_used,
            "style_reference_used": style_used, "identity_score": identity_score,
            "overall_score": score, "peacock_feather_violation": False,
            "temporary_output": str(temporary_output) if args.debug else "cleaned",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        cleanup_work(work, keep=args.debug)
        return 0
    except Exception as exc:
        elapsed = round(time.monotonic() - started, 1)
        reviews = sorted(work.reviews.glob("coloring_candidate_*.json"))
        review = json.loads(reviews[-1].read_text(encoding="utf-8")) if reviews else {}
        print(json.dumps({
            "status": "FAILED", "chapter": plan.chapter_no, "story": content.title,
            "elapsed_seconds": elapsed, "error": str(exc), "review": review,
            "diagnostics": str(work.root),
        }, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
