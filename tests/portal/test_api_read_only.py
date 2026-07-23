from __future__ import annotations

from fastapi.testclient import TestClient

from bhava_api.main import create_app


def test_public_catalog_endpoints_and_disabled_factory() -> None:
    with TestClient(create_app(), headers={"host": "127.0.0.1"}) as client:
        assert client.get("/api/v1/health").json()["status"] == "ok"
        stories = client.get("/api/v1/stories")
        assert stories.status_code == 200
        assert len(stories.json()) >= 7
        assert client.get("/api/v1/search", params={"q": "Chapter 4"}).status_code == 200
        status = client.get("/api/v1/local/status").json()
        result = client.post(
            "/api/v1/local/generate-next",
            headers={"X-Bhava-CSRF-Token": status["csrf_token"]},
        )
        assert result.status_code == 200
        assert result.json()["status"] == "disabled"


def test_media_route_rejects_path_traversal() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/stories/007/assets/%2e%2e%2f.env")
        assert response.status_code == 404


def test_media_route_sets_content_type_even_without_indexed_asset() -> None:
    """manifest.json is contract-served but not always present in Asset rows."""
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/stories/007/assets/manifest.json")
        assert response.status_code == 200
        assert response.headers.get("content-type")
        assert "json" in response.headers["content-type"]
        md = client.get("/api/v1/stories/007/assets/story.md")
        assert md.status_code == 200
        assert md.headers.get("content-type")
