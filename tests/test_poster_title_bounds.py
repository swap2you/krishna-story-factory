"""Geometry / wrapping guards for poster title bands (D-12)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from krishna_story_factory.images.generator import compose_poster
from krishna_story_factory.publication.fonts import resolve_unicode_fonts
from krishna_story_factory.publication.poster_text import (
    MAX_TITLE_LINES,
    bands_for_art_height,
    fit_title_layout,
    title_block_height,
    wrap_text_lines,
)

STORY_019_TITLE = "Kṛṣṇa Protects the Calves from Vatsāsura and Bakāsura"
LONG_THREE_LINE_TITLE = (
    "Kṛṣṇa Protects the Calves from Vatsāsura and Bakāsura with Loving Care"
)


def test_bands_reserve_room_for_three_title_lines():
    title_band, footer_band = bands_for_art_height(1024, legacy=False)
    assert title_band >= title_block_height(3, 42)
    assert footer_band >= 56
    legacy_title, _ = bands_for_art_height(1024, legacy=True)
    assert title_band > legacy_title


def test_fit_title_layout_allows_two_or_three_lines_without_overflow():
    fonts = resolve_unicode_fonts()
    canvas = Image.new("RGB", (1024, 200), "#120c06")
    draw = ImageDraw.Draw(canvas)
    title_band, _ = bands_for_art_height(1024, legacy=False)
    max_w = 1024 - int(1024 * 0.06) * 2

    for title in (STORY_019_TITLE, LONG_THREE_LINE_TITLE, "Baby Kṛṣṇa Breaks the Cart"):
        lines, font, size = fit_title_layout(
            draw,
            title,
            font_loader=fonts.pillow_bold,
            max_width=max_w,
            band_height=title_band,
        )
        assert 1 <= len(lines) <= MAX_TITLE_LINES
        assert title_block_height(len(lines), size) <= title_band
        assert all(draw.textlength(line, font=font) <= max_w for line in lines)


def test_compose_poster_keeps_title_ink_inside_title_band(tmp_path: Path):
    art = tmp_path / "art.png"
    Image.new("RGB", (1024, 1024), "#334455").save(art)
    out = tmp_path / "poster.png"
    compose_poster(art, out, STORY_019_TITLE, "Remember the Lord with a soft and grateful heart.")

    with Image.open(out) as img:
        rgb = img.convert("RGB")
        title_band, footer_band = bands_for_art_height(1024, legacy=False)
        assert rgb.size == (1024, 1024 + title_band + footer_band)
        title_region = rgb.crop((0, 0, 1024, title_band))
        # Ink must exist inside the band and must not spill into the first art rows.
        ink = [
            (x, y)
            for y in range(title_region.height)
            for x in range(0, title_region.width, 8)
            if title_region.getpixel((x, y)) != (0x12, 0x0C, 0x06)
        ]
        assert ink, "expected title ink inside the title band"
        assert max(y for _, y in ink) < title_band - 2
        assert min(y for _, y in ink) >= 2

        art_top = rgb.crop((0, title_band, 1024, title_band + 8))
        # Artwork row should remain the solid art colour (no title glyphs).
        assert all(art_top.getpixel((x, 0)) == (0x33, 0x44, 0x55) for x in range(0, 1024, 16))


def test_wrap_text_is_deterministic():
    fonts = resolve_unicode_fonts()
    font = fonts.pillow_bold(42)
    canvas = Image.new("RGB", (64, 64), "#000000")
    draw = ImageDraw.Draw(canvas)
    a = wrap_text_lines(draw, STORY_019_TITLE, font, 900)
    b = wrap_text_lines(draw, STORY_019_TITLE, font, 900)
    assert a == b
    assert 2 <= len(a) <= 3
