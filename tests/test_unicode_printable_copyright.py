"""Unicode font, PDF footer, and printable copyright regressions."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
)
GLYPHS = ("Bhāva", "Kṛṣṇa", "Pūtanā", "Rādhā", "Śrīmad-Bhāgavatam", "Śrīla Prabhupāda")


def _story_dir(n: int) -> Path:
    return next((ROOT / "output").glob(f"{n:03d}_*"))


def test_unicode_font_resolver_supports_required_glyphs() -> None:
    from krishna_story_factory.publication.fonts import (
        resolve_unicode_fonts,
        validate_font_glyph_coverage,
    )

    resolve_unicode_fonts.cache_clear()
    fonts = resolve_unicode_fonts()
    assert fonts.regular_path.is_file()
    assert validate_font_glyph_coverage(fonts.regular_path) == []


def test_pdf_rights_page_preserves_bhava_and_footer_every_page() -> None:
    from krishna_story_factory.publication.artifacts import stamp_pdf_footer
    from krishna_story_factory.publication.identity import load_identity

    identity = load_identity(ROOT)
    master = ROOT / "output" / "_archive" / "pre-copyright" / "001" / "2.0" / "activity_sheet.pdf"
    assert master.is_file()
    dest = ROOT / "output" / "_staging" / "unicode-test" / "001_activity.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    note = stamp_pdf_footer(master, dest, year=None, identity=identity)
    reader = PdfReader(str(dest))
    assert len(reader.pages) == note["activity_pages"] + note["rights_pages_added"]
    # Every activity page should extract the compact footer owner/publisher tokens.
    for idx in range(note["activity_pages"]):
        text = reader.pages[idx].extract_text() or ""
        assert "Svarna Gauranga Das" in text
        assert "Dauji Publication" in text
    rights_text = "\n".join((reader.pages[i].extract_text() or "") for i in range(note["activity_pages"], len(reader.pages)))
    assert "Bhāva" in rights_text
    assert "Bhava" not in rights_text.replace("Bhāva", "")
    assert "A Bhāva Project publication" in rights_text
    assert "Helvetica" not in str(note.get("reportlab_font"))


def test_public_packages_version_and_exact_eight() -> None:
    from krishna_story_factory.package_swap import validate_exact_eight_files

    baseline = json.loads(
        (ROOT / "docs" / "releases" / "BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json").read_text(
            encoding="utf-8"
        )
    )
    for n in range(1, 10):
        folder = _story_dir(n)
        assert validate_exact_eight_files(folder) == []
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        # The launch safety baseline is the source of truth for released versions;
        # artifact corrections advance individual stories past 2.1.1-copyright.
        assert manifest.get("version") == baseline["stories"][f"{n:03d}"]["version"]
        assert (ROOT / "output" / "_archive" / "pre-copyright" / f"{n:03d}" / "2.1.0-copyright").is_dir()
        assert (ROOT / "output" / "_archive" / "pre-copyright" / f"{n:03d}" / "2.0").is_dir()


def test_narrative_unchanged_before_rights() -> None:
    for n in range(1, 10):
        public = (_story_dir(n) / "story.md").read_text(encoding="utf-8")
        master = (
            ROOT / "output" / "_archive" / "pre-copyright" / f"{n:03d}" / "2.0" / "story.md"
        ).read_text(encoding="utf-8")
        pub_idx = public.find("## Rights and Credits")
        mas_idx = master.find("<!--")
        if mas_idx < 0:
            mas_idx = len(master)
        assert public[:pub_idx].rstrip() == master[:mas_idx].rstrip()


def test_image_credit_strip_unicode_and_no_duplicate() -> None:
    from krishna_story_factory.publication.artifacts import append_image_credit_strip
    from krishna_story_factory.publication.fonts import resolve_unicode_fonts
    from krishna_story_factory.publication.identity import load_identity

    identity = load_identity(ROOT)
    fonts = resolve_unicode_fonts()
    master = ROOT / "output" / "_archive" / "pre-copyright" / "009" / "2.0" / "story_poster.png"
    dest = ROOT / "output" / "_staging" / "unicode-test" / "009_poster.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    note = append_image_credit_strip(master, dest, year=None, ai_image=True, identity=identity)
    assert note["sacred_subject_overlay"] is False
    with Image.open(master) as src, Image.open(dest) as out:
        assert out.size[1] > src.size[1]
        assert out.size[0] == src.size[0]
        # One strip only: height delta roughly one strip.
        assert abs((out.size[1] - src.size[1]) - note["strip_height_px"]) <= 1
    # Glyph smoke: render required tokens with the same font used for exports.
    img = Image.new("RGB", (900, 80), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 20), " · ".join(GLYPHS), fill="black", font=fonts.pillow_regular(18))
    # No pure-black tofu blocks expected for these glyphs when font covers them.
    # Soft check: bounding boxes for each sample have positive width.
    font = fonts.pillow_regular(24)
    for sample in GLYPHS:
        bbox = font.getbbox(sample)
        assert bbox and (bbox[2] - bbox[0]) > 0


def test_story_010_absent_and_queue_pending() -> None:
    assert not list((ROOT / "output").glob("010_*"))
    queue = ROOT / "tracking" / "queue_state.csv"
    if not queue.is_file():
        pytest.skip("queue_state.csv absent")
    rows = {str(r["chapter_no"]).zfill(3): r["status"] for r in csv.DictReader(queue.open(encoding="utf-8"))}
    assert rows.get("009") == "done"
    assert rows.get("010") == "pending"


def test_public_pdf_has_footer_on_all_activity_pages() -> None:
    for n in (1, 9):
        pdf = _story_dir(n) / "activity_sheet.pdf"
        reader = PdfReader(str(pdf))
        assert len(reader.pages) >= 2
        # Last page is rights; earlier pages are activity.
        for page in reader.pages[:-1]:
            text = page.extract_text() or ""
            assert "Svarna Gauranga Das" in text
            assert "Dauji Publication" in text
        rights = reader.pages[-1].extract_text() or ""
        assert "Bhāva" in rights
        assert "Rights and Credits" in rights
