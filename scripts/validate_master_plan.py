from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.csv_store import read_next_pending
from krishna_story_factory.master_plan import load_master_plan, validate_master_plan


def main() -> int:
    path = PROJECT_ROOT / "input" / "krishna_book_master_plan.csv"
    errors = validate_master_plan(path)
    rows = load_master_plan(path)
    next_plan = read_next_pending(PROJECT_ROOT)
    if not next_plan:
        errors.append("No next pending episode found in runtime queue.")
    if errors:
        print("MASTER PLAN INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    chapters = {int(row["source_chapter"]) for row in rows}
    print(
        f"MASTER PLAN VALID: {len(rows)} episodes; "
        f"chapters {min(chapters)}-{max(chapters)} covered; "
        f"next active {next_plan.chapter_no}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
