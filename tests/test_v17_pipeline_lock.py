"""V1.7 ownership-safe scheduler lock tests."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from krishna_story_factory.pipeline_lock import (
    acquire_pipeline_lock,
    lock_is_stale,
    read_lock_meta,
    release_pipeline_lock,
    touch_lock_heartbeat,
    write_lock_atomic,
)


def test_live_lock_blocks_second_acquire(tmp_path: Path):
    first = acquire_pipeline_lock(tmp_path, run_id="a", mode="prod", child_pid=os.getpid())
    with pytest.raises(RuntimeError, match="in progress"):
        acquire_pipeline_lock(tmp_path, run_id="b", mode="prod")
    release_pipeline_lock(first, force=True)


def test_stale_dead_pid_reclaimed(tmp_path: Path):
    lock = tmp_path / ".pipeline.lock"
    write_lock_atomic(
        lock,
        {
            "run_id": "old",
            "pid": 99999999,
            "child_pid": 99999999,
            "wrapper_pid": 99999998,
            "created_at": "2020-01-01T00:00:00+00:00",
            "heartbeat_at": "2020-01-01T00:00:00+00:00",
            "mode": "prod",
        },
    )
    held = acquire_pipeline_lock(tmp_path, stale_after_sec=1, run_id="new", mode="prod")
    assert json.loads(held.read_text(encoding="utf-8"))["run_id"] == "new"
    release_pipeline_lock(held, force=True)


def test_corrupt_lock_reclaimed(tmp_path: Path):
    lock = tmp_path / ".pipeline.lock"
    lock.write_text("{not-json", encoding="utf-8")
    assert lock_is_stale(read_lock_meta(lock))
    held = acquire_pipeline_lock(tmp_path, run_id="ok", mode="prod")
    release_pipeline_lock(held, force=True)


def test_owner_only_release(tmp_path: Path):
    held = acquire_pipeline_lock(tmp_path, run_id="mine", mode="prod", child_pid=os.getpid())
    assert release_pipeline_lock(held, run_id="other", owner_pid=1, force=False) is False
    assert held.exists()
    assert release_pipeline_lock(held, run_id="mine", owner_pid=os.getpid(), force=False) is True
    assert not held.exists()


def test_validation_lock_isolated(tmp_path: Path):
    prod = acquire_pipeline_lock(tmp_path, run_id="prod", mode="prod")
    val = acquire_pipeline_lock(tmp_path, validation=True, run_id="val", mode="validate")
    assert prod.name == ".pipeline.lock"
    assert val.name == ".pipeline.validate.lock"
    release_pipeline_lock(prod, force=True)
    release_pipeline_lock(val, force=True)


def test_heartbeat_updates(tmp_path: Path):
    held = acquire_pipeline_lock(tmp_path, run_id="hb", mode="prod")
    before = read_lock_meta(held)["heartbeat_at"]
    touch_lock_heartbeat(held, story_no="009")
    after = read_lock_meta(held)
    assert after["story_no"] == "009"
    assert after["heartbeat_at"] >= before
    release_pipeline_lock(held, force=True)


def test_scheduled_runner_uses_dotnet_process_isolation():
    text = Path("scripts/run_daily_story_scheduled.ps1").read_text(encoding="utf-8")
    assert "System.Diagnostics.Process" in text
    assert "CreateNoWindow = $true" in text
    assert "UseShellExecute = $false" in text
    code_lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    joined = "\n".join(code_lines)
    assert "NoNewWindow" not in joined
    assert "Start-Process" not in joined
    assert "-SimulateProduction" in text
    assert "v1.7.0-dotnet-process" in text
