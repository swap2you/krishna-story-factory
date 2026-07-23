"""Isolated Story 008/009 fixture coverage for V1.2 automatic catalog integration."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bhava_api.catalog.freshness import catalog_freshness
from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES

REQUIRED = sorted(REQUIRED_PACKAGE_FILES)


def _write_package(root: Path, chapter: str, *, publishable: bool = True, include_all: bool = True) -> Path:
    folder = root / f"{chapter}_fixture"
    folder.mkdir(parents=True, exist_ok=True)
    names = list(REQUIRED) if include_all else ["manifest.json", "story.md"]
    for name in names:
        if name == "manifest.json":
            continue
        if name == "story.md":
            (folder / name).write_text("# Fixture\n\nBody\n", encoding="utf-8")
        else:
            (folder / name).write_bytes(b"fixture")
    (folder / "manifest.json").write_text(
        json.dumps(
            {
                "chapter_no": chapter,
                "slug": f"fixture-{chapter}",
                "title": f"Fixture {chapter}",
                "publishable": publishable,
                "quality": {"status": "PASS"},
                "audio": {"generation_verified": True, "audio_stale": False},
            }
        ),
        encoding="utf-8",
    )
    return folder


@pytest.fixture()
def isolated_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    output = tmp_path / "output"
    db = tmp_path / "catalog.sqlite"
    output.mkdir()
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(db))
    monkeypatch.setenv("BHAVA_ENFORCE_LOOPBACK", "0")
    monkeypatch.setenv("BHAVA_FACTORY_ACTIONS_ENABLED", "0")
    monkeypatch.setenv("BHAVA_AUTO_WEB_ASSETS", "0")

    import bhava_api.db as db_mod
    import bhava_api.main as main_mod

    db_mod.engine = db_mod.make_engine()
    db_mod.SessionLocal.configure(bind=db_mod.engine)
    db_mod.Base.metadata.create_all(bind=db_mod.engine)
    catalog_freshness.min_interval_sec = 0.01
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0

    app = main_mod.create_app()
    with TestClient(app) as client:
        yield client, output


def test_story_008_fixture_appears_after_refresh(isolated_client):
    client, output = isolated_client
    _write_package(output, "008", publishable=True)
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0
    stories = client.get("/api/v1/stories").json()
    assert any(item["story_no"] == "008" for item in stories)


def test_incomplete_009_excluded(isolated_client):
    client, output = isolated_client
    _write_package(output, "009", publishable=True, include_all=False)
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0
    stories = client.get("/api/v1/stories").json()
    assert all(item["story_no"] != "009" for item in stories)


def test_unpublishable_010_excluded(isolated_client):
    client, output = isolated_client
    _write_package(output, "010", publishable=False)
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0
    stories = client.get("/api/v1/stories").json()
    assert all(item["story_no"] != "010" for item in stories)


def test_required_package_contract_unchanged():
    assert "story.md" in REQUIRED_PACKAGE_FILES
    assert len(REQUIRED_PACKAGE_FILES) == 8
