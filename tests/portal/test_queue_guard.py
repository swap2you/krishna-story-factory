from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LOCK_FILE = ROOT / "data" / "catalog" / "locked_story_hashes.json"
QUEUE = ROOT / "tracking" / "queue_state.csv"
LOCKED_QUEUE = ROOT / "data" / "catalog" / "locked_queue_state.csv"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def test_queue_still_has_008_pending_and_001_007_done() -> None:
    if not QUEUE.is_file():
        pytest.skip("Runtime queue_state.csv not present in this environment.")
    import csv

    rows = list(csv.DictReader(QUEUE.open(encoding="utf-8")))
    by_chapter = {str(row["chapter_no"]).zfill(3): row["status"] for row in rows}
    for chapter in ("001", "002", "003", "004", "005", "006", "007"):
        assert by_chapter.get(chapter) == "done"
    assert by_chapter.get("008") == "pending"


def test_queue_fingerprint_unchanged_when_lock_present() -> None:
    if not LOCK_FILE.exists() or not QUEUE.is_file():
        pytest.skip("Lock file or queue missing.")
    import json

    lock = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    expected = lock.get("queue_sha256")
    if not expected:
        pytest.skip("No queue fingerprint recorded.")
    assert _sha256(QUEUE) == expected.upper()
    if LOCKED_QUEUE.is_file():
        assert QUEUE.read_bytes() == LOCKED_QUEUE.read_bytes()
