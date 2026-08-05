from __future__ import annotations

import argparse
import json
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files
from krishna_story_factory.pipeline import rebuild_story_range, run_daily_story


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily Krishna-conscious bedtime story package.")
    parser.add_argument("--mode", choices=["test", "prod"], default=None)
    parser.add_argument("--force", action="store_true", help="Reprocess a specific chapter when used with --chapter.")
    parser.add_argument("--chapter", help="Process a specific chapter number, e.g. 003")
    parser.add_argument("--rebuild", action="store_true", help="Allow selecting a done row when no pending rows remain.")
    parser.add_argument("--rebuild-components", help="Comma-separated locked-package components to rebuild (activity,coloring).")
    parser.add_argument(
        "--rebuild-range",
        help="Rebuild completed stories in a chapter range, e.g. 001:005 (does not generate 006).",
    )
    parser.add_argument(
        "--preserve-queue",
        action="store_true",
        help="With --rebuild-range, restore queue so rebuilt stories stay done and 006 stays pending.",
    )
    parser.add_argument(
        "--replace-drive",
        action="store_true",
        help="With --rebuild-range, upload/replace Drive package files for each rebuilt story.",
    )
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--clean-reset", action="store_true", help="Reset output, queue 001-010 pending, and tracking logs.")
    parser.add_argument(
        "--resume-from",
        help="Resume from a governed recovery workspace, e.g. work/stories/008/20260724-100002",
    )
    parser.add_argument(
        "--enable-production-recovery",
        action="store_true",
        help="Explicitly allow generating only missing Story artifacts while reusing locked story/narration.",
    )
    parser.add_argument(
        "--scheduler-simulate",
        action="store_true",
        help="Safe scheduled-task simulation: lock, queue probe, stage_state, permissions; no providers/Drive/queue writes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    ensure_csv_files(project_root)
    if args.scheduler_simulate:
        from krishna_story_factory.scheduler_simulate import run_scheduler_simulate

        result = run_scheduler_simulate(project_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status") == "SUCCESS" else 1
    settings = load_settings(project_root)
    if args.rebuild_range:
        result = rebuild_story_range(
            settings,
            range_spec=args.rebuild_range,
            mode=args.mode or "prod",
            preserve_queue=bool(args.preserve_queue),
            replace_drive=bool(args.replace_drive) and not args.no_upload,
            debug=args.debug,
            archive=True,
        )
        _print_json(result)
        return 0 if result.get("status") == "SUCCESS" else 1

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
        resume_from=args.resume_from,
        enable_production_recovery=bool(args.enable_production_recovery),
    )
    _print_json(result)
    return 0 if result.get("status") in {
        "SUCCESS",
        "NO_PENDING_STORY",
        "SKIPPED_ALREADY_COMPLETED_TODAY",
        "ALREADY_DONE",
        "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE",
    } else 1


def _print_json(payload: dict) -> None:
    """Print JSON without crashing Windows cp1252 consoles on diacritics."""
    import sys

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    stream = sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        stream.write(text + "\n")
    except UnicodeEncodeError:
        stream.buffer.write((text + "\n").encode(encoding, errors="replace"))
        stream.buffer.flush()


if __name__ == "__main__":
    raise SystemExit(main())
