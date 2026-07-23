"""Isolated tests for live catalog refresh and publish gates."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bhava_api.catalog.freshness import catalog_freshness
from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES
from bhava_api.catalog.publish_gates import is_publicly_publishable
from bhava_api.catalog.filesystem import Package


REQUIRED = sorted(REQUIRED_PACKAGE_FILES)


def _write_package(
    root: Path,
    chapter: str,
    *,
    publishable: bool = True,
    quality: str = "PASS",
    audio_stale: bool = False,
    generation_verified: bool = True,
    include_all_files: bool = True,
) -> Path:
    folder = root / f"{chapter}_fixture"
    folder.mkdir(parents=True, exist_ok=True)
    files = list(REQUIRED) if include_all_files else ["manifest.json", "story.md"]
    for name in files:
        if name == "manifest.json":
            continue
        (folder / name).write_bytes(b"fixture")
    manifest = {
        "chapter_no": chapter,
        "slug": f"fixture-{chapter}",
        "title": f"Fixture {chapter}",
        "publishable": publishable,
        "quality": {"status": quality, "errors": [], "warnings": []},
        "audio": {
            "generation_verified": generation_verified,
            "audio_stale": audio_stale,
        },
    }
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return folder


@pytest.fixture()
def temp_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    output = tmp_path / "output"
    db = tmp_path / "catalog.sqlite"
    output.mkdir()
    for chapter in ["001", "002", "003", "004", "005", "006", "007"]:
        _write_package(output, chapter)

    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(db))
    monkeypatch.setenv("BHAVA_ENFORCE_LOOPBACK", "0")
    monkeypatch.setenv("BHAVA_FACTORY_ACTIONS_ENABLED", "0")

    # Rebuild engine/session against the temp DB.
    import bhava_api.db as db_mod
    import bhava_api.main as main_mod
    from bhava_api.config import get_settings

    get_settings.cache_clear = getattr(get_settings, "cache_clear", lambda: None)  # type: ignore
    db_mod.engine = db_mod.make_engine()
    db_mod.SessionLocal.configure(bind=db_mod.engine)
    db_mod.Base.metadata.create_all(bind=db_mod.engine)
    catalog_freshness.min_interval_sec = 0.01
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0

    app = main_mod.create_app()
    with TestClient(app) as client:
        yield client, output


def test_publish_gates_reject_incomplete_and_unpublished() -> None:
    good = Package(
        Path("x"),
        {
            "chapter_no": "008",
            "slug": "a",
            "title": "A",
            "publishable": True,
            "quality": {"status": "PASS"},
            "audio": {"generation_verified": True, "audio_stale": False},
        },
        frozenset(REQUIRED_PACKAGE_FILES),
    )
    assert is_publicly_publishable(good)
    incomplete = Package(Path("y"), good.manifest, frozenset({"manifest.json"}))
    assert not is_publicly_publishable(incomplete)
    unpublished = Package(Path("z"), {**good.manifest, "publishable": False}, frozenset(REQUIRED_PACKAGE_FILES))
    assert not is_publicly_publishable(unpublished)


def test_dynamic_catalog_adds_and_removes_without_restart(temp_catalog) -> None:
    client, output = temp_catalog
    stories = client.get("/api/v1/stories").json()
    assert [s["story_no"] for s in stories] == [f"{i:03d}" for i in range(1, 8)]

    _write_package(output, "008")
    catalog_freshness._last_refresh = 0.0
    stories = client.get("/api/v1/stories").json()
    assert [s["story_no"] for s in stories] == [f"{i:03d}" for i in range(1, 9)]

    _write_package(output, "009", include_all_files=False)
    _write_package(output, "010", publishable=False)
    catalog_freshness._last_refresh = 0.0
    numbers = [s["story_no"] for s in client.get("/api/v1/stories").json()]
    assert "009" not in numbers
    assert "010" not in numbers
    assert numbers == [f"{i:03d}" for i in range(1, 9)]

    folder = output / "008_fixture"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    manifest["quality"]["status"] = "FAIL"
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    catalog_freshness._last_refresh = 0.0
    numbers = [s["story_no"] for s in client.get("/api/v1/stories").json()]
    assert "008" not in numbers
    assert numbers == [f"{i:03d}" for i in range(1, 8)]
