"""Regression guard for the complete poster text surface, not only the credit strip.

The 2.1.1 defect was invisible to credit-strip-only checks: the title and caption
bands are drawn by a different compositor, which fell through to Pillow's default
bitmap font and burned missing-glyph boxes into released posters. These tests
inspect all three text layers of every released poster, at pixel level.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageFont

from krishna_story_factory.publication.fonts import (
    REQUIRED_GLYPH_SAMPLES,
    UnicodeFontError,
    assert_text_renderable,
    missing_glyphs,
    resolve_unicode_fonts,
    validate_font_glyph_coverage,
)
from krishna_story_factory.publication.poster_text import (
    TOFU_CODEPOINTS,
    count_missing_glyph_boxes,
    derive_poster_geometry,
    has_text_bands,
    poster_band_crops,
    validate_poster_text,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
MASTERS = OUTPUT / "_archive" / "pre-copyright"
CHAPTERS = [f"{n:03d}" for n in range(1, 10)]

# Mission-mandated glyph sample for every public text surface.
REQUIRED_POSTER_GLYPHS = (
    "Bhāva",
    "Kṛṣṇa",
    "Pūtanā",
    "Rādhā",
    "Śrīla Prabhupāda",
    "Vaiṣṇava",
    "Śrīmad-Bhāgavatam",
    "Caitanya-caritāmṛta",
    "—",
    "’",
)

# A real TrueType face at the poster's requested sizes produces ink far taller
# than Pillow's default bitmap font (~10px). This is how the 2.1.1 defect stays
# detectable without depending on which Unicode font the platform resolved.
MIN_TITLE_INK_HEIGHT = 24
MIN_CAPTION_INK_HEIGHT = 16
MIN_TITLE_INK_WIDTH_RATIO = 0.25


def _package(chapter: str) -> Path:
    matches = [p for p in sorted(OUTPUT.glob(f"{chapter}_*")) if (p / "manifest.json").is_file()]
    assert len(matches) == 1, f"Expected one package for {chapter}, found {matches}"
    return matches[0]


def _manifest(chapter: str) -> dict:
    return json.loads((_package(chapter) / "manifest.json").read_text(encoding="utf-8"))


def _poster(chapter: str) -> Path:
    return _package(chapter) / "story_poster.png"


def _master(chapter: str) -> Path:
    return MASTERS / chapter / "2.0" / "story_poster.png"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _poster_note(chapter: str) -> dict:
    publication = _manifest(chapter).get("publication") or {}
    images = (publication.get("artifact_notes") or {}).get("images") or {}
    return images.get("story_poster.png") or {}


#: Posters that actually carry title/caption bands. Stories 004 and 005 are bare
#: artwork plus a credit strip, so they have no title or caption text to inspect.
#: Declared as constants so collection never depends on provisioned content;
#: test_band_and_corrected_chapters_are_discovered checks them against reality.
BAND_CHAPTERS = ["001", "002", "003", "006", "007", "008", "009"]

#: Posters whose recorded title or caption contains non-ASCII characters. These get
#: the strict typeface and box-glyph gates.
CORRECTED_CHAPTERS = ["007", "009"]

#: Unicode-font poster correction that left coloring/audio/PDF unchanged.
#: Story 009 later received an intentional v3 visual (poster+coloring) repair.
SUPERSESSION_STABLE_CHAPTERS = ["007"]


def _discover_band_chapters() -> list[str]:
    return [chapter for chapter in CHAPTERS if has_text_bands(_poster(chapter))]


def _discover_corrected_chapters() -> list[str]:
    return [
        chapter
        for chapter in _discover_band_chapters()
        if any(
            ord(char) > 127
            for text in (
                str(_poster_note(chapter).get("title_text") or ""),
                str(_poster_note(chapter).get("caption_text") or ""),
            )
            for char in text
        )
    ]


def _ink_bbox(band: Image.Image) -> tuple[int, int, int, int] | None:
    """Bounding box of drawn text within a flat-background band."""
    rgb = band.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((2, 2)))
    diff = ImageChops.difference(rgb, background).convert("L")
    return diff.point(lambda p: 255 if p > 28 else 0).getbbox()


# --------------------------------------------------------------------------
# Resolver-level guarantees
# --------------------------------------------------------------------------


def test_resolver_covers_required_poster_glyphs() -> None:
    fonts = resolve_unicode_fonts()
    for path in (fonts.regular_path, fonts.bold_path):
        assert validate_font_glyph_coverage(path, REQUIRED_POSTER_GLYPHS) == [], path


def test_required_glyph_samples_include_em_dash_and_apostrophe() -> None:
    assert "—" in REQUIRED_GLYPH_SAMPLES
    assert "’" in REQUIRED_GLYPH_SAMPLES


def test_default_bitmap_font_is_detected_as_unrenderable() -> None:
    """The exact failure mode behind the poster defect must be caught.

    A ``.notdef`` box has positive advance width, so width-only checks pass it.
    """
    default = ImageFont.load_default()
    assert missing_glyphs(default, "Pūtanā — Kṛṣṇa’s Astonishing Mercy")
    assert missing_glyphs(default, "Yoga-māyā warns Kaṁsa")
    assert missing_glyphs(default, "Plain ASCII text") == []
    with pytest.raises(UnicodeFontError):
        assert_text_renderable(default, ["Pūtanā — Kṛṣṇa’s Astonishing Mercy"], context="test")


def test_replacement_character_is_rejected() -> None:
    fonts = resolve_unicode_fonts()
    with pytest.raises(UnicodeFontError):
        assert_text_renderable(fonts.pillow_regular(24), ["K\ufffd\ufffda"], context="test")


def test_poster_compositor_never_uses_default_font() -> None:
    from krishna_story_factory.images.generator import _font

    fonts = resolve_unicode_fonts()
    assert Path(_font(42, bold=True).path) == fonts.bold_path
    assert Path(_font(24, bold=False).path) == fonts.regular_path


def test_alternate_compositors_never_use_default_font() -> None:
    from krishna_story_factory.visuals.line_art_compositor import _load_fonts as line_fonts
    from krishna_story_factory.visuals.poster_compositor import _load_fonts as poster_fonts

    fonts = resolve_unicode_fonts()
    allowed = {fonts.regular_path, fonts.bold_path}
    for font in list(poster_fonts()) + list(line_fonts()):
        assert Path(font.path) in allowed, font


# --------------------------------------------------------------------------
# All released posters
# --------------------------------------------------------------------------


@pytest.mark.content_release
def test_band_and_corrected_chapters_are_discovered() -> None:
    assert BAND_CHAPTERS == ["001", "002", "003", "006", "007", "008", "009"], BAND_CHAPTERS
    assert CORRECTED_CHAPTERS == ["007", "009"], CORRECTED_CHAPTERS


@pytest.mark.local_archive
@pytest.mark.parametrize("chapter", CHAPTERS)
def test_poster_has_exactly_one_credit_strip(chapter: str) -> None:
    with Image.open(_master(chapter)) as master, Image.open(_poster(chapter)) as live:
        strip = live.size[1] - master.size[1]
        assert live.size[0] == master.size[0], chapter
        recorded = _poster_note(chapter).get("strip_height_px")
        if recorded:
            assert strip == recorded, (
                f"{chapter}: poster is {strip}px taller than its master but the manifest "
                f"records a {recorded}px strip, implying a stacked second strip"
            )


@pytest.mark.local_archive
@pytest.mark.parametrize("chapter", CHAPTERS)
def test_credit_strip_does_not_obstruct_sacred_artwork(chapter: str) -> None:
    """Artwork pixels must be byte-identical to the clean 2.0 master.

    Text bands are compared separately; only the artwork region is asserted here
    so a legitimate title/caption re-render does not look like artwork tampering.
    """
    with Image.open(_master(chapter)) as master:
        master_rgb = master.convert("RGB")
        if chapter in BAND_CHAPTERS:
            box = derive_poster_geometry(master_rgb.size).art_box
        else:
            box = (0, 0, master_rgb.width, master_rgb.height)
        master_art = master_rgb.crop(box).tobytes()
    with Image.open(_poster(chapter)) as live:
        live_art = live.convert("RGB").crop(box).tobytes()
    assert live_art == master_art, f"{chapter}: artwork region was altered"


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", BAND_CHAPTERS)
def test_poster_text_bands_contain_no_missing_glyph_boxes(chapter: str, tmp_path: Path) -> None:
    """Pixel-level tofu scan of the title, caption and credit bands.

    The box template must come from the font that drew the text, so scan against
    both the validated Unicode font and the default font that caused the defect.
    """
    fonts = resolve_unicode_fonts()
    crops = poster_band_crops(_poster(chapter))
    templates = {
        "unicode-regular": fonts.pillow_regular(24),
        "unicode-bold": fonts.pillow_bold(42),
        "pillow-default": ImageFont.load_default(),
    }
    for band in ("title", "caption", "credit"):
        crops[band].save(tmp_path / f"{chapter}-{band}.png")
        for label, font in templates.items():
            boxes = count_missing_glyph_boxes(crops[band], font)
            assert boxes == 0, (
                f"{chapter}: {boxes} missing-glyph box(es) in the {band} band "
                f"(detected with the {label} box template)"
            )


# --------------------------------------------------------------------------
# Posters whose title or caption contains non-ASCII characters
# --------------------------------------------------------------------------


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_unicode_poster_text_glyphs_are_covered(chapter: str) -> None:
    note = _poster_note(chapter)
    report = validate_poster_text(
        str(note["title_text"]), str(note["caption_text"]), str(note["credit_line"])
    )
    assert report["ok"], report
    for layer in ("title_band", "caption_band", "credit_strip"):
        assert report[layer]["missing_glyphs"] == [], (chapter, layer, report[layer])
        assert report[layer]["contains_tofu_codepoint"] == [], (chapter, layer)


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_unicode_poster_text_has_no_replacement_or_box_characters(chapter: str) -> None:
    note = _poster_note(chapter)
    for key in ("title_text", "caption_text", "credit_line"):
        text = str(note[key])
        for bad in TOFU_CODEPOINTS:
            assert bad not in text, f"{chapter}: {bad!r} in {key}"


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_unicode_poster_title_band_uses_a_real_typeface(chapter: str, tmp_path: Path) -> None:
    crops = poster_band_crops(_poster(chapter))
    crops["title"].save(tmp_path / f"{chapter}-title.png")
    bbox = _ink_bbox(crops["title"])
    assert bbox is not None, f"{chapter}: title band has no text"
    height, width = bbox[3] - bbox[1], bbox[2] - bbox[0]
    assert height >= MIN_TITLE_INK_HEIGHT, (
        f"{chapter}: title ink height {height}px indicates the default bitmap font"
    )
    assert width / crops["full"].width >= MIN_TITLE_INK_WIDTH_RATIO, (
        f"{chapter}: title ink width ratio {width / crops['full'].width:.3f} too small"
    )


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_unicode_poster_caption_band_uses_a_real_typeface(chapter: str, tmp_path: Path) -> None:
    crops = poster_band_crops(_poster(chapter))
    crops["caption"].save(tmp_path / f"{chapter}-caption.png")
    bbox = _ink_bbox(crops["caption"])
    assert bbox is not None, f"{chapter}: caption band has no text"
    height = bbox[3] - bbox[1]
    assert height >= MIN_CAPTION_INK_HEIGHT, (
        f"{chapter}: caption ink height {height}px indicates the default bitmap font"
    )


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_unicode_poster_text_is_not_transliterated(chapter: str) -> None:
    note = _poster_note(chapter)
    for key in ("title_text", "caption_text"):
        text = str(note[key])
        if not any(ord(ch) > 127 for ch in text):
            continue
        folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        assert text != folded, f"{chapter}: {key} was ASCII-transliterated"


@pytest.mark.content_release
def test_story_009_poster_shows_the_expected_devanagari_transliteration() -> None:
    note = _poster_note("009")
    assert "Pūtanā" in note["title_text"]
    assert "Kṛṣṇa" in note["title_text"]
    assert "—" in note["title_text"]
    assert "Kṛṣṇa" in note["caption_text"]
    assert "Bhāva" in note["credit_line"]


@pytest.mark.content_release
def test_story_007_poster_caption_keeps_its_diacritics() -> None:
    note = _poster_note("007")
    assert "Yoga-māyā" in note["caption_text"]
    assert "Kaṁsa" in note["caption_text"]


@pytest.mark.local_archive
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_superseded_poster_with_box_glyphs_is_rejected(chapter: str, tmp_path: Path) -> None:
    """The archived pre-correction poster must fail the same gates."""
    prior = str((_manifest(chapter).get("publication") or {}).get("supersedes") or "")
    archived = MASTERS / chapter / prior / "story_poster.png"
    assert archived.is_file(), f"Missing archived predecessor poster {archived}"

    default = ImageFont.load_default()
    crops = poster_band_crops(archived)
    crops["title"].save(tmp_path / f"{chapter}-old-title.png")
    crops["caption"].save(tmp_path / f"{chapter}-old-caption.png")

    old_boxes = count_missing_glyph_boxes(crops["title"], default) + count_missing_glyph_boxes(
        crops["caption"], default
    )
    old_title_ink = _ink_bbox(crops["title"])
    old_title_height = (old_title_ink[3] - old_title_ink[1]) if old_title_ink else 0

    assert old_boxes > 0 or old_title_height < MIN_TITLE_INK_HEIGHT, (
        f"{chapter}: archived {prior} poster passes the poster-text gates, so this "
        "regression no longer discriminates the defect it was written for"
    )
    assert _sha(archived) != _sha(_poster(chapter))


@pytest.mark.local_archive
def test_old_story_009_poster_specifically_fails() -> None:
    """Named guard for CLOSEOUT-B1's exact artefact."""
    archived = MASTERS / "009" / "2.1.1-copyright" / "story_poster.png"
    assert archived.is_file(), archived
    crops = poster_band_crops(archived)
    title_ink = _ink_bbox(crops["title"])
    assert title_ink is not None
    assert (title_ink[3] - title_ink[1]) < MIN_TITLE_INK_HEIGHT, (
        "The superseded Story 009 poster must not pass the typeface gate"
    )
    default = ImageFont.load_default()
    boxes = count_missing_glyph_boxes(crops["title"], default)
    assert boxes >= 4, (
        f"Expected box glyphs in the superseded Story 009 title band, found {boxes}"
    )


