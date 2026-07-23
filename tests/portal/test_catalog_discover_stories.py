from __future__ import annotations

from pathlib import Path

from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES, Package, _chapter_sort_key, discover_packages
from bhava_api.catalog.indexer import _normalize_story_no


def test_catalog_discovers_released_stories_001_through_007() -> None:
    packages = discover_packages()
    chapters = {str(package.manifest["chapter_no"]).zfill(3) for package in packages}
    assert {"001", "002", "003", "004", "005", "006", "007"} <= chapters
    for package in packages:
        if str(package.manifest.get("chapter_no", "")).zfill(3) in chapters:
            assert REQUIRED_PACKAGE_FILES <= package.files


def test_packages_sort_numerically_not_lexically() -> None:
    fake = [
        Package(Path("10"), {"chapter_no": 10}, frozenset()),
        Package(Path("2"), {"chapter_no": 2}, frozenset()),
        Package(Path("1"), {"chapter_no": "001"}, frozenset()),
    ]
    ordered = sorted(fake, key=_chapter_sort_key)
    assert [p.manifest["chapter_no"] for p in ordered] == ["001", 2, 10]


def test_normalize_story_no_rejects_missing_and_zero() -> None:
    assert _normalize_story_no(None) is None
    assert _normalize_story_no("") is None
    assert _normalize_story_no("   ") is None
    assert _normalize_story_no(0) is None
    assert _normalize_story_no("000") is None
    assert _normalize_story_no(7) == "007"
    assert _normalize_story_no("4") == "004"
    assert _normalize_story_no("010") == "010"
