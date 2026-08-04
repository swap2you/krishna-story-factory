"""Verify the story parser strips ALL internal production material from reader output.

Parameterized exclusively from committed fixtures under tests/fixtures/story_reader/.
Never reads output/, work/, Dropbox, or absolute local developer paths.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from bhava_api.web_assets.story_parser import parse_story_markdown

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "story_reader"
FIXTURE_FILES = sorted(FIXTURE_ROOT.glob("*.md"))

LEAK_MARKERS = [
    "Audio Narration",
    "Poster Visual Brief",
    "Coloring Visual Brief",
    "Activity Data",
    "<break time=",
    "&lt;break",
]


def test_story_reader_fixtures_are_non_empty() -> None:
    """Zero fixture cases must never silently pass."""
    assert FIXTURE_ROOT.is_dir(), f"Missing fixture root: {FIXTURE_ROOT}"
    assert len(FIXTURE_FILES) >= 3, (
        f"Expected committed story_reader fixtures, found {len(FIXTURE_FILES)} in {FIXTURE_ROOT}"
    )


@pytest.fixture(params=FIXTURE_FILES, ids=[p.stem for p in FIXTURE_FILES])
def parsed(request: pytest.FixtureRequest):
    story_path: Path = request.param
    raw = story_path.read_text(encoding="utf-8")
    return parse_story_markdown(raw), story_path


class TestReaderLeakPrevention:
    """Each fixture must produce clean reader output free of internal blocks."""

    def test_no_internal_leak_markers_flag(self, parsed):
        result, story_path = parsed
        assert not result.has_internal_leak_markers, (
            f"{story_path.name}: reader still has leak markers"
        )

    @pytest.mark.parametrize("marker", LEAK_MARKERS, ids=LEAK_MARKERS)
    def test_reader_md_excludes_marker(self, parsed, marker):
        result, story_path = parsed
        assert marker not in result.reader_md, (
            f"{story_path.name}: reader_md contains '{marker}'"
        )

    @pytest.mark.parametrize("marker", LEAK_MARKERS, ids=LEAK_MARKERS)
    def test_reader_txt_excludes_marker(self, parsed, marker):
        result, story_path = parsed
        assert marker not in result.reader_txt, (
            f"{story_path.name}: reader_txt contains '{marker}'"
        )

    def test_no_html_comments(self, parsed):
        result, _ = parsed
        assert "<!--" not in result.reader_md
        assert "-->" not in result.reader_md

    def test_main_story_present(self, parsed):
        result, story_path = parsed
        assert "Main Story" in result.reader_md or len(result.reader_md) > 200, (
            f"{story_path.name}: Main Story content missing from reader"
        )

    def test_reader_txt_not_empty(self, parsed):
        result, _ = parsed
        assert len(result.reader_txt) > 100

    def test_narration_extracted(self, parsed):
        result, story_path = parsed
        assert len(result.narration_txt) > 100, (
            f"{story_path.name}: narration_txt should be extracted from Audio Narration block"
        )

    def test_narration_no_ssml(self, parsed):
        result, story_path = parsed
        assert "<break time=" not in result.narration_txt, (
            f"{story_path.name}: narration_txt still contains SSML break tags"
        )