@pytest.mark.local_archive
def test_old_story_007_poster_caption_specifically_fails() -> None:
    """Named guard for the second instance found during this correction pass."""
    archived = MASTERS / "007" / "2.1.1-copyright" / "story_poster.png"
    assert archived.is_file(), archived
    crops = poster_band_crops(archived)
    boxes = count_missing_glyph_boxes(crops["caption"], ImageFont.load_default())
    assert boxes >= 3, (
        f"Expected the superseded Story 007 caption to show missing-glyph boxes, found {boxes}"
    )


# --------------------------------------------------------------------------
# Bookkeeping for the correction
# --------------------------------------------------------------------------


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_manifest_records_poster_text_rebuild(chapter: str) -> None:
    publication = _manifest(chapter).get("publication") or {}
    validation = publication.get("poster_text_glyph_validation") or {}
    assert validation.get("ok") is True, (chapter, validation)
    note = _poster_note(chapter)
    assert note.get("text_layers_rebuilt") == ["title_band", "caption_band", "credit_strip"], note
    assert note.get("artwork_pixels_redrawn") is False, note
    assert note.get("sacred_subject_overlay") is False, note
    assert note.get("missing_glyph_boxes") == {"title": 0, "caption": 0, "credit": 0}, note
    preserved = note.get("wording_preserved_vs_previous_version") or {}
    assert preserved.get("title_preserved") is True, note
    assert preserved.get("caption_preserved") is True, note


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_correction_history_records_poster_fix(chapter: str) -> None:
    history = (_manifest(chapter).get("rights") or {}).get("correction_history") or []
    changes = [entry.get("change") for entry in history]
    assert "poster_title_and_caption_unicode_font" in changes, changes
    assert "unicode_font_and_per_page_pdf_footer" in changes, (
        f"{chapter}: earlier correction history was dropped"
    )


