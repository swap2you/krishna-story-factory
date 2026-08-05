"""Regression tests for empty-catalog / incomplete-scan production safeguards."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from bhava_api.catalog.freshness import catalog_freshness
from bhava_api.catalog.indexer import index_packages
from bhava_api.catalog.readiness import CatalogReadinessError
from bhava_api.db import SessionLocal
from bhava_api.models import Story
from tests.support.catalog_fixture import build_public_catalog, write_package


REQUIRED_WEB = (
    "reader.md",
    "reader.txt",
    "source_links.json",
    "reflections.json",
    "shlokas.json",
    "sync.json",
    "waveform.json",
    "web_manifest.json",
)


def _write_web_assets(root: Path, count: int) -> None:
    for number in range(1, count + 1):
        story_no = f"{number:03d}"
        dest = root / story_no
        dest.mkdir(parents=True, exist_ok=True)
        assets = {}
        for name in REQUIRED_WEB:
            if name == "web_manifest.json":
                continue
            path = dest / name
            if name.endswith(".json"):
                path.write_text("{}", encoding="utf-8")
            else:
                path.write_text("x", encoding="utf-8")
            assets[name] = {"sha256": "a" * 64, "bytes": max(1, path.stat().st_size)}
        (dest / "web_manifest.json").write_text(
            json.dumps(
                {
                    "package_manifest_sha256": "b" * 64,
                    "story_md_sha256": "c" * 64,
                    "generated_at": "2026-08-01T00:00:00Z",
                    "assets": assets,
                }
            ),
            encoding="utf-8",
        )


def _reload_app(monkeypatch, output: Path, db: Path, web: Path, *, public: bool, story_max: int):
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1" if public else "0")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(db))
    monkeypatch.setenv("BHAVA_WEB_ASSETS_ROOT", str(web))
    monkeypatch.setenv("BHAVA_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", str(story_max))
    monkeypatch.setenv("BHAVA_ENFORCE_LOOPBACK", "0")
    monkeypatch.setenv("BHAVA_FACTORY_ACTIONS_ENABLED", "0")
    monkeypatch.setenv("BHAVA_RELEASE_SHA", "hotfixsha123")

    import bhava_api.db as db_mod
    import bhava_api.main as main_mod

    db_mod.engine = db_mod.make_engine()
    db_mod.SessionLocal.configure(bind=db_mod.engine)
    db_mod.Base.metadata.create_all(bind=db_mod.engine)
    catalog_freshness.min_interval_sec = 0.01
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0
    catalog_freshness._indexed = 0
    return main_mod.create_app()


def test_complete_public_index_keeps_twenty(monkeypatch, tmp_path):
    output = build_public_catalog(tmp_path / "output", count=20)
    web = tmp_path / "web-assets"
    _write_web_assets(web, 20)
    db = tmp_path / "catalog.sqlite"
    app = _reload_app(monkeypatch, output, db, web, public=True, story_max=20)
    with TestClient(app) as client:
        stories = client.get("/api/v1/stories").json()
        assert len(stories) == 20
        assert stories[0]["story_no"] == "001"
        assert stories[-1]["story_no"] == "020"
        assert client.get("/readyz").status_code == 200
        version = client.get("/api/v1/version").json()
        assert version["indexed_story_count"] == 20
        assert version["discovered_package_count"] == 20
        assert version["public_story_max"] == 20
        assert version["short_sha"] == "hotfixs"


def test_zero_scan_preserves_last_known_good(monkeypatch, tmp_path):
    output = build_public_catalog(tmp_path / "output", count=20)
    web = tmp_path / "web-assets"
    _write_web_assets(web, 20)
    db = tmp_path / "catalog.sqlite"
    app = _reload_app(monkeypatch, output, db, web, public=True, story_max=20)
    with TestClient(app):
        with SessionLocal() as session:
            assert session.scalar(select(func.count()).select_from(Story)) == 20

    # Wipe packages (simulates empty bind mount) and attempt reindex.
    for child in output.iterdir():
        if child.is_dir():
            for file in child.iterdir():
                file.unlink()
            child.rmdir()

    with SessionLocal() as session:
        with pytest.raises(CatalogReadinessError):
            index_packages(session)
        count = session.scalar(select(func.count()).select_from(Story))
        assert count == 20


def test_incomplete_scan_preserves_rows(monkeypatch, tmp_path):
    output = build_public_catalog(tmp_path / "output", count=20)
    web = tmp_path / "web-assets"
    _write_web_assets(web, 20)
    db = tmp_path / "catalog.sqlite"
    app = _reload_app(monkeypatch, output, db, web, public=True, story_max=20)
    with TestClient(app):
        pass

    # Remove one package → 19 remain.
    target = next(p for p in output.iterdir() if p.name.startswith("020_"))
    for file in target.iterdir():
        file.unlink()
    target.rmdir()

    with SessionLocal() as session:
        with pytest.raises(CatalogReadinessError):
            index_packages(session)
        assert session.scalar(select(func.count()).select_from(Story)) == 20


def test_readyz_fails_on_catalog_mismatch(monkeypatch, tmp_path):
    output = build_public_catalog(tmp_path / "output", count=20)
    web = tmp_path / "web-assets"
    _write_web_assets(web, 20)
    db = tmp_path / "catalog.sqlite"
    app = _reload_app(monkeypatch, output, db, web, public=True, story_max=20)
    with TestClient(app) as client:
        assert client.get("/readyz").status_code == 200

    # Empty the mount after a healthy start; readiness must fail closed.
    for child in list(output.iterdir()):
        if child.is_dir():
            for file in child.iterdir():
                file.unlink()
            child.rmdir()
    catalog_freshness._fingerprint = "stale"
    catalog_freshness._last_refresh = 0.0

    with TestClient(app) as client:
        # Background/force refresh keeps rows; readyz still sees package mismatch.
        assert client.get("/readyz").status_code == 503


def test_story_021_stays_private(monkeypatch, tmp_path):
    output = build_public_catalog(tmp_path / "output", count=20)
    write_package(output, "021")
    web = tmp_path / "web-assets"
    _write_web_assets(web, 20)
    db = tmp_path / "catalog.sqlite"
    app = _reload_app(monkeypatch, output, db, web, public=True, story_max=20)
    with TestClient(app) as client:
        assert client.get("/api/v1/stories/020").status_code == 200
        assert client.get("/api/v1/stories/021").status_code == 404
        stories = client.get("/api/v1/stories").json()
        assert len(stories) == 20
        assert all(item["story_no"] != "021" for item in stories)
