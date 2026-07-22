from __future__ import annotations

from bhava_api.catalog.filesystem import REQUIRED_PACKAGE_FILES, discover_packages


def test_catalog_discovers_released_stories_001_through_007() -> None:
    packages = discover_packages()
    chapters = {str(package.manifest["chapter_no"]).zfill(3) for package in packages}
    assert {"001", "002", "003", "004", "005", "006", "007"} <= chapters
    for package in packages:
        if str(package.manifest.get("chapter_no", "")).zfill(3) in chapters:
            assert REQUIRED_PACKAGE_FILES <= package.files
