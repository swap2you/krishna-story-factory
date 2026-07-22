"""Safe local serving for assets discovered in exact story packages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog.filesystem import package_file
from ..db import get_session
from ..models import Story

router = APIRouter(prefix="/api/v1/stories", tags=["media"])


@router.get("/{story_no}/assets/{filename}")
def serve_asset(story_no: str, filename: str, session: Session = Depends(get_session)) -> FileResponse:
    story = session.scalar(select(Story).where(Story.story_no == story_no.zfill(3)))
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    path = package_file(story.package_path, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(path, media_type=next(
        (asset.media_type for asset in story.assets if asset.filename == filename), None
    ))
