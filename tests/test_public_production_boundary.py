from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient


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
