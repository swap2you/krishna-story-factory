from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.visuals import StoryVisualGenerator
from krishna_story_factory.visuals.models import make_visual_paths


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate story visuals from story.md")
    parser.add_argument("--story", required=True, help="Path to story.md")
    parser.add_argument("--output", required=True, help="Output directory for visual artifacts")
    parser.add_argument("--line-art-only", action="store_true")
    parser.add_argument("--poster-only", action="store_true")
    parser.add_argument("--generate-all", action="store_true")
    parser.add_argument("--use-references", action="store_true", default=None)
    parser.add_argument("--no-references", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mode", default="prod", choices=("prod", "test"))
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    settings = load_settings(PROJECT_ROOT)
    story_path = Path(args.story)
    output_dir = Path(args.output)
    if not story_path.exists():
        print(f"Story file not found: {story_path}", file=sys.stderr)
        return 1

    line_art_only = args.line_art_only
    poster_only = args.poster_only
    if args.generate_all:
        line_art_only = False
        poster_only = False
    if line_art_only and poster_only:
        print("Choose only one of --line-art-only or --poster-only.", file=sys.stderr)
        return 1

    use_refs: bool | None = None
    if args.no_references:
        use_refs = False
    elif args.use_references:
        use_refs = True

    generator = StoryVisualGenerator(settings, mode=args.mode)
    result = generator.generate_all(
        story_path,
        output_dir,
        line_art_only=line_art_only,
        poster_only=poster_only,
        use_references=use_refs,
        force=args.force,
        dry_run=args.dry_run,
    )

    paths = make_visual_paths(output_dir)
    summary = {
        "line_art_status": result.line_art_status,
        "poster_status": result.poster_status,
        "reference_images_used": result.reference_images_used,
        "quality_score": result.quality_score,
        "model": result.model,
        "dry_run": result.dry_run,
        "issues": result.issues,
        "artifacts": [
            field.name
            for field in dataclasses.fields(paths)
            if field.name != "root"
            and isinstance(getattr(paths, field.name), Path)
            and getattr(paths, field.name).exists()
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
