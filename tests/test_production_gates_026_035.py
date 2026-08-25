"""Production publish gates for Stories 026–035 after owner promotion."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES, Package
from bhava_api.catalog.publish_gates import (
    is_catalog_indexable,
    is_private_staging_eligible,
    is_publicly_publishable,
)

pytestmark = pytest.mark.content_release

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
STAGING_NOTE = "Private staging review. Production publication requires owner approval."


def _pkg(story_no: str) -> Package:
    matches = sorted(OUTPUT.glob(f"{story_no}_*"))
    assert len(matches) == 1, matches
    path = matches[0]
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    files = frozenset(p.name for p in path.iterdir() if p.is_file())
    return Package(path, manifest, files)


@pytest.mark.parametrize("story_no", [f"{n:03d}" for n in range(26, 36)])
def test_026_035_production_publishable(story_no: str) -> None:
    pkg = _pkg(story_no)
    assert REQUIRED_PACKAGE_FILES.issubset(pkg.files)
    assert pkg.manifest.get("publishable") is True
    assert pkg.manifest.get("private_staging_eligible") is True
    review = pkg.manifest.get("review") or {}
    assert review.get("human_approval_complete") is True
    assert review.get("owner_production_approval") is True
    assert review.get("production_publishable") is True
    assert review.get("production_publication_requires_owner_approval") is False
    publication = pkg.manifest.get("publication") or {}
    assert publication.get("status") == "published"
    assert publication.get("visibility") == "public"
    assert publication.get("catalog_exposure") == "public"
    assert int(publication.get("public_ceiling") or 0) == 35
    assert is_publicly_publishable(pkg) is True
    assert is_catalog_indexable(pkg, environment="production", public_site=True) is True


def test_030_senior_review_not_falsely_complete() -> None:
    pkg = _pkg("030")
    review = pkg.manifest.get("review") or {}
    assert review.get("senior_devotional_review_complete") is False
    assert review.get("owner_publication_approval_overrides_pending_senior_review") is True


def test_030_poster_child_safety_attestation() -> None:
    pkg = _pkg("030")
    poster = pkg.path / "story_poster.png"
    expected = (pkg.manifest.get("file_sha256") or {}).get("story_poster.png", "").upper()
    actual = hashlib.sha256(poster.read_bytes()).hexdigest().upper()
    assert actual == expected


def test_029_poster_hash_matches_disk() -> None:
    pkg = _pkg("029")
    expected = (pkg.manifest.get("file_sha256") or {}).get("story_poster.png", "").upper()
    actual = hashlib.sha256((pkg.path / "story_poster.png").read_bytes()).hexdigest().upper()
    assert actual == expected


@pytest.mark.parametrize("story_no", [f"{n:03d}" for n in range(26, 36)])
def test_026_035_story_md_has_no_staging_process_wording(story_no: str) -> None:
    text = (_pkg(story_no).path / "story.md").read_text(encoding="utf-8")
    assert STAGING_NOTE not in text
    assert "PRIVATE draft" not in text
    assert "paid audio" not in text.lower()


def test_staging_eligibility_still_works_for_private_staging_gate(story_no: str = "026") -> None:
    pkg = _pkg(story_no)
    assert is_private_staging_eligible(pkg) is True
