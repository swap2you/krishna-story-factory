"""Verify the story parser strips ALL internal production material from reader output.

For each story 001–007, reads the raw story.md from output/ and asserts the
parsed reader content excludes Audio Narration, Poster/Coloring Visual Briefs,
Activity Data, and SSML break tags — while still containing Main Story content.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "output"

STORY_DIRS = sorted(
    p
    for p in OUTPUT_ROOT.iterdir()
    if p.is_dir() and not p.name.startswith("_") and (p / "story.md").is_file()
)

LEAK_MARKERS = [
    "Audio Narration",
    "Poster Visual Brief",
    "Coloring Visual Brief",
    "Activity Data",
    "<break time=",
    "&lt;break",
]

from bhava_api.web_assets.story_parser import parse_story_markdown  # noqa: E402


def _story_no(d: Path) -> str:
    m = re.match(r"^(\d{3})_", d.name)
    return m.group(1) if m else d.name[:3]


@pytest.fixture(params=STORY_DIRS, ids=[d.name for d in STORY_DIRS])
def parsed(request: pytest.FixtureRequest):
    story_dir: Path = request.param
    raw = (story_dir / "story.md").read_text(encoding="utf-8")
    return parse_story_markdown(raw), story_dir


class TestReaderLeakPrevention:
    """Each story must produce clean reader output free of internal blocks."""

    def test_no_internal_leak_markers_flag(self, parsed):
        result, story_dir = parsed
        assert not result.has_internal_leak_markers, (
            f"{story_dir.name}: reader still has leak markers"
        )

    @pytest.mark.parametrize("marker", LEAK_MARKERS, ids=LEAK_MARKERS)
    def test_reader_md_excludes_marker(self, parsed, marker):
        result, story_dir = parsed
        assert marker not in result.reader_md, (
            f"{story_dir.name}: reader_md contains '{marker}'"
        )

    @pytest.mark.parametrize("marker", LEAK_MARKERS, ids=LEAK_MARKERS)
    def test_reader_txt_excludes_marker(self, parsed, marker):
        result, story_dir = parsed
        assert marker not in result.reader_txt, (
            f"{story_dir.name}: reader_txt contains '{marker}'"
        )

    def test_no_html_comments(self, parsed):
        result, _ = parsed
        assert "<!--" not in result.reader_md
        assert "-->" not in result.reader_md

    def test_main_story_present(self, parsed):
        result, story_dir = parsed
        assert "Main Story" in result.reader_md or len(result.reader_md) > 500, (
            f"{story_dir.name}: Main Story content missing from reader"
        )

    def test_reader_txt_not_empty(self, parsed):
        result, _ = parsed
        assert len(result.reader_txt) > 200

    def test_narration_extracted(self, parsed):
        result, story_dir = parsed
        assert len(result.narration_txt) > 100, (
            f"{story_dir.name}: narration_txt should be extracted from Audio Narration block"
        )

    def test_narration_no_ssml(self, parsed):
        result, story_dir = parsed
        assert "<break time=" not in result.narration_txt, (
            f"{story_dir.name}: narration_txt still contains SSML break tags"
        )
