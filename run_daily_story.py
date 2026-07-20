from __future__ import annotations

import argparse
import json
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files
from krishna_story_factory.pipeline import run_daily_story


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily Krishna-conscious bedtime story package.")
    parser.add_argument("--mode", choices=["test", "prod"], default=None)
    parser.add_argument("--force", action="store_true", help="Reprocess a specific chapter when used with --chapter.")
    parser.add_argument("--chapter", help="Process a specific chapter number, e.g. 003")
    parser.add_argument("--rebuild", action="store_true", help="Allow selecting a done row when no pending rows remain.")
    parser.add_argument("--rebuild-components", help="Comma-separated locked-package components to rebuild (activity,coloring).")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--clean-reset", action="store_true", help="Reset output, queue 001-010 pending, and tracking logs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    ensure_csv_files(project_root)
    settings = load_settings(project_root)
    rebuild_components = {item.strip() for item in (args.rebuild_components or "").split(",") if item.strip()}
    mode = args.mode or ("prod" if rebuild_components else "test")
    result = run_daily_story(
        settings,
        mode=mode,
        force=args.force,
        chapter=args.chapter,
        rebuild=args.rebuild,
        no_upload=args.no_upload,
        debug=args.debug,
        clean_reset=args.clean_reset,
        rebuild_components=rebuild_components,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {
        "SUCCESS",
        "NO_PENDING_STORY",
        "SKIPPED_ALREADY_COMPLETED_TODAY",
        "ALREADY_DONE",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
