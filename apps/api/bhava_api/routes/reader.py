"""Public reader endpoints that serve clean story content without internal production blocks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..catalog.filesystem import package_file
from ..config import get_settings
from ..db import get_session
from ..models import Story
from ..web_assets.builder import build_web_assets_for_package
from ..web_assets.story_parser import parse_story_markdown

router = APIRouter(prefix="/api/v1/stories", tags=["reader"])


def _web_assets_root() -> Path:
    return get_settings().repository_root / "data" / "web-assets"


def _web_asset_path(story_no: str, filename: str) -> Path | None:
    path = _web_assets_root() / story_no / filename
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


def ensure_web_assets(story: Story) -> Path:
    """Return web-assets dir for the story, building from package_path when missing."""
    padded = story.story_no.zfill(3)
    dest = _web_assets_root() / padded
    if (dest / "web_manifest.json").is_file():
        return dest
    package = Path(story.package_path)
    if not package.is_dir():
        raise HTTPException(status_code=404, detail="Story package not available")
    return build_web_assets_for_package(package, padded, _web_assets_root())


def _read_web_json(story: Story, filename: str) -> Any:
    padded = story.story_no.zfill(3)
    path = _web_asset_path(padded, filename)
    if path is None:
        ensure_web_assets(story)
        path = _web_asset_path(padded, filename)
    if path is None:
        raise HTTPException(status_code=404, detail=f"{filename} not available")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/{story_no}/reader", response_class=PlainTextResponse)
def reader_md(story_no: str, session: Session = Depends(get_session)) -> PlainTextResponse:
    """Clean reader markdown — no internal production blocks."""
    padded = story_no.zfill(3)

    asset = _web_asset_path(padded, "reader.md")
    if asset is not None:
        return PlainTextResponse(asset.read_text(encoding="utf-8"), media_type="text/markdown")

    story = _get_story_record(session, story_no)
    try:
        ensure_web_assets(story)
        asset = _web_asset_path(padded, "reader.md")
        if asset is not None:
            return PlainTextResponse(asset.read_text(encoding="utf-8"), media_type="text/markdown")
    except HTTPException:
        pass
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
    try:
        ensure_web_assets(story)
        asset = _web_asset_path(padded, "reader.txt")
        if asset is not None:
            return PlainTextResponse(asset.read_text(encoding="utf-8"), media_type="text/plain")
    except HTTPException:
        pass
    _, txt = _parse_on_the_fly(story)
    return PlainTextResponse(txt, media_type="text/plain")


@router.get("/{story_no}/sync")
def story_sync(story_no: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Narration follow-along cues (honest pending when not aligned)."""
    story = _get_story_record(session, story_no)
    data = _read_web_json(story, "sync.json")
    return JSONResponse(data)


@router.get("/{story_no}/reflections")
def story_reflections(story_no: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Teaching reflections seeded from package lessons (needs_review until curated)."""
    story = _get_story_record(session, story_no)
    data = _read_web_json(story, "reflections.json")
    return JSONResponse(data)


@router.get("/{story_no}/source-links")
def story_source_links(story_no: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Source / scripture link seeds from package manifest."""
    story = _get_story_record(session, story_no)
    data = _read_web_json(story, "source_links.json")
    return JSONResponse(data)


@router.get("/{story_no}/web-manifest")
def story_web_manifest(story_no: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Enrichment status snapshot for Studio / operators."""
    story = _get_story_record(session, story_no)
    data = _read_web_json(story, "web_manifest.json")
    return JSONResponse(data)
