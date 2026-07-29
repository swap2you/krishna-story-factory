"""Loopback-only local factory status routes and disabled action controls."""
from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..csrf import require_csrf
from ..db import get_session
from ..factory_adapter import perform
from ..models import Story
from ..web_assets.builder import build_web_assets_for_package

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


@router.post(
    "/rebuild-web-assets/{story_no}",
    dependencies=[Depends(require_loopback), Depends(require_csrf)],
)
def rebuild_web_assets(story_no: str, session: Session = Depends(get_session)) -> dict:
    """Rebuild data/web-assets for one story. Requires factory_actions_enabled (default off)."""
    settings = get_settings()
    if not settings.factory_actions_enabled:
        return {
            "operation": "rebuild-web-assets",
            "status": "disabled",
            "detail": (
                "Factory actions are disabled. Set BHAVA_FACTORY_ACTIONS_ENABLED=true "
                "only for intentional local ops."
            ),
            "story_no": story_no.zfill(3),
        }
    padded = story_no.zfill(3)
    story = session.scalar(select(Story).where(Story.story_no == padded))
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    package = Path(story.package_path)
    if not package.is_dir():
        raise HTTPException(status_code=404, detail="Story package not available")
    web_root = settings.repository_root / "data" / "web-assets"
    dest = build_web_assets_for_package(package, padded, web_root)
    return {
        "operation": "rebuild-web-assets",
        "status": "ok",
        "story_no": padded,
        "path": str(dest),
        "detail": f"Rebuilt web assets for story {padded}.",
    }


@router.post("/scheduler/enable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def scheduler_enable() -> dict:
    return {"status": "disabled", "detail": "Scheduler controls are not implemented in Phase 0."}


@router.post("/scheduler/disable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def scheduler_disable() -> dict:
    return {"status": "disabled", "detail": "Scheduler controls are not implemented in Phase 0."}
