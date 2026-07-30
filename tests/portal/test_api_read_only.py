from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.support.catalog_fixture import build_public_catalog


@pytest.fixture()
def fixture_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A portal client backed by a deterministic nine-story fixture catalog."""
    output = build_public_catalog(tmp_path / "output")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_ENFORCE_LOOPBACK", "0")
    monkeypatch.setenv("BHAVA_FACTORY_ACTIONS_ENABLED", "0")
    monkeypatch.setenv("BHAVA_AUTO_WEB_ASSETS", "0")
    # Local operator mode: the factory router is mounted but every action must
    # refuse to run. Public production removes the router entirely, which
    # test_public_production_boundary.py asserts separately.
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "0")

    import bhava_api.db as db_mod
    import bhava_api.main as main_mod
    from bhava_api.catalog.freshness import catalog_freshness

    db_mod.engine = db_mod.make_engine()
    db_mod.SessionLocal.configure(bind=db_mod.engine)
    db_mod.Base.metadata.create_all(bind=db_mod.engine)
    catalog_freshness.min_interval_sec = 0.01
    catalog_freshness._fingerprint = ""
    catalog_freshness._last_refresh = 0.0

    with TestClient(main_mod.create_app()) as client:
        yield client


def test_catalog_endpoints_and_disabled_factory(fixture_client: TestClient) -> None:
    client = fixture_client
    assert client.get("/api/v1/health").json()["status"] == "ok"
    stories = client.get("/api/v1/stories")
    assert stories.status_code == 200
    assert [item["story_no"] for item in stories.json()] == [f"{n:03d}" for n in range(1, 10)]
    assert client.get("/api/v1/search", params={"q": "Chapter 4"}).status_code == 200
    status = client.get("/api/v1/local/status").json()
    result = client.post(
        "/api/v1/local/generate-next",
        headers={"X-Bhava-CSRF-Token": status["csrf_token"]},
    )
    assert result.status_code == 200
    assert result.json()["status"] == "disabled"


def test_media_route_rejects_path_traversal(fixture_client: TestClient) -> None:
    response = fixture_client.get("/api/v1/stories/007/assets/%2e%2e%2f.env")
    assert response.status_code == 404


def test_media_route_sets_content_type_even_without_indexed_asset(
    fixture_client: TestClient,
) -> None:
    """manifest.json is contract-served but not always present in Asset rows."""
    response = fixture_client.get("/api/v1/stories/007/assets/manifest.json")
    assert response.status_code == 200
    assert "json" in response.headers["content-type"]
    md = fixture_client.get("/api/v1/stories/007/assets/story.md")
    assert md.status_code == 200
    assert md.headers.get("content-type")
