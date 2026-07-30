from __future__ import annotations

import importlib
import os

import pytest
from fastapi.testclient import TestClient

from tests.support.catalog_fixture import build_public_catalog, write_package

pytestmark = pytest.mark.production_security


def test_public_app_omits_factory_router(monkeypatch, tmp_path):
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(tmp_path / "output"))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "9")

    import bhava_api.config
    import bhava_api.main

    bhava_api.config.get_settings.cache_clear() if hasattr(
        bhava_api.config.get_settings, "cache_clear"
    ) else None
    module = importlib.reload(bhava_api.main)

    paths = {
        path
        for route in module.create_app().routes
        if (path := getattr(route, "path", None))
    }
    assert not any("factory" in path for path in paths)
    assert "/docs" not in paths
    assert "/openapi.json" not in paths


def test_public_app_blocks_local_factory_routes(monkeypatch, tmp_path):
    """Route absence must also be observable over HTTP, not just in the route table."""
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(build_public_catalog(tmp_path / "output")))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_ALLOWED_HOSTS", "testserver")
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "9")

    import bhava_api.main

    with TestClient(bhava_api.main.create_app()) as client:
        assert client.get("/api/v1/stories").status_code == 200
        for path in ("/api/v1/local/status", "/api/v1/local/queue", "/api/v1/local/scheduler"):
            assert client.get(path).status_code == 404, path
        for path in ("/api/v1/local/generate-next", "/api/v1/local/preflight"):
            assert client.post(path).status_code == 404, path
        for path in ("/docs", "/redoc", "/openapi.json"):
            assert client.get(path).status_code == 404, path


def test_version_endpoint_contains_safe_release(monkeypatch, tmp_path):
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(tmp_path / "output"))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_ALLOWED_HOSTS", "testserver")
    monkeypatch.setenv("BHAVA_RELEASE_SHA", "abc123")
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "9")

    import bhava_api.main

    app = bhava_api.main.create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {
        "service": "bhava-api",
        "release_sha": "abc123",
        "environment": os.getenv("BHAVA_ENVIRONMENT", "development"),
        "public_story_max": 9,
    }


def test_default_allowed_hosts_reject_unknown_origin(monkeypatch, tmp_path):
    """The test harness widens BHAVA_ALLOWED_HOSTS; production defaults must not."""
    monkeypatch.delenv("BHAVA_ALLOWED_HOSTS", raising=False)
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(tmp_path / "output"))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))

    import bhava_api.config
    import bhava_api.main

    assert "testserver" not in bhava_api.config.get_settings().allowed_hosts

    app = bhava_api.main.create_app()
    with TestClient(app, headers={"host": "bhava.me"}) as client:
        assert client.get("/api/v1/stories").status_code == 200
        assert client.get("/api/v1/stories", headers={"host": "attacker.example"}).status_code == 400
        assert client.get("/api/v1/stories", headers={"host": "testserver"}).status_code == 400


def test_public_site_refuses_to_start_above_story_ceiling(monkeypatch, tmp_path):
    output = tmp_path / "output"
    build_public_catalog(output)
    write_package(output, "010")

    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "9")

    import bhava_api.main

    with pytest.raises(RuntimeError, match="Public content boundary violation"):
        with TestClient(bhava_api.main.create_app()):
            pass
