"""Read-only catalog and ranged media routes for Prabhupāda Vāṇī."""
from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from ..config import get_settings
from .filesystem import (
    TRACK_IDS,
    archive_root,
    load_collection,
    load_tracks,
    normalize_track_id,
    preferred_audio,
    unavailable_track,
    waveform_file,
)
from .publish_gates import stream_allowed
from .schemas import TrackManifest

router = APIRouter(prefix="/api/v1/vani/krishna-book", tags=["vani"])
_CHUNK_SIZE = 1024 * 1024


def _can_stream(track: TrackManifest) -> bool:
    settings = get_settings()
    return stream_allowed(
        track.rights,
        environment=settings.environment,
        public_site=settings.public_site,
    )


def _playable(track: TrackManifest, root: Path) -> bool:
    return (
        track.availability.strip().lower() == "available"
        and _can_stream(track)
        and preferred_audio(track, root) is not None
    )


def _public_track(track: TrackManifest, root: Path) -> dict:
    payload = track.model_dump(mode="json")
    # Filesystem layout is an operator concern; clients receive stable API URLs.
    payload.get("original", {}).pop("relative_path", None)
    payload.get("restored", {}).pop("relative_path", None)
    if isinstance(payload.get("waveform"), dict):
        payload["waveform"].pop("relative_path", None)
        payload["waveform"].pop("peaks_relative_path", None)
    payload.pop("waveform_relative_path", None)
    track_id = track.canonical_track_id
    allowed = _playable(track, root)
    payload.update(
        {
            "track_id": track_id,
            "stream_allowed": allowed,
            "audio_url": (
                f"/api/v1/vani/krishna-book/{track_id}/audio" if allowed else None
            ),
            "waveform_url": (
                f"/api/v1/vani/krishna-book/{track_id}/waveform"
                if allowed and waveform_file(track, root) is not None
                else None
            ),
        }
    )
    return payload


def _neighbors(
    track_id: str,
    tracks: dict[str, TrackManifest],
    root: Path,
) -> tuple[str | None, str | None]:
    available = sorted(
        candidate_id
        for candidate_id, candidate in tracks.items()
        if _playable(candidate, root)
    )
    previous = next((item for item in reversed(available) if item < track_id), None)
    following = next((item for item in available if item > track_id), None)
    return previous, following


def _track_or_404(
    track_id: str,
) -> tuple[str, TrackManifest | None, dict[str, TrackManifest], Path]:
    normalized = normalize_track_id(track_id)
    if normalized is None:
        raise HTTPException(status_code=404, detail="Track not found")
    root = archive_root()
    tracks = load_tracks(root)
    return normalized, tracks.get(normalized), tracks, root


@router.get("")
def collection_catalog() -> dict:
    root = archive_root()
    collection = load_collection(root).model_dump(mode="json")
    tracks = load_tracks(root)
    records = [
        _public_track(tracks[track_id], root)
        if track_id in tracks
        else unavailable_track(track_id)
        for track_id in TRACK_IDS
    ]
    collection.update(
        {
            "tracks": records,
            "track_count": len(TRACK_IDS),
            "available_track_count": sum(
                record["availability"].strip().lower() == "available"
                for record in records
            ),
            "streamable_track_count": sum(bool(record["stream_allowed"]) for record in records),
        }
    )
    return collection


@router.get("/{track_id}")
def track_detail(track_id: str) -> dict:
    normalized, track, tracks, root = _track_or_404(track_id)
    payload = _public_track(track, root) if track is not None else unavailable_track(normalized)
    previous, following = _neighbors(normalized, tracks, root)
    payload["previous_available_track_id"] = previous
    payload["next_available_track_id"] = following
    return payload


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
        start, end = max(0, size - suffix), size - 1
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
        while remaining:
            chunk = handle.read(min(_CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def _audio_headers(path: Path) -> dict[str, str]:
    return {
        "accept-ranges": "bytes",
        "cache-control": "private, max-age=3600, must-revalidate",
        "content-disposition": f"inline; filename*=UTF-8''{quote(path.name, safe='')}",
        "x-content-type-options": "nosniff",
    }


@router.api_route("/{track_id}/audio", methods=["GET", "HEAD"])
def serve_audio(track_id: str, request: Request):
    _, track, _, root = _track_or_404(track_id)
    if track is None or track.availability.strip().lower() != "available":
        raise HTTPException(status_code=404, detail="Audio not found")
    if not _can_stream(track):
        raise HTTPException(status_code=403, detail="Audio streaming is not permitted")
    path = preferred_audio(track, root)
    if path is None:
        raise HTTPException(status_code=404, detail="Audio not found")

    size = path.stat().st_size
    headers = _audio_headers(path)
    range_value = request.headers.get("range")
    if range_value:
        try:
            start, end = _parse_range(range_value, size)
        except (TypeError, ValueError):
            return Response(
                status_code=416,
                headers={**headers, "content-range": f"bytes */{size}"},
            )
        length = end - start + 1
        headers.update(
            {
                "content-range": f"bytes {start}-{end}/{size}",
                "content-length": str(length),
            }
        )
        if request.method == "HEAD":
            return Response(status_code=206, media_type="audio/mpeg", headers=headers)
        return StreamingResponse(
            _iter_file(path, start, length),
            status_code=206,
            media_type="audio/mpeg",
            headers=headers,
        )

    headers["content-length"] = str(size)
    if request.method == "HEAD":
        return Response(status_code=200, media_type="audio/mpeg", headers=headers)
    return StreamingResponse(
        _iter_file(path, 0, size),
        media_type="audio/mpeg",
        headers=headers,
    )


@router.get("/{track_id}/waveform")
def serve_waveform(track_id: str):
    _, track, _, root = _track_or_404(track_id)
    if track is None or not _can_stream(track):
        raise HTTPException(status_code=404, detail="Waveform not found")
    path = waveform_file(track, root)
    if path is None:
        raise HTTPException(status_code=404, detail="Waveform not found")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=404, detail="Waveform not found") from exc
    return JSONResponse(
        payload,
        headers={
            "cache-control": "private, max-age=3600, must-revalidate",
            "x-content-type-options": "nosniff",
        },
    )
