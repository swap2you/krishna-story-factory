"""Ownership-safe pipeline lock helpers for scheduled and CLI runs."""
from __future__ import annotations

import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STALE_AFTER_SEC = 7200.0
DEFAULT_HEARTBEAT_STALE_SEC = 180.0
VALIDATION_LOCK_NAME = ".pipeline.validate.lock"


def lock_path_for(project_root: Path, *, validation: bool = False) -> Path:
    name = VALIDATION_LOCK_NAME if validation else ".pipeline.lock"
    return project_root / name


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, int(pid))
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except SystemError:
        return False
    return True


def read_lock_meta(lock: Path) -> dict[str, Any]:
    if not lock.exists():
        return {}
    raw = lock.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {"started_at": raw}
        except json.JSONDecodeError:
            return {"corrupt": True, "raw": raw[:200]}
    return {"started_at": raw, "legacy": True}


def _heartbeat_age_sec(meta: dict[str, Any]) -> float | None:
    stamp = str(meta.get("heartbeat_at") or meta.get("created_at") or meta.get("started_at") or "")
    if not stamp:
        return None
    try:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).total_seconds()


def lock_is_stale(
    meta: dict[str, Any],
    *,
    stale_after_sec: float = DEFAULT_STALE_AFTER_SEC,
    heartbeat_stale_sec: float = DEFAULT_HEARTBEAT_STALE_SEC,
) -> bool:
    if meta.get("corrupt"):
        return True
    wrapper_pid = int(meta.get("wrapper_pid") or 0)
    child_pid = int(meta.get("child_pid") or meta.get("pid") or 0)
    owners = [p for p in (wrapper_pid, child_pid) if p > 0]
    if owners and all(not _pid_alive(p) for p in owners):
        return True
    if not owners:
        # Legacy/corrupt without PID — treat as stale after age.
        age = _heartbeat_age_sec(meta)
        return age is None or age >= stale_after_sec
    age = _heartbeat_age_sec(meta)
    if age is None:
        return True
    if age >= stale_after_sec:
        return True
    # Missing/stale heartbeat while claiming a live owner is reclaimable only when PIDs are dead
    # (already handled). If PIDs are alive, never reclaim.
    if any(_pid_alive(p) for p in owners):
        return False
    return age >= heartbeat_stale_sec


def build_lock_payload(
    *,
    run_id: str,
    mode: str,
    git_sha: str = "unknown",
    story_no: str = "",
    wrapper_pid: int | None = None,
    child_pid: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = _utc_now()
    payload: dict[str, Any] = {
        "run_id": run_id,
        "host": socket.gethostname(),
        "wrapper_pid": int(wrapper_pid or 0) or None,
        "child_pid": int(child_pid or os.getpid()),
        "pid": int(child_pid or os.getpid()),  # backward compatible
        "created_at": now,
        "started_at": now,
        "heartbeat_at": now,
        "git_sha": git_sha,
        "story_no": story_no,
        "mode": mode,
    }
    if extra:
        payload.update(extra)
    return payload


def write_lock_atomic(lock: Path, payload: dict[str, Any]) -> Path:
    lock.parent.mkdir(parents=True, exist_ok=True)
    tmp = lock.with_suffix(lock.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(lock)
    return lock


def touch_lock_heartbeat(lock: Path, **fields: Any) -> None:
    if not lock.exists():
        return
    meta = read_lock_meta(lock)
    if meta.get("corrupt"):
        return
    meta["heartbeat_at"] = _utc_now()
    for key, value in fields.items():
        if value is not None:
            meta[key] = value
    write_lock_atomic(lock, meta)


def acquire_pipeline_lock(
    project_root: Path,
    *,
    stale_after_sec: float = DEFAULT_STALE_AFTER_SEC,
    validation: bool = False,
    run_id: str | None = None,
    mode: str = "prod",
    git_sha: str = "unknown",
    story_no: str = "",
    wrapper_pid: int | None = None,
    child_pid: int | None = None,
) -> Path:
    """Acquire exclusive pipeline lock; reclaim only when owners are absent/stale."""
    lock = lock_path_for(project_root, validation=validation)
    if lock.exists():
        meta = read_lock_meta(lock)
        if lock_is_stale(meta, stale_after_sec=stale_after_sec):
            lock.unlink(missing_ok=True)
            if not validation:
                try:
                    from .csv_store import reset_processing_to_pending

                    reset_processing_to_pending(project_root)
                except Exception:
                    pass
        else:
            detail = meta.get("run_id") or meta.get("pid") or meta.get("created_at") or "unknown"
            raise RuntimeError(
                f"Another pipeline run appears to be in progress ({lock.name}; holder={detail})."
            )

    payload = build_lock_payload(
        run_id=run_id or f"local-{os.getpid()}-{int(time.time())}",
        mode=("validate" if validation else mode),
        git_sha=git_sha,
        story_no=story_no,
        wrapper_pid=wrapper_pid,
        child_pid=child_pid,
    )
    return write_lock_atomic(lock, payload)


def release_pipeline_lock(
    lock_path: Path,
    *,
    owner_pid: int | None = None,
    run_id: str | None = None,
    force: bool = False,
) -> bool:
    """Owner-only deletion unless force=True (tests / explicit reclaim)."""
    if not lock_path.exists():
        return False
    meta = read_lock_meta(lock_path)
    if not force:
        if run_id and meta.get("run_id") and meta.get("run_id") != run_id:
            return False
        holders = [
            int(meta.get("wrapper_pid") or 0),
            int(meta.get("child_pid") or 0),
            int(meta.get("pid") or 0),
        ]
        holders = [p for p in holders if p > 0]
        if owner_pid and holders and owner_pid not in holders:
            # Allow release if all holders are dead (crash recovery by same wrapper restart).
            if any(_pid_alive(p) for p in holders):
                return False
    lock_path.unlink(missing_ok=True)
    return True
