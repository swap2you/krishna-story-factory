"""Unified Platform draft scheduler must not call Story generation entrypoints."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.support.catalog_fixture import build_public_catalog

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def fixture_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    output = build_public_catalog(tmp_path / "output")
    monkeypatch.setenv("BHAVA_OUTPUT_ROOT", str(output))
    monkeypatch.setenv("BHAVA_CATALOG_DB", str(tmp_path / "catalog.sqlite"))
    monkeypatch.setenv("BHAVA_ENFORCE_LOOPBACK", "0")
    monkeypatch.setenv("BHAVA_FACTORY_ACTIONS_ENABLED", "0")
    monkeypatch.setenv("BHAVA_AUTO_WEB_ASSETS", "0")
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


def test_draft_scheduler_module_has_no_story_imports() -> None:
    path = ROOT / "apps" / "api" / "bhava_api" / "draft_scheduler.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    banned = {
        "krishna_story_factory",
        "run_daily_story",
        "factory_adapter",
        "scheduler_simulate",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in banned
            assert "pipeline" not in node.module


def test_draft_scheduler_dry_run_refuses_story_and_publish(fixture_client: TestClient) -> None:
    from bhava_api import draft_scheduler

    draft_scheduler.asserts_no_story_generation_imports()

    client = fixture_client
    status = client.get("/api/v1/local/status").json()
    csrf = status["csrf_token"]
    headers = {"X-Bhava-CSRF-Token": csrf}

    state = client.get("/api/v1/local/draft-scheduler").json()
    assert state["capabilities"]["can_trigger_story_generation"] is False
    assert state["capabilities"]["can_publish"] is False
    assert state["story_scheduler_unchanged"] is True
    assert "story_generation" in state["forbidden"]

    assert client.post("/api/v1/local/draft-scheduler/enable", headers=headers).status_code == 200
    configured = client.post(
        "/api/v1/local/draft-scheduler/configure",
        headers=headers,
        json={"queue": "vani", "dry_run": True, "max_retries": 1},
    )
    assert configured.status_code == 200
    assert configured.json()["controls"]["queue"] == "vani"

    dry = client.post(
        "/api/v1/local/draft-scheduler/enqueue-dry-run",
        headers=headers,
        json={"idempotency_key": "m4-test-1"},
    )
    assert dry.status_code == 200
    assert dry.json()["controls"]["status"] == "completed_dry_run"
    assert "no story generation" in (dry.json()["controls"]["last_log"] or "").lower()

    for action in ("approve", "merge", "deploy", "publish", "generate-story"):
        refused = client.post(f"/api/v1/local/draft-scheduler/{action}", headers=headers)
        assert refused.status_code == 200
        body = refused.json()
        assert body["status"] == "refused"
        assert body["can_trigger_story_generation"] is False


def test_story_scheduler_scripts_untouched_by_draft_module() -> None:
    """Regression: MWF story scheduler entrypoints still exist and are separate."""
    scheduled = ROOT / "scripts" / "run_daily_story_scheduled.ps1"
    create_next = ROOT / "scripts" / "create-next-bhava-story.ps1"
    assert scheduled.is_file()
    assert create_next.is_file()
    draft_src = (ROOT / "apps" / "api" / "bhava_api" / "draft_scheduler.py").read_text(encoding="utf-8")
    # Entrypoint names may appear only inside the forbidden-list constant — never as call sites.
    assert "import run_daily_story" not in draft_src
    assert "from krishna_story_factory" not in draft_src
    assert "perform(" not in draft_src
    assert "def run_daily_story" not in draft_src
    assert "STORY_GENERATION_ENTRYPOINTS" in draft_src
