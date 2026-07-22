"""Loopback-only local factory status routes and disabled action controls."""
from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..config import get_settings
from ..csrf import require_csrf
from ..factory_adapter import perform

router = APIRouter(prefix="/api/v1/local", tags=["local-factory"])
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]"}


def require_loopback(request: Request) -> None:
    settings = get_settings()
    if not settings.enforce_loopback:
        return
    host = request.headers.get("host", "").lower().split(":", 1)[0]
    origin = request.headers.get("origin", "")
    if host not in _LOCAL_HOSTS or (origin and not any(item in origin.lower() for item in _LOCAL_HOSTS)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Local factory is loopback-only")


def _queue_rows() -> list[dict[str, str]]:
    path = get_settings().repository_root / "tracking" / "queue_state.csv"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@router.get("/status", dependencies=[Depends(require_loopback)])
def local_status(request: Request) -> dict:
    return {
        "loopback_only": get_settings().enforce_loopback,
        "factory_actions_enabled": get_settings().factory_actions_enabled,
        "csrf_token": request.app.state.csrf_token,
    }


@router.get("/queue", dependencies=[Depends(require_loopback)])
def queue() -> dict:
    rows = _queue_rows()
    return {"items": rows, "next_pending": next((row for row in rows if row.get("status") == "pending"), None)}


@router.get("/runs", dependencies=[Depends(require_loopback)])
def runs() -> dict:
    return {"runs": [], "note": "Run history is not yet indexed."}


@router.get("/scheduler", dependencies=[Depends(require_loopback)])
def scheduler() -> dict:
    return {"enabled": None, "note": "Scheduler state is not yet exposed by the Phase 0 adapter."}


@router.post("/preflight", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def preflight() -> dict:
    return perform("preflight")


@router.post("/generate-next", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def generate_next() -> dict:
    return perform("generate-next")


@router.post("/drive/readback", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def drive_readback() -> dict:
    return perform("drive-readback")


@router.post("/scheduler/enable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def scheduler_enable() -> dict:
    return {"status": "disabled", "detail": "Scheduler controls are not implemented in Phase 0."}


@router.post("/scheduler/disable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def scheduler_disable() -> dict:
    return {"status": "disabled", "detail": "Scheduler controls are not implemented in Phase 0."}
