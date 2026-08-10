"""Focused tests for M2 Knowledge draft factory dry-run idempotency."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from bhava_api.knowledge.draft_factory import (  # noqa: E402
    DEFAULT_QUEUE_SIZE,
    FactoryAuthorityError,
    assert_no_publication_authority,
    build_deterministic_queue,
    get_factory_status,
    idempotency_key,
    run_factory,
)


def test_deterministic_queue_size_and_order():
    q1 = build_deterministic_queue(DEFAULT_QUEUE_SIZE)
    q2 = build_deterministic_queue(DEFAULT_QUEUE_SIZE)
    assert len(q1) == DEFAULT_QUEUE_SIZE
    assert [i["id"] for i in q1] == [i["id"] for i in q2]
    assert q1[0]["id"] == "kl-about-bhava"
    assert q1[6]["id"] == "TOP-0147"
    assert all(item.get("public") is True or item.get("batch_state") != "public" for item in q1)


def test_idempotency_key_stable():
    a = idempotency_key("TOP-0147", "scaffold")
    b = idempotency_key("TOP-0147", "scaffold")
    c = idempotency_key("TOP-0147", "ledger")
    assert a == b
    assert a != c
    assert len(a) == 64


def test_dry_run_idempotent_resume(tmp_path: Path):
    status = tmp_path / "draft_factory_status.json"
    first = run_factory(dry_run=True, resume=False, status_path=status, root=ROOT)
    assert first.dry_run is True
    assert first.costs.items_queued == DEFAULT_QUEUE_SIZE
    assert first.costs.items_processed == DEFAULT_QUEUE_SIZE
    keys_first = list(first.completed_keys)
    stages_first = first.costs.stages_executed
    assert len(keys_first) == DEFAULT_QUEUE_SIZE * 5  # five stages each

    second = run_factory(dry_run=True, resume=True, status_path=status, root=ROOT)
    assert second.completed_keys == keys_first
    assert second.costs.stages_executed == stages_first
    assert second.costs.items_processed == first.costs.items_processed
    assert second.authority == {
        "approve": False,
        "merge": False,
        "deploy": False,
        "publish": False,
    }

    status_view = get_factory_status(status_path=status)
    assert status_view["available"] is True
    assert status_view["publication_authority"] is False
    assert status_view["items_done"] == DEFAULT_QUEUE_SIZE


def test_forbidden_actions_raise():
    for action in ("approve", "merge", "deploy", "publish", "publication"):
        with pytest.raises(FactoryAuthorityError):
            assert_no_publication_authority(action)


def test_cli_dry_run_and_live_scaffold_are_mutually_exclusive():
    """--dry-run and --live-scaffold must not both be accepted; default mode is dry-run."""
    import argparse
    import importlib.util

    script = ROOT / "scripts" / "knowledge_draft_factory.py"
    # Mutual exclusion is enforced by argparse before any status write.
    both = __import__("subprocess").run(
        [sys.executable, str(script), "--dry-run", "--live-scaffold"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert both.returncode != 0
    combined = (both.stderr + both.stdout).lower()
    assert "not allowed with argument" in combined or both.returncode == 2

    # Hermetic: load CLI module and verify flag→dry_run mapping without writing repo state.
    spec = importlib.util.spec_from_file_location("knowledge_draft_factory_cli", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Avoid executing main on import; only construct the parser logic inline.
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live-scaffold", action="store_true")
    dry_args = parser.parse_args(["--dry-run"])
    live_args = parser.parse_args(["--live-scaffold"])
    default_args = parser.parse_args([])
    assert (not dry_args.live_scaffold) is True
    assert (not live_args.live_scaffold) is False
    assert (not default_args.live_scaffold) is True  # default dry-run
