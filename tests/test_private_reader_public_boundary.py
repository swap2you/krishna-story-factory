"""P0 regression: private reader projections must obey catalog visibility.

Reproduces shared-mount architecture:
- public_site=true
- public_story_max=20 (production) or 22 (staging)
- indexed catalog capped at max
- filesystem/web-assets may still contain packages above max
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.portal.test_catalog_readiness_hotfix import _reload_app, _write_web_assets
from tests.support.catalog_fixture import build_public_catalog, write_package

pytestmark = pytest.mark.production_security

READER_PY = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "api"
    / "bhava_api"
    / "routes"
    / "reader.py"
)

PROJECTION_SUFFIXES = (
    "",
    "/reader",
    "/reader.txt",
    "/source-links",
    "/shlokas",
    "/reflections",
    "/web-manifest",
    "/sync",
    "/waveform",
    "/assets/story_poster.png",
    "/assets/narration.mp3",
    "/assets/activity_sheet.pdf",
)


def _shared_mount_app(
    monkeypatch,
    tmp_path,
    *,
    story_max: int,
    indexed_count: int,
    disk_count: int,
):
    """Build public app where disk/web assets may exceed the indexed ceiling."""
    output = build_public_catalog(tmp_path / "output", count=indexed_count)
    for extra in range(indexed_count + 1, disk_count + 1):
        write_package(output, f"{extra:03d}")
    web = tmp_path / "web-assets"
    _write_web_assets(web, disk_count)
    db = tmp_path / "catalog.sqlite"
    return _reload_app(
        monkeypatch,
        output,
        db,
        web,
        public=True,
        story_max=story_max,
    )


def test_reader_handlers_require_story_record_before_filesystem() -> None:
    """Static AST guard: reader routes must resolve the Story record before assets."""
    tree = ast.parse(READER_PY.read_text(encoding="utf-8"))
    handlers = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in {"reader_md", "reader_txt"}
    }
    assert set(handlers) == {"reader_md", "reader_txt"}
    for name, node in handlers.items():
        # Sort by source location; ast.walk() alone is not source-order stable.
        calls: list[tuple[int, int, str]] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name):
                    label = func.id
                elif isinstance(func, ast.Attribute):
                    label = func.attr
                else:
                    continue
                calls.append((child.lineno, child.col_offset, label))
        ordered = [label for _, _, label in sorted(calls)]
        assert "_get_story_record" in ordered, f"{name} must call _get_story_record"
        assert "_resolve_reader_body" in ordered, f"{name} must use shared resolver"
        assert ordered.index("_get_story_record") < ordered.index("_resolve_reader_body"), name
        assert "_web_asset_path" not in ordered, (
            f"{name} must not call _web_asset_path directly; resolve Story first"
        )


def test_production_reader_boundary_shared_mount(monkeypatch, tmp_path):
    """Production max=20 with 001-022 on disk: private readers must 404."""
    app = _shared_mount_app(
        monkeypatch, tmp_path, story_max=20, indexed_count=20, disk_count=22
    )
    with TestClient(app) as client:
        assert client.get("/api/v1/stories/020/reader").status_code == 200
        assert client.get("/api/v1/stories/020/reader.txt").status_code == 200
        for story in ("021", "022", "023"):
            assert client.get(f"/api/v1/stories/{story}/reader").status_code == 404, story
            assert client.get(f"/api/v1/stories/{story}/reader.txt").status_code == 404, story
        version = client.get("/api/v1/version").json()
        assert version["public_story_max"] == 20
        assert version["indexed_story_count"] == 20
        assert version["discovered_package_count"] >= 22


def test_staging_reader_boundary_shared_mount(monkeypatch, tmp_path):
    """Staging max=22: 021/022 readers visible; 023 still 404 even with disk assets."""
    app = _shared_mount_app(
        monkeypatch, tmp_path, story_max=22, indexed_count=22, disk_count=23
    )
    with TestClient(app) as client:
        assert client.get("/api/v1/stories/021/reader").status_code == 200
        assert client.get("/api/v1/stories/021/reader.txt").status_code == 200
        assert client.get("/api/v1/stories/022/reader").status_code == 200
        assert client.get("/api/v1/stories/022/reader.txt").status_code == 200
        assert client.get("/api/v1/stories/023/reader").status_code == 404
        assert client.get("/api/v1/stories/023/reader.txt").status_code == 404
        version = client.get("/api/v1/version").json()
        assert version["public_story_max"] == 22
        assert version["indexed_story_count"] == 22


@pytest.mark.parametrize("suffix", PROJECTION_SUFFIXES)
@pytest.mark.parametrize("story_no", ["021", "022"])
def test_production_all_projections_404_above_max(monkeypatch, tmp_path, story_no, suffix):
    app = _shared_mount_app(
        monkeypatch, tmp_path, story_max=20, indexed_count=20, disk_count=22
    )
    with TestClient(app) as client:
        path = f"/api/v1/stories/{story_no}{suffix}"
        assert client.get(path).status_code == 404, path


def test_caddyfile_production_only_private_reader_deny() -> None:
    caddy = (
        Path(__file__).resolve().parents[1] / "deploy" / "ionos" / "Caddyfile"
    ).read_text(encoding="utf-8")
    assert "private_reader_api" in caddy
    # Must live in bhava.me production site, not staging / common_security alone.
    prod = caddy.split("bhava.me {", 1)[1].split("www.bhava.me", 1)[0]
    staging = caddy.split("staging.bhava.me {", 1)[1]
    assert "private_reader_api" in prod
    assert "private_reader_api" not in staging
    assert "@private_reader_api" in prod
