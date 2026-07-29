"""Generate Bhāva V1.2 safety baseline JSON."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    stories: dict[str, dict] = {}
    for n in range(1, 8):
        prefix = f"{n:03d}_"
        folders = [p for p in (ROOT / "output").iterdir() if p.is_dir() and p.name.startswith(prefix)]
        if not folders:
            raise SystemExit(f"missing package for {prefix}")
        folder = sorted(folders)[0]
        files = {name: sha(folder / name) for name in REQUIRED}
        stories[f"{n:03d}"] = {"package_folder": folder.name, "files": files}

    queue_path = ROOT / "tracking" / "queue_state.csv"
    queue_rows = list(csv.DictReader(queue_path.open(encoding="utf-8", newline=""))) if queue_path.is_file() else []
    queue_008 = "pending"
    for row in queue_rows:
        chapter = "".join(ch for ch in str(row.get("chapter_no") or row.get("story_no") or "") if ch.isdigit())
        if chapter.zfill(3) == "008":
            queue_008 = str(row.get("status") or "pending")
            break
    qf = sha(queue_path) if queue_path.is_file() else hashlib.sha256(b"").hexdigest()

    baseline = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "branch": "feature/bhava-portal-v1",
        "head_sha": "b0ba09aa51f6500f7a99257d148ff3bc1e4a12d0",
        "tested_release_candidate_sha": "70722981ee19550c8c6ce19137d33c4bdccae9f8",
        "main_sha": "3bae97850ef8b934bbec3a48f42f92fbe6de169f",
        "tags": [
            "v1.0.0-pilot-stories-001-006",
            "v1.1.0-stories-001-007-operational",
        ],
        "queue_fingerprint_sha256": qf,
        "queue_008_status": queue_008,
        "factory_actions_enabled_default": False,
        "scheduler_triggered": False,
        "drive_modified": False,
        "paid_apis_called": False,
        "stories": stories,
    }
    out = ROOT / "docs" / "releases" / "BHAVA_V1_2_SAFETY_BASELINE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} queue_008={queue_008} stories={len(stories)}")


if __name__ == "__main__":
    main()
