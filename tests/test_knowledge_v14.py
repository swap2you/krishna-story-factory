"""V1.4 Knowledge roadmap + governance tests."""
from __future__ import annotations

import json
from pathlib import Path

from bhava_api.knowledge.governance import evaluate_publication
from bhava_api.knowledge.search import search_knowledge

ROOT = Path(__file__).resolve().parents[1]


def test_roadmap_import_count_exact_348():
    records = json.loads((ROOT / "content/knowledge/roadmap/records.json").read_text(encoding="utf-8"))
    index = json.loads((ROOT / "content/knowledge/roadmap/index.json").read_text(encoding="utf-8"))
    assert len(records) == 348
    assert index["total"] == 348
    assert len({r["id"] for r in records}) == 348


def test_public_search_excludes_source_research():
    result = search_knowledge("bhakti", include_private=False, limit=100)
    assert result["count"] == 0 or all(
        row["lifecycle"] in {"approved", "published"} for row in result["results"]
    )


def test_private_search_sees_roadmap():
    result = search_knowledge("Sanatana", include_private=True, limit=20)
    assert result["count"] >= 1


def test_publication_gate_blocks_confidential():
    result = evaluate_publication(
        {
            "rights": {"status": "cleared"},
            "contains_sacred_text": False,
            "confidential": True,
            "required_reviewer_completed": True,
            "source_tier": "A1",
            "title": "test",
            "body": "",
        }
    )
    assert result.ok is False
    assert "confidential_content" in result.reasons
