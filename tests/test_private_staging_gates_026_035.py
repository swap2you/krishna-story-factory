"""Gates for private staging vs production publishability (026–035)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES, Package
from bhava_api.catalog.publish_gates import (
    is_catalog_indexable,
    is_private_staging_eligible,
    is_publicly_publishable,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def _pkg(story_no: str) -> Package:
    matches = sorted(OUTPUT.glob(f"{story_no}_*"))
    assert len(matches) == 1, matches
    path = matches[0]
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    files = frozenset(p.name for p in path.iterdir() if p.is_file())
    return Package(path, manifest, files)


@pytest.mark.parametrize("story_no", [f"{n:03d}" for n in range(26, 36)])
def test_026_035_production_not_publishable_but_private_staging_eligible(story_no: str) -> None:
    pkg = _pkg(story_no)
    assert REQUIRED_PACKAGE_FILES.issubset(pkg.files)
    assert pkg.manifest.get("publishable") is False
    assert pkg.manifest.get("private_staging_eligible") is True
    review = pkg.manifest.get("review") or {}
    assert review.get("human_approval_complete") is False
    assert review.get("private_staging_allowed") is True
    assert review.get("production_publication_requires_owner_approval") is True
    assert is_publicly_publishable(pkg) is False
    assert is_private_staging_eligible(pkg) is True
    assert is_catalog_indexable(pkg, environment="production", public_site=True) is False
    assert is_catalog_indexable(pkg, environment="staging", public_site=True) is True
    assert is_catalog_indexable(pkg, environment="development", public_site=False) is True


def test_030_poster_child_safety_attestation() -> None:
    """Regression: Story 030 poster must remain the approved child-safe bytes."""
    pkg = _pkg("030")
    poster = pkg.path / "story_poster.png"
    assert poster.is_file()
    expected = (pkg.manifest.get("file_sha256") or {}).get("story_poster.png", "").upper()
    assert len(expected) == 64
    import hashlib

    actual = hashlib.sha256(poster.read_bytes()).hexdigest().upper()
    assert actual == expected
    # Hard constraints encoded in package review / publication for operators.
    assert pkg.manifest.get("publishable") is False
    # Evidence from corrective regenerate must exist after Stage-1 lock.
    evidence = ROOT / "work" / "_030_poster_childsafe" / "poster_evidence.json"
    if evidence.is_file():
        data = json.loads(evidence.read_text(encoding="utf-8"))
        assert data["poster_sha256"].upper() == actual
        assert int(data["vision_score"]) >= 70
        assert data.get("hard_rejection") is False


def test_029_poster_hash_matches_disk() -> None:
    pkg = _pkg("029")
    expected = (pkg.manifest.get("file_sha256") or {}).get("story_poster.png", "").upper()
    import hashlib

    actual = hashlib.sha256((pkg.path / "story_poster.png").read_bytes()).hexdigest().upper()
    assert actual == expected


@pytest.mark.parametrize("story_no", [f"{n:03d}" for n in range(26, 36)])
def test_026_035_story_md_staging_review_wording(story_no: str) -> None:
    pkg = _pkg(story_no)
    text = (pkg.path / "story.md").read_text(encoding="utf-8")
    assert "Private staging review. Production publication requires owner approval." in text
    assert "PRIVATE draft" not in text
    assert "paid audio" not in text.lower()
