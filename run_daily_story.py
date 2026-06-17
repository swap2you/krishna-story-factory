from __future__ import annotations

import argparse
import json
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files
from krishna_story_factory.pipeline import run_daily_story


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily Krishna-conscious bedtime story package.")
    parser.add_argument("--mode", choices=["test", "prod"], default="test", help="test uses local mock content and no external API calls.")
    parser.add_argument("--force", action="store_true", help="Allow sending even if a story was already sent today.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    ensure_csv_files(project_root)
    settings = load_settings(project_root)
    result = run_daily_story(settings, mode=args.mode, force=args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {"SUCCESS", "NO_PENDING_STORY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
