#!/usr/bin/env python3
"""CLI for the private Knowledge draft factory (M2).

Examples:
  python scripts/knowledge_draft_factory.py --dry-run
  python scripts/knowledge_draft_factory.py --dry-run --no-resume
  python scripts/knowledge_draft_factory.py --status
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from bhava_api.knowledge.draft_factory import (  # noqa: E402
    assert_no_publication_authority,
    get_factory_status,
    run_factory,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bhāva Knowledge private draft factory")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run (default)")
    parser.add_argument("--live-scaffold", action="store_true", help="Write private scaffolds (still no publish)")
    parser.add_argument("--no-resume", action="store_true", help="Ignore prior status and start a new run")
    parser.add_argument("--queue-size", type=int, default=50)
    parser.add_argument("--status", action="store_true", help="Print read-only status JSON and exit")
    parser.add_argument(
        "--attempt-action",
        default="",
        help="Internal guard test: attempt a forbidden action name",
    )
    args = parser.parse_args()

    if args.attempt_action:
        assert_no_publication_authority(args.attempt_action)

    if args.status:
        print(json.dumps(get_factory_status(), indent=2, ensure_ascii=False))
        return 0

    dry_run = not args.live_scaffold
    state = run_factory(
        dry_run=dry_run,
        resume=not args.no_resume,
        queue_size=args.queue_size,
        write_drafts=bool(args.live_scaffold),
    )
    summary = {
        "run_id": state.run_id,
        "dry_run": state.dry_run,
        "queue_size": len(state.queue),
        "items_processed": state.costs.items_processed,
        "duplicates_skipped": state.costs.duplicates_skipped,
        "completed_keys": len(state.completed_keys),
        "publication_authority": False,
        "status_path": str((ROOT / "content/knowledge/factory/state/draft_factory_status.json").as_posix()),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
