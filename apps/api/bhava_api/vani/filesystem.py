"""Filesystem loader for the local Krishna Book dictation archive."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from pydantic import ValidationError

from ..config import get_settings
from .schemas import CollectionManifest, TrackManifest

TRACK_IDS = tuple(f"{number:02d}" for number in range(91))
_TRACK_ID_RE = re.compile(r"^(?:0[0-9]|[1-8][0-9]|90)$")


def archive_root() -> Path:
    configured = os.getenv("BHAVA_VANI_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (
        get_settings().repository_root
        / "content-local"
        / "vani"
        / "krishna-book-dictations"
        / "v1"
    ).resolve()


def normalize_track_id(track_id: str) -> str | None:
    value = str(track_id).strip()
    return value if _TRACK_ID_RE.fullmatch(value) else None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def load_collection(root: Path | None = None) -> CollectionManifest:
    base = (root or archive_root()).resolve()
    candidates = (
        base / "manifests" / "collection.json",
        base / "manifests" / "collection_manifest.json",
        base / "collection_manifest.json",
    )
    for path in candidates:
        payload = _read_json(path)
        if payload is None:
            continue
        try:
            return CollectionManifest.model_validate(payload)
        except ValidationError:
            continue
    return CollectionManifest()


def load_tracks(root: Path | None = None) -> dict[str, TrackManifest]:
    base = (root or archive_root()).resolve()
    tracks: dict[str, TrackManifest] = {}
    for path in sorted((base / "manifests" / "tracks").glob("*.json")):
        payload = _read_json(path)
        if payload is None:
            continue
        try:
            track = TrackManifest.model_validate(payload)
        except ValidationError:
            continue
        track_id = normalize_track_id(track.canonical_track_id)
        if track_id is not None and track_id not in tracks:
            tracks[track_id] = track
    return tracks


def unavailable_track(track_id: str) -> dict[str, Any]:
    number = int(track_id)
    return {
        "track_id": track_id,
        "canonical_track_id": track_id,
        "canonical_title": "Introduction" if number == 0 else f"Chapter {number}",
        "availability": "unavailable",
        "stream_allowed": False,
        "audio_url": None,
        "waveform_url": None,
    }


def safe_archive_file(
    relative_path: str | None,
    *,
    root: Path | None = None,
    suffix: str | None = None,
) -> Path | None:
    """Resolve only a relative file contained by the configured archive root."""
    if not relative_path or "\x00" in relative_path:
        return None
    posix = PurePosixPath(relative_path)
    windows = PureWindowsPath(relative_path)
    if posix.is_absolute() or windows.is_absolute() or ".." in posix.parts or ".." in windows.parts:
        return None
    base = (root or archive_root()).resolve()
    candidate = (base / Path(relative_path)).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    if suffix is not None and candidate.suffix.lower() != suffix.lower():
        return None
    return candidate if candidate.is_file() else None


def preferred_audio(track: TrackManifest, root: Path | None = None) -> Path | None:
    restored = safe_archive_file(track.restored.relative_path, root=root, suffix=".mp3")
    if restored is not None:
        return restored
    return safe_archive_file(track.original.relative_path, root=root, suffix=".mp3")


def waveform_file(track: TrackManifest, root: Path | None = None) -> Path | None:
    base = (root or archive_root()).resolve()
    relative_path = track.waveform_relative_path
    waveform = getattr(track, "waveform", None)
    if not relative_path and isinstance(waveform, dict):
        relative_path = waveform.get("relative_path") or waveform.get("peaks_relative_path")
    explicit = safe_archive_file(relative_path, root=base, suffix=".json")
    if explicit is not None:
        return explicit
    return safe_archive_file(
        f"waveforms/{track.canonical_track_id}.json",
        root=base,
        suffix=".json",
    )
