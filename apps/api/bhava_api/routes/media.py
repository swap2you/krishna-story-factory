"""Safe serving for assets discovered in exact public story packages."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..catalog.filesystem import asset_media_type, package_file
from ..db import get_session
from ..models import Story

router = APIRouter(prefix="/api/v1/stories", tags=["media"])
_CHUNK_SIZE = 1024 * 1024


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


def _cache_control(path: Path) -> str:
    if path.suffix.lower() in {".mp3", ".png", ".pdf"}:
        return "public, max-age=86400, stale-while-revalidate=604800"
    return "public, max-age=3600, must-revalidate"


def _common_headers(path: Path, *, download: bool = False) -> dict[str, str]:
    encoded = quote(path.name, safe="")
    disposition = "attachment" if download else "inline"
    return {
        "accept-ranges": "bytes",
        "cache-control": _cache_control(path),
        "content-disposition": f"{disposition}; filename*=UTF-8''{encoded}",
        "x-content-type-options": "nosniff",
    }


def _parse_range(value: str, size: int) -> tuple[int, int]:
    if not value.startswith("bytes=") or "," in value:
        raise ValueError("unsupported range")
    start_text, end_text = value[6:].split("-", 1)
    if not start_text and not end_text:
        raise ValueError("empty range")

    if not start_text:
        suffix = int(end_text)
        if suffix <= 0:
            raise ValueError("invalid suffix")
        start = max(0, size - suffix)
        end = size - 1
    else:
        start = int(start_text)
        end = int(end_text) if end_text else size - 1

    if start < 0 or end < start or start >= size:
        raise ValueError("unsatisfiable range")
    return start, min(end, size - 1)


def _iter_file(path: Path, start: int, length: int) -> Iterator[bytes]:
    remaining = length
    with path.open("rb") as handle:
        handle.seek(start)
        while remaining > 0:
            chunk = handle.read(min(_CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


@router.api_route("/{story_no}/assets/{filename}", methods=["GET", "HEAD"])
def serve_asset(
    story_no: str,
    filename: str,
    request: Request,
    session: Session = Depends(get_session),
):
    path, media_type = _resolve_asset(story_no, filename, session)
    size = path.stat().st_size
    download = request.query_params.get("download", "").strip().lower() in {"1", "true", "yes"}
    headers = _common_headers(path, download=download)

    range_value = request.headers.get("range")
    if range_value:
        try:
            start, end = _parse_range(range_value, size)
        except (ValueError, TypeError):
            return Response(
                status_code=416,
                headers={**headers, "content-range": f"bytes */{size}"},
            )

        length = end - start + 1
        range_headers = {
            **headers,
            "content-range": f"bytes {start}-{end}/{size}",
            "content-length": str(length),
        }
        if request.method == "HEAD":
            return Response(status_code=206, media_type=media_type, headers=range_headers)
        return StreamingResponse(
            _iter_file(path, start, length),
            status_code=206,
            media_type=media_type,
            headers=range_headers,
        )

    headers["content-length"] = str(size)
    if request.method == "HEAD":
        return Response(status_code=200, media_type=media_type, headers=headers)
    return StreamingResponse(
        _iter_file(path, 0, size),
        status_code=200,
        media_type=media_type,
        headers=headers,
    )
