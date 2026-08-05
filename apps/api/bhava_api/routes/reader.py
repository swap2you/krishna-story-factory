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
from ..catalog.next_preview import apply_dynamic_next_preview
from ..config import get_settings
from ..db import get_session
from ..models import Story
from ..web_assets.builder import build_web_assets_for_package
from ..web_assets.story_parser import parse_story_markdown
from ..web_assets.waveform import write_peaks_json

router = APIRouter(prefix="/api/v1/stories", tags=["reader"])


def _web_assets_root() -> Path:
    return get_settings().web_assets_root


def _can_write_web_assets() -> bool:
    settings = get_settings()
    return bool(settings.web_assets_writable) and not settings.public_site


def _missing_web_asset_error(filename: str) -> HTTPException:
    settings = get_settings()
    if settings.public_site:
        return HTTPException(
            status_code=503,
            detail=(
                f"Required web asset '{filename}' is missing. "
                "Public deployments must ship pre-built web-assets; runtime generation is disabled."
            ),
        )
    return HTTPException(
        status_code=404,
        detail=(
            f"{filename} not available. "
            "Local on-demand generation requires BHAVA_WEB_ASSETS_WRITABLE=true "
            "and BHAVA_PUBLIC_SITE=false."
        ),
    )


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
    """Fallback: parse story.md from the package when pre-built web assets are missing.

    Only used in local writable mode. Public / read-only mode never falls back to
    generating derivatives from the package.
    """
    raw_path = package_file(story.package_path, "story.md")
    if raw_path is None:
        raise HTTPException(status_code=404, detail="Story content not available")
    raw = raw_path.read_text(encoding="utf-8")
    parsed = parse_story_markdown(raw)
    return parsed.reader_md, parsed.reader_txt


def ensure_web_assets(story: Story) -> Path:
    """Return web-assets dir for the story, building from package_path when allowed."""
    if not _can_write_web_assets():
        raise _missing_web_asset_error("web_manifest.json")

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
        if _can_write_web_assets():
            ensure_web_assets(story)
            path = _web_asset_path(padded, filename)
        else:
            raise _missing_web_asset_error(filename)
    if path is None:
        raise _missing_web_asset_error(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_reader_body(story: Story, *, markdown: bool) -> str:
    """Load reader body only after catalog visibility has already succeeded.

    Public deployments must never treat web-assets filesystem presence as
    authorization. Stories outside the indexed catalog raise 404 from
    ``_get_story_record`` before this helper runs.
    """
    padded = story.story_no.zfill(3)
    filename = "reader.md" if markdown else "reader.txt"

    asset = _web_asset_path(padded, filename)
    if asset is not None:
        body = asset.read_text(encoding="utf-8")
        return apply_dynamic_next_preview(body, padded)

    if not _can_write_web_assets():
        raise _missing_web_asset_error(filename)

    try:
        ensure_web_assets(story)
        asset = _web_asset_path(padded, filename)
        if asset is not None:
            body = asset.read_text(encoding="utf-8")
            return apply_dynamic_next_preview(body, padded)
    except HTTPException:
        pass
    md, txt = _parse_on_the_fly(story)
    body = md if markdown else txt
    return apply_dynamic_next_preview(body, padded)


@router.get("/{story_no}/reader", response_class=PlainTextResponse)
def reader_md(story_no: str, session: Session = Depends(get_session)) -> PlainTextResponse:
    """Clean reader markdown — no internal production blocks."""
    # Catalog visibility first: never serve filesystem reader assets for private stories.
    story = _get_story_record(session, story_no)
    return PlainTextResponse(
        _resolve_reader_body(story, markdown=True),
        media_type="text/markdown",
    )


@router.get("/{story_no}/reader.txt", response_class=PlainTextResponse)
def reader_txt(story_no: str, session: Session = Depends(get_session)) -> PlainTextResponse:
    """Plain-text reader download — no internal production blocks."""
    # Catalog visibility first: never serve filesystem reader assets for private stories.
    story = _get_story_record(session, story_no)
    return PlainTextResponse(
        _resolve_reader_body(story, markdown=False),
        media_type="text/plain",
    )

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


@router.get("/{story_no}/waveform")
def story_waveform(story_no: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Cached preview peaks so the browser never full-fetches MP3 for waveform drawing."""
    story = _get_story_record(session, story_no)
    padded = story.story_no.zfill(3)
    cache = _web_assets_root() / padded / "waveform.json"
    if cache.is_file():
        return JSONResponse(json.loads(cache.read_text(encoding="utf-8")))

    if not _can_write_web_assets():
        raise _missing_web_asset_error("waveform.json")

    mp3 = package_file(story.package_path, "narration.mp3")
    if mp3 is None:
        raise HTTPException(status_code=404, detail="Narration audio not found")
    payload = write_peaks_json(mp3, cache)
    return JSONResponse(payload)
