"""Package → portal-tab completeness contract for Stories 001–020.

When local packages and web-assets both exist, assert the derived assets required
by Listen / Read / Activities / Coloring / Source / Notes / Ślokas tabs.

Skips gracefully when assets are missing (CI without content fixture).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "output"
WEB_ASSETS_ROOT = ROOT / "data" / "web-assets"

REQUIRED_WEB_ASSETS = {
    "reader.md",
    "reader.txt",
    "source_links.json",
    "reflections.json",
    "shlokas.json",
    "sync.json",
    "waveform.json",
    "web_manifest.json",
}

PUBLIC_STORIES = [f"{n:03d}" for n in range(1, 21)]


def _package_dir(story_no: str) -> Path | None:
    matches = sorted(OUTPUT_ROOT.glob(f"{story_no}_*"))
    dirs = [p for p in matches if p.is_dir()]
    if len(dirs) == 1:
        return dirs[0]
    return None


def _web_dir(story_no: str) -> Path | None:
    dest = WEB_ASSETS_ROOT / story_no
    return dest if dest.is_dir() else None


def _stories_with_both() -> list[str]:
    return [
        story_no
        for story_no in PUBLIC_STORIES
        if _package_dir(story_no) is not None and _web_dir(story_no) is not None
    ]


@pytest.fixture(scope="module")
def stories_with_assets() -> list[str]:
    found = _stories_with_both()
    if not found:
        pytest.skip(
            "No Stories 001–020 with both output package and data/web-assets present; "
            "skip package-to-tabs contract (CI without content fixture)."
        )
    return found


@pytest.mark.content_release
def test_package_to_tabs_required_web_assets(stories_with_assets: list[str]) -> None:
    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        names = {p.name for p in dest.iterdir() if p.is_file()}
        missing = REQUIRED_WEB_ASSETS - names
        assert not missing, f"web-assets/{story_no} missing {sorted(missing)}"
        for name in REQUIRED_WEB_ASSETS:
            path = dest / name
            assert path.stat().st_size > 0, f"web-assets/{story_no}/{name} is empty"


@pytest.mark.content_release
def test_package_to_tabs_reader_nonempty(stories_with_assets: list[str]) -> None:
    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        for name in ("reader.md", "reader.txt"):
            text = (dest / name).read_text(encoding="utf-8").strip()
            assert text, f"web-assets/{story_no}/{name} must be non-empty for Read tab"


@pytest.mark.content_release
def test_package_to_tabs_source_links_reviewed(stories_with_assets: list[str]) -> None:
    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        payload = json.loads((dest / "source_links.json").read_text(encoding="utf-8"))
        assert isinstance(payload, list) and payload, f"source_links.json empty for {story_no}"
        reviewed = [
            row
            for row in payload
            if isinstance(row, dict) and str(row.get("review_status", "")).lower() == "reviewed"
        ]
        assert reviewed, (
            f"web-assets/{story_no}/source_links.json has no reviewed entries "
            "(Source tab requires reviewed provenance for public stories)."
        )
        assert any(row.get("vedabase_url") for row in reviewed), (
            f"web-assets/{story_no}/source_links.json reviewed rows lack vedabase_url"
        )


@pytest.mark.content_release
def test_package_to_tabs_shlokas_not_fake_pending(stories_with_assets: list[str]) -> None:
    """Reject status=pending with no decision/note (fake placeholder).

    Honest pending (empty shlokas + explanatory note) is allowed only when the
    reviewed registry does not yet claim a decision for that story.
    """
    from bhava_api.web_assets.reviewed_shlokas import REVIEWED_SHLOKAS

    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        payload = json.loads((dest / "shlokas.json").read_text(encoding="utf-8"))
        status = str(payload.get("status") or "").strip().lower()
        note = str(payload.get("note") or "").strip()
        shlokas = payload.get("shlokas")

        if story_no in REVIEWED_SHLOKAS:
            assert status == "reviewed", (
                f"web-assets/{story_no}/shlokas.json status={status!r} but "
                "REVIEWED_SHLOKAS has a decision — rebuild web-assets."
            )
            assert isinstance(shlokas, list) and shlokas, (
                f"web-assets/{story_no}/shlokas.json reviewed but shlokas list empty"
            )
            continue

        if status == "pending":
            assert note, (
                f"web-assets/{story_no}/shlokas.json is pending without a decision note "
                "(fake pending). Add an honest note or complete review."
            )
