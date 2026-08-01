from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "tracking" / "queue_state.csv"
V15_BASELINE = ROOT / "docs" / "releases" / "BHAVA_V1_5_SAFETY_BASELINE.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


@pytest.mark.local_runtime
def test_queue_001_020_done_and_021_pending() -> None:
    rows = list(csv.DictReader(QUEUE.open(encoding="utf-8")))
    by_chapter = {str(row["chapter_no"]).zfill(3): row["status"] for row in rows}
    for n in range(1, 21):
        chapter = f"{n:03d}"
        assert by_chapter.get(chapter) == "done", chapter
    assert by_chapter.get("021") == "pending"


def test_v15_baseline_records_008_complete() -> None:
    if not V15_BASELINE.is_file():
        pytest.skip("V1.5 safety baseline missing.")
    import json

    data = json.loads(V15_BASELINE.read_text(encoding="utf-8"))
    story = data.get("story_008") or {}
    assert story.get("status") in {"complete_published", "partial_quarantined"}
    if story.get("status") == "complete_published":
        assert story.get("queue_status") == "done"
        assert story.get("next_pending") == "009"
