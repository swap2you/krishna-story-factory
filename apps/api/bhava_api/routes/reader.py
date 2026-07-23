"""Public reader endpoints that serve clean story content without internal production blocks."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog.filesystem import package_file
from ..config import get_settings
from ..db import get_session
from ..models import Story
from ..web_assets.story_parser import parse_story_markdown

router = APIRouter(prefix="/api/v1/stories", tags=["reader"])


def _web_asset_path(story_no: str, filename: str) -> Path | None:
    settings = get_settings()
    path = settings.repository_root / "data" / "web-assets" / story_no / filename
    return path if path.is_file() else None


def _get_story_record(session: Session, story_no: str) -> Story:
    story = session.scalar(
        select(Story).where(Story.story_no == story_no.zfill(3))
    )
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


def _parse_on_the_fly(story: Story) -> tuple[str, str]:
    """Fallback: parse story.md from the package when pre-built web assets are missing."""
    raw_path = package_file(story.package_path, "story.md")
    if raw_path is None:
        raise HTTPException(status_code=404, detail="Story content not available")
    raw = raw_path.read_text(encoding="utf-8")
    parsed = parse_story_markdown(raw)
    return parsed.reader_md, parsed.reader_txt


@router.get("/{story_no}/reader", response_class=PlainTextResponse)
def reader_md(story_no: str, session: Session = Depends(get_session)) -> PlainTextResponse:
    """Clean reader markdown — no internal production blocks."""
    padded = story_no.zfill(3)

    asset = _web_asset_path(padded, "reader.md")
    if asset is not None:
        return PlainTextResponse(asset.read_text(encoding="utf-8"), media_type="text/markdown")

    story = _get_story_record(session, story_no)
    md, _ = _parse_on_the_fly(story)
    return PlainTextResponse(md, media_type="text/markdown")


@router.get("/{story_no}/reader.txt", response_class=PlainTextResponse)
def reader_txt(story_no: str, session: Session = Depends(get_session)) -> PlainTextResponse:
    """Plain-text reader download — no internal production blocks."""
    padded = story_no.zfill(3)

    asset = _web_asset_path(padded, "reader.txt")
    if asset is not None:
        return PlainTextResponse(asset.read_text(encoding="utf-8"), media_type="text/plain")

    story = _get_story_record(session, story_no)
    _, txt = _parse_on_the_fly(story)
    return PlainTextResponse(txt, media_type="text/plain")
