"""Safe local serving for assets discovered in exact story packages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..catalog.filesystem import asset_media_type, package_file
from ..db import get_session
from ..models import Story

router = APIRouter(prefix="/api/v1/stories", tags=["media"])


def _resolve_asset(story_no: str, filename: str, session: Session):
    story = session.scalar(
        select(Story)
        .options(selectinload(Story.assets))
        .where(Story.story_no == story_no.zfill(3))
    )
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    path = package_file(story.package_path, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    media_type = next(
        (asset.media_type for asset in story.assets if asset.filename == filename and asset.media_type),
        None,
    ) or asset_media_type(filename)
    return path, media_type


@router.api_route("/{story_no}/assets/{filename}", methods=["GET", "HEAD"])
def serve_asset(
    story_no: str,
    filename: str,
    request: Request,
    session: Session = Depends(get_session),
):
    path, media_type = _resolve_asset(story_no, filename, session)
    if request.method == "HEAD":
        size = path.stat().st_size
        return Response(
            status_code=200,
            media_type=media_type,
            headers={
                "content-length": str(size),
                "accept-ranges": "bytes",
            },
        )
    return FileResponse(path, media_type=media_type)
