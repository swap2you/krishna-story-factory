"""No-provider simulation path used by the scheduled-task wrapper."""
from __future__ import annotations

import csv
import os
from pathlib import Path

from .pipeline_lock import acquire_pipeline_lock, release_pipeline_lock
from .stage_state import StageState


def run_scheduler_simulate(project_root: Path) -> dict:
    queue_path = project_root / "tracking" / "queue_state.csv"
    output_root = project_root / "output"
    staging = project_root / "staging"
    logs = project_root / "logs" / "scheduler"
    run_id = f"simulate-{os.getpid()}"
    lock = None
    try:
        if not queue_path.is_file():
            return {"status": "FAILED", "error": "missing_queue"}
        rows = list(csv.DictReader(queue_path.open(encoding="utf-8-sig")))
        next_pending = next(
            (
                r
                for r in rows
                if str(r.get("status", "")).lower() == "pending"
                and str(r.get("chapter_no", "")).strip().zfill(3)
            ),
            None,
        )
        story_no = str((next_pending or {}).get("chapter_no", "")).strip().zfill(3) or "none"
        lock = acquire_pipeline_lock(
            project_root,
            validation=True,
            run_id=run_id,
            mode="simulate",
            story_no=story_no,
            child_pid=os.getpid(),
            wrapper_pid=int(os.environ.get("BHAVA_WRAPPER_PID") or 0) or None,
            git_sha=os.environ.get("BHAVA_GIT_SHA") or "unknown",
        )
        # Touch stage_state API without mutating story workspaces.
        _ = StageState
        for path in (output_root, staging, logs, project_root / "work" / "stories"):
            path.mkdir(parents=True, exist_ok=True)
            probe = path / f".simulate_write_probe_{os.getpid()}"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        # Import pipeline modules to prove venv/resolution without running providers.
        from . import config, stage_state  # noqa: F401

        return {
            "status": "SUCCESS",
            "mode": "scheduler-simulate",
            "story_selected": story_no,
            "provider_calls": 0,
            "drive_actions": "none",
            "queue_mutated": False,
            "lock": str(lock),
            "pid": os.getpid(),
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAILED", "error": str(exc), "provider_calls": 0, "drive_actions": "none"}
    finally:
        if lock is not None:
            release_pipeline_lock(lock, run_id=run_id, owner_pid=os.getpid(), force=False)