@pytest.mark.local_archive
@pytest.mark.parametrize("chapter", CORRECTED_CHAPTERS)
def test_superseded_archive_is_intact_and_correctly_labelled(chapter: str) -> None:
    manifest = _manifest(chapter)
    prior = str((manifest.get("publication") or {}).get("supersedes") or "")
    archive = MASTERS / chapter / prior
    assert archive.is_dir(), f"Missing predecessor archive {archive}"
    archived_manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    assert str(archived_manifest.get("version")) == prior, (
        f"Archive {archive} is labelled {archived_manifest.get('version')} "
        f"but should hold {prior}"
    )
    prior_hashes = (manifest.get("rights") or {}).get("prior_version_sha256") or {}
    assert prior_hashes, f"{chapter}: no supersession hashes recorded"
    for name, expected in prior_hashes.items():
        path = archive / name
        assert path.is_file(), path
        assert _sha(path) == expected.lower(), f"Supersession hash drift {chapter}/{name}"


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", SUPERSESSION_STABLE_CHAPTERS)
def test_narration_and_narrative_survive_the_correction(chapter: str) -> None:
    rights = _manifest(chapter).get("rights") or {}
    current = rights.get("sha256") or {}
    prior = rights.get("prior_version_sha256") or {}
    assert current.get("narration.mp3") == prior.get("narration.mp3"), (
        f"{chapter}: narration.mp3 changed across the poster correction"
    )
    for name in (
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
    ):
        assert current.get(name) == prior.get(name), f"{chapter}: {name} changed unexpectedly"


