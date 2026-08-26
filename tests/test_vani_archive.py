from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from bhava_api.vani.filesystem import load_tracks, safe_archive_file  # noqa: E402
from bhava_api.vani.publish_gates import stream_allowed  # noqa: E402
from bhava_api.vani.routes import router  # noqa: E402
from bhava_api.vani.schemas import RightsManifest, RightsState  # noqa: E402


def _write_track(
    root: Path,
    track_id: str,
    *,
    rights_state: str = "PRIVATE_REVIEW_ALLOWED",
    public_stream_allowed: bool = False,
    audio: bytes = b"original-audio",
    restored: bytes | None = None,
) -> None:
    original_path = root / "original" / f"{track_id}.mp3"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(audio)
    restored_relative = None
    if restored is not None:
        restored_path = root / "restored" / f"{track_id}.mp3"
        restored_path.parent.mkdir(parents=True, exist_ok=True)
        restored_path.write_bytes(restored)
        restored_relative = f"restored/{track_id}.mp3"
    manifest = {
        "canonical_track_id": track_id,
        "canonical_title": "Introduction" if track_id == "00" else f"Chapter {int(track_id)}",
        "availability": "available",
        "rights": {
            "state": rights_state,
            "public_stream_allowed": public_stream_allowed,
        },
        "original": {"relative_path": f"original/{track_id}.mp3"},
        "restored": {"relative_path": restored_relative},
    }
    destination = root / "manifests" / "tracks" / f"{track_id}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest), encoding="utf-8")


@pytest.fixture()
def vani_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, Path]:
    archive = tmp_path / "vani"
    _write_track(archive, "00", restored=b"restored-listening-edition")
    _write_track(archive, "02")
    monkeypatch.setenv("BHAVA_VANI_ROOT", str(archive))
    monkeypatch.setenv("BHAVA_ENVIRONMENT", "staging")
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "0")
    app = FastAPI()
    app.include_router(router)
    return TestClient(app), archive


def test_inventory_includes_all_gaps(vani_client: tuple[TestClient, Path]) -> None:
    client, archive = vani_client
    assert set(load_tracks(archive)) == {"00", "02"}
    response = client.get("/api/v1/vani/krishna-book")
    assert response.status_code == 200
    tracks = response.json()["tracks"]
    assert len(tracks) == 91
    assert tracks[0]["canonical_track_id"] == "00"
    assert tracks[1]["availability"] == "unavailable"
    assert tracks[-1]["canonical_track_id"] == "90"


def test_rights_gate_distinguishes_private_and_public_production() -> None:
    private = RightsManifest(state=RightsState.PRIVATE_REVIEW_ALLOWED)
    approved = RightsManifest(
        state=RightsState.PUBLIC_REDISTRIBUTION_APPROVED,
        public_stream_allowed=True,
    )
    unresolved = RightsManifest()
    assert stream_allowed(private, environment="staging", public_site=True)
    assert not stream_allowed(private, environment="production", public_site=True)
    assert stream_allowed(approved, environment="production", public_site=True)
    assert not stream_allowed(unresolved, environment="development", public_site=False)


def test_archive_path_traversal_is_rejected(vani_client: tuple[TestClient, Path]) -> None:
    client, archive = vani_client
    assert safe_archive_file("../outside.mp3", root=archive) is None
    assert safe_archive_file(r"..\outside.mp3", root=archive) is None
    assert safe_archive_file(str(archive / "original" / "00.mp3"), root=archive) is None
    assert client.get("/api/v1/vani/krishna-book/%2e%2e%2f00/audio").status_code == 404


def test_range_requests_prefer_restored_audio(vani_client: tuple[TestClient, Path]) -> None:
    client, _ = vani_client
    response = client.get(
        "/api/v1/vani/krishna-book/00/audio",
        headers={"Range": "bytes=0-7"},
    )
    assert response.status_code == 206
    assert response.content == b"restored"
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.headers["accept-ranges"] == "bytes"
    assert response.headers["content-range"].startswith("bytes 0-7/")

    head = client.head(
        "/api/v1/vani/krishna-book/00/audio",
        headers={"Range": "bytes=-4"},
    )
    assert head.status_code == 206
    assert head.content == b""


def test_track_detail_skips_unavailable_neighbors(
    vani_client: tuple[TestClient, Path],
) -> None:
    client, _ = vani_client
    detail = client.get("/api/v1/vani/krishna-book/01").json()
    assert detail["availability"] == "unavailable"
    assert detail["previous_available_track_id"] == "00"
    assert detail["next_available_track_id"] == "02"