@pytest.mark.content_release
@pytest.mark.parametrize("chapter", SUPERSESSION_STABLE_CHAPTERS)
def test_only_poster_story_and_manifest_changed(chapter: str) -> None:
    rights = _manifest(chapter).get("rights") or {}
    current = rights.get("sha256") or {}
    prior = rights.get("prior_version_sha256") or {}
    changed = {name for name in current if current[name] != prior.get(name)}
    assert changed == {"story_poster.png", "story.md", "manifest.json"}, changed


@pytest.mark.local_archive
def test_swap_backup_records_its_true_version() -> None:
    """A swap backup must be labelled with the version it actually contains."""
    backups = OUTPUT / "_archive" / "copyright-swap-backups"
    sidecars = sorted(backups.glob("*_PREVIOUS_VERSION.json"))
    if not sidecars:
        pytest.skip("No labelled swap backups present")
    for sidecar in sidecars:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        backup_dir = backups / payload["backup_dir"]
        assert backup_dir.is_dir(), backup_dir
        manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))
        assert str(manifest.get("version")) == payload["backed_up_version"], (
            f"{sidecar.name}: label {payload['backed_up_version']} does not match "
            f"backup content {manifest.get('version')}"
        )


@pytest.mark.content_release
def test_text_less_posters_are_not_misdecomposed() -> None:
    """Stories 004 and 005 are bare artwork; band geometry must not be inferred."""
    for chapter in ("004", "005"):
        assert not has_text_bands(_poster(chapter)), chapter


@pytest.mark.content_release
def test_already_credited_poster_is_not_accepted_as_a_master() -> None:
    """Guard against stacking a second credit strip by passing a live poster."""
    with Image.open(_poster("009")) as live:
        with pytest.raises(ValueError):
            derive_poster_geometry(live.size)
