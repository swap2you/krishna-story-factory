"""Recover poster artwork and recompose poster text with validated Unicode fonts.

The title and caption bands are burned into ``story_poster.png`` at generation
time, so a credit-strip-only retrofit cannot repair diacritics that were drawn
with a font lacking the glyphs. This module inverts the known band geometry of
``images.generator.compose_poster`` to recover the untouched artwork, then
re-runs the production compositor. Artwork pixels are never redrawn.
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from .artifacts import append_image_credit_strip
from .fonts import missing_glyphs, resolve_unicode_fonts
from .identity import PublicationIdentity

# Unicode replacement character and the codepoints commonly substituted for a
# missing glyph by viewers. Any of these in public poster text is a defect.
TOFU_CODEPOINTS = ("\ufffd", "\u25a1", "\u25a0", "\u2b1b", "\u2b1c")

#: Title layout — keep in lockstep with ``images.generator.compose_poster``.
MAX_TITLE_LINES = 3
MAX_CAPTION_LINES = 2
BASE_TITLE_SIZE = 42
MIN_TITLE_SIZE = 26
TITLE_LINE_GAP = 4
TITLE_PAD_Y = 14
BASE_CAPTION_SIZE = 24


@dataclass(frozen=True)
class PosterGeometry:
    """Band layout of a composed (pre-credit-strip) poster."""

    width: int
    height: int
    art_height: int
    title_band: int
    footer_band: int

    @property
    def art_box(self) -> tuple[int, int, int, int]:
        return (0, self.title_band, self.width, self.title_band + self.art_height)

    @property
    def title_box(self) -> tuple[int, int, int, int]:
        return (0, 0, self.width, self.title_band)

    @property
    def caption_box(self) -> tuple[int, int, int, int]:
        top = self.title_band + self.art_height
        return (0, top, self.width, top + self.footer_band)


def bands_for_art_height(art_height: int, *, legacy: bool = False) -> tuple[int, int]:
    """Mirror of ``compose_poster`` band sizing. Keep in lockstep with it.

    ``legacy=True`` recovers pre-D-12 posters (hard-capped 2-line / ~8% title band).
    Current layout reserves a taller title band for safe 2–3 line titles.
    """
    if legacy:
        return max(int(art_height * 0.08), 72), max(int(art_height * 0.06), 56)
    # 168px fits three 42px title lines with TITLE_PAD_Y / TITLE_LINE_GAP safely.
    return max(int(art_height * 0.14), 168), max(int(art_height * 0.06), 56)


# Back-compat alias used by older call sites / tests.
def _bands_for_art_height(art_height: int) -> tuple[int, int]:
    return bands_for_art_height(art_height, legacy=False)


#: Flat backdrop colour that compose_poster paints behind the title/caption bands.
BAND_BACKDROP = (0x12, 0x0C, 0x06)
#: Cream credit-strip fill from ``append_image_credit_strip``.
CREDIT_STRIP_BACKDROP = (0xF7, 0xF1, 0xE6)


def wrap_text_lines(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int
) -> list[str]:
    """Deterministic word-wrap used by poster title/caption compositing."""
    if not text.strip():
        return []
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def title_block_height(line_count: int, font_size: int) -> int:
    if line_count <= 0:
        return 0
    return TITLE_PAD_Y * 2 + line_count * font_size + max(0, line_count - 1) * TITLE_LINE_GAP


def fit_title_layout(
    draw: ImageDraw.ImageDraw,
    title: str,
    *,
    font_loader: Callable[[int], ImageFont.FreeTypeFont],
    max_width: int,
    band_height: int,
) -> tuple[list[str], ImageFont.FreeTypeFont, int]:
    """Choose font size and ≤3 wrap lines that fit entirely inside ``band_height``."""
    for size in range(BASE_TITLE_SIZE, MIN_TITLE_SIZE - 1, -2):
        font = font_loader(size)
        lines = wrap_text_lines(draw, title, font, max_width)
        if not lines:
            return [], font, size
        if len(lines) > MAX_TITLE_LINES:
            continue
        if title_block_height(len(lines), size) <= band_height:
            return lines, font, size
    font = font_loader(MIN_TITLE_SIZE)
    lines = wrap_text_lines(draw, title, font, max_width)[:MAX_TITLE_LINES]
    return lines, font, MIN_TITLE_SIZE


def _geometry_for_formula(size: tuple[int, int], *, legacy: bool) -> PosterGeometry | None:
    width, height = size
    solutions = [
        art_height
        for art_height in range(1, height)
        if art_height + sum(bands_for_art_height(art_height, legacy=legacy)) == height
    ]
    if len(solutions) != 1:
        return None
    art_height = solutions[0]
    title_band, footer_band = bands_for_art_height(art_height, legacy=legacy)
    return PosterGeometry(
        width=width,
        height=height,
        art_height=art_height,
        title_band=title_band,
        footer_band=footer_band,
    )


def _band_corners_match(rgb: Image.Image, geometry: PosterGeometry) -> bool:
    probes = [
        (2, 2),
        (rgb.width - 3, 2),
        (2, geometry.title_band - 2),
        (2, geometry.title_band + geometry.art_height + 2),
    ]
    return all(
        0 <= x < rgb.width and 0 <= y < rgb.height and _near(rgb.getpixel((x, y)), BAND_BACKDROP)
        for x, y in probes
    )


def derive_poster_geometry(
    size: tuple[int, int], *, rgb: Image.Image | None = None
) -> PosterGeometry:
    """Invert the composed-poster band geometry, or fail when ambiguous.

    Supports both legacy (pre-D-12) and current taller title-band formulas.
    When both uniquely solve the height equation, ``rgb`` band-corner probes
    disambiguate; otherwise prefer the current formula.
    """
    candidates = [
        geo
        for legacy in (False, True)
        if (geo := _geometry_for_formula(size, legacy=legacy)) is not None
    ]
    if not candidates:
        raise ValueError(f"Cannot recover poster artwork region for size {size}")
    if len(candidates) == 1:
        return candidates[0]
    if rgb is not None:
        validated = [geo for geo in candidates if _band_corners_match(rgb, geo)]
        if len(validated) == 1:
            return validated[0]
        if validated:
            # Prefer the larger title band when both still validate.
            return max(validated, key=lambda g: g.title_band)
    raise ValueError(
        f"Ambiguous poster geometry for size {size} without image disambiguation "
        f"(candidates title_bands={[g.title_band for g in candidates]})"
    )


def composed_size(poster_path: Path) -> tuple[int, int]:
    """Size of a finished poster with its credit strip removed."""
    with Image.open(poster_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        strip_h = _infer_strip_height((width, height), rgb=rgb)
    return (width, height - strip_h)


def has_text_bands(poster_path: Path) -> bool:
    """True when a poster actually carries title/caption bands.

    Some posters are bare artwork plus a credit strip. Size arithmetic alone can
    produce a spurious decomposition for those, so confirm the band corners hold
    the flat backdrop colour that compose_poster paints.
    """
    with Image.open(poster_path) as img:
        rgb = img.convert("RGB")
        try:
            strip_h = _infer_strip_height(rgb.size, rgb=rgb)
            composed = rgb.crop((0, 0, rgb.width, rgb.height - strip_h))
            geometry = derive_poster_geometry(composed.size, rgb=composed)
        except ValueError:
            return False
        return _band_corners_match(composed, geometry)


def _near(pixel: tuple[int, ...], target: tuple[int, int, int], tolerance: int = 12) -> bool:
    return all(abs(int(a) - int(b)) <= tolerance for a, b in zip(pixel[:3], target))


_TITLE_INK = (0xF6, 0xE7, 0xB8)


def _spill_ink_present(art: Image.Image, *, spill_rows: int, tolerance: int = 40) -> bool:
    rows = min(spill_rows, art.height)
    for y in range(rows):
        for x in range(0, art.width, 3):
            if _near(art.getpixel((x, y)), _TITLE_INK, tolerance=tolerance):
                return True
    return False


def scrub_title_spill(art: Image.Image, *, spill_rows: int = 48) -> Image.Image:
    """Remove burned-in title overflow from the top of recovered artwork.

    Pre-D-12 two-line titles often painted into the art region when the title
    band was too short. Replace near-exact title-ink pixels in the spill zone
    with samples from the first clean row beneath it.
    """
    if spill_rows <= 0 or art.height <= spill_rows + 2:
        return art
    if not _spill_ink_present(art, spill_rows=spill_rows):
        return art
    cleaned = art.copy()
    pixels = cleaned.load()
    source_y = min(art.height - 1, spill_rows + 12)
    for y in range(spill_rows):
        for x in range(art.width):
            if _near(pixels[x, y], _TITLE_INK, tolerance=40):
                pixels[x, y] = cleaned.getpixel((x, source_y))
    return cleaned


def extract_poster_art(master_path: Path, dest_path: Path) -> PosterGeometry:
    """Write the untouched artwork region of a composed poster to ``dest_path``."""
    with Image.open(master_path) as img:
        rgb = img.convert("RGB")
        geometry = derive_poster_geometry(rgb.size, rgb=rgb)
        art = scrub_title_spill(rgb.crop(geometry.art_box), spill_rows=48)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        art.save(dest_path, "PNG")
    return geometry


def rebuild_poster_from_master(
    master_path: Path,
    dest_path: Path,
    *,
    title: str,
    caption: str,
    year: int | None,
    ai_image: bool,
    identity: PublicationIdentity,
) -> dict:
    """Recompose title/caption from clean artwork, then append the credit strip.

    ``master_path`` must be a pre-credit-strip master (``2.0``); passing an
    already-credited poster would stack a second strip.
    """
    from ..images.generator import compose_poster

    fonts = resolve_unicode_fonts()
    with tempfile.TemporaryDirectory(prefix="bhava-poster-") as tmp:
        tmp_dir = Path(tmp)
        art_path = tmp_dir / "art.png"
        geometry = extract_poster_art(master_path, art_path)
        composed = tmp_dir / "composed.png"
        compose_poster(art_path, composed, title, caption)
        strip_note = append_image_credit_strip(
            composed,
            dest_path,
            year=year,
            ai_image=ai_image,
            identity=identity,
        )
    with Image.open(dest_path) as final:
        final_size = final.size
    return {
        "title_text": title,
        "caption_text": caption,
        "title_font": str(fonts.bold_path),
        "caption_font": str(fonts.regular_path),
        "credit_font": strip_note["font"],
        "credit_line": strip_note["credit_line"],
        "strip_height_px": strip_note["strip_height_px"],
        "placement": strip_note["placement"],
        "sacred_subject_overlay": False,
        "artwork_source": str(master_path),
        "artwork_region": list(geometry.art_box),
        "artwork_pixels_redrawn": False,
        "composed_size": list(final_size),
        "text_layers_rebuilt": ["title_band", "caption_band", "credit_strip"],
    }


def rebuild_poster_from_finished(
    poster_path: Path,
    dest_path: Path,
    *,
    title: str,
    caption: str,
    year: int | None,
    ai_image: bool,
    identity: PublicationIdentity,
) -> dict:
    """Recover art from a finished poster and recompose title/caption."""
    from ..images.generator import compose_poster

    fonts = resolve_unicode_fonts()
    with tempfile.TemporaryDirectory(prefix="bhava-poster-fin-") as tmp:
        tmp_dir = Path(tmp)
        with Image.open(poster_path) as img:
            rgb = img.convert("RGB")
            strip_h = _infer_strip_height(rgb.size, rgb=rgb)
            composed_img = rgb.crop((0, 0, rgb.width, rgb.height - strip_h))
            master_path = tmp_dir / "master.png"
            composed_img.save(master_path, "PNG")
        art_path = tmp_dir / "art.png"
        geometry = extract_poster_art(master_path, art_path)
        composed = tmp_dir / "composed.png"
        compose_poster(art_path, composed, title, caption)
        layers = ["title_band", "caption_band"]
        # Always publish with a credit strip. Regenerated artwork may lack one;
        # stacking is avoided because we compose onto recovered art, not onto a
        # finished credited poster.
        strip_note = append_image_credit_strip(
            composed,
            dest_path,
            year=year,
            ai_image=ai_image,
            identity=identity,
        )
        layers.append("credit_strip")
    with Image.open(dest_path) as final:
        final_size = final.size
    return {
        "title_text": title,
        "caption_text": caption,
        "title_font": str(fonts.bold_path),
        "caption_font": str(fonts.regular_path),
        "credit_font": strip_note["font"],
        "credit_line": strip_note["credit_line"],
        "strip_height_px": strip_note["strip_height_px"],
        "placement": strip_note["placement"],
        "sacred_subject_overlay": False,
        "artwork_source": str(poster_path),
        "artwork_region": list(geometry.art_box),
        "artwork_pixels_redrawn": False,
        "composed_size": list(final_size),
        "text_layers_rebuilt": layers,
        "recovery_path": "finished_poster_strip_then_bands",
    }


def validate_poster_text(title: str, caption: str, credit_line: str) -> dict:
    """Confirm the resolved fonts cover every character of all poster text."""
    fonts = resolve_unicode_fonts()
    layers = {
        "title_band": (fonts.pillow_bold(42), title),
        "caption_band": (fonts.pillow_regular(24), caption),
        "credit_strip": (fonts.pillow_regular(20), credit_line),
    }
    report: dict[str, dict] = {}
    for layer, (font, text) in layers.items():
        report[layer] = {
            "text": text,
            "font": str(getattr(font, "path", "")),
            "missing_glyphs": missing_glyphs(font, text),
            "contains_tofu_codepoint": [c for c in TOFU_CODEPOINTS if c in text],
            "non_ascii": [c for c in text if ord(c) > 127],
        }
    report["ok"] = all(
        not entry["missing_glyphs"] and not entry["contains_tofu_codepoint"]
        for key, entry in report.items()
        if key != "ok"
    )
    return report


def poster_band_crops(poster_path: Path, *, strip_height: int | None = None) -> dict[str, Image.Image]:
    """Crop the title, caption and credit bands of a finished poster."""
    with Image.open(poster_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        strip_h = (
            strip_height if strip_height is not None else _infer_strip_height(rgb.size, rgb=rgb)
        )
        composed_height = height - strip_h
        composed = rgb.crop((0, 0, width, composed_height))
        geometry = derive_poster_geometry((width, composed_height), rgb=composed)
        return {
            "title": rgb.crop(geometry.title_box),
            "caption": rgb.crop(
                (
                    geometry.caption_box[0],
                    geometry.caption_box[1],
                    geometry.caption_box[2],
                    geometry.caption_box[3],
                )
            ),
            "credit": rgb.crop((0, composed_height, width, height)),
            "full": rgb.copy(),
        }


def _strip_looks_like_credit(rgb: Image.Image, strip_h: int) -> bool:
    """True when the bottom strip matches the cream credit canvas colour."""
    if strip_h <= 0 or strip_h >= rgb.height:
        return False
    y = rgb.height - max(2, strip_h // 2)
    probes = [(2, y), (rgb.width // 2, y), (rgb.width - 3, y)]
    return all(_near(rgb.getpixel(p), CREDIT_STRIP_BACKDROP, tolerance=20) for p in probes)


def _infer_strip_height(size: tuple[int, int], *, rgb: Image.Image | None = None) -> int:
    """Find the credit-strip height whose remainder is a valid composed poster.

    Returns 0 when the poster has title/caption bands but no cream credit strip
    (common for some 010–020 packages).
    """
    width, height = size
    if rgb is not None and not _strip_looks_like_credit(rgb, max(40, int(height * 0.05))):
        # No cream strip: whole canvas may already be the composed poster.
        try:
            derive_poster_geometry((width, height), rgb=rgb)
            return 0
        except ValueError:
            pass

    matches: list[int] = []
    for candidate in range(40, max(41, int(height * 0.2))):
        composed_h = height - candidate
        if candidate != max(40, int(composed_h * 0.05)):
            continue
        if rgb is not None and not _strip_looks_like_credit(rgb, candidate):
            continue
        composed_rgb = None
        if rgb is not None:
            composed_rgb = rgb.crop((0, 0, width, composed_h))
        try:
            derive_poster_geometry((width, composed_h), rgb=composed_rgb)
        except ValueError:
            continue
        matches.append(candidate)
    if len(matches) == 1:
        return matches[0]
    if rgb is not None:
        validated: list[int] = []
        for candidate in matches:
            composed_h = height - candidate
            composed_rgb = rgb.crop((0, 0, width, composed_h))
            try:
                geo = derive_poster_geometry((width, composed_h), rgb=composed_rgb)
            except ValueError:
                continue
            if _band_corners_match(composed_rgb, geo):
                validated.append(candidate)
        if len(validated) == 1:
            return validated[0]
        if validated:
            return validated[0]
    if matches:
        return matches[0]
    # Last resort: no strip.
    try:
        derive_poster_geometry((width, height), rgb=rgb)
        return 0
    except ValueError as exc:
        raise ValueError(f"Cannot infer credit-strip height for poster size {size}") from exc


def font_of(font: ImageFont.FreeTypeFont) -> str:
    return str(getattr(font, "path", ""))


def legacy_text_bands(
    composed_size: tuple[int, int], title: str, caption: str
) -> dict[str, Image.Image]:
    """Reproduce the pre-correction title/caption bands using Pillow's default font.

    Used to prove that a rebuild preserves the exact wording burned into a
    released poster: if these bands match the old poster byte-for-byte, only the
    font changed, not the words.
    """
    width, _ = composed_size
    # Legacy glyph-fix path used the pre-D-12 band formula and 2-line cap.
    geometry = _geometry_for_formula(composed_size, legacy=True)
    if geometry is None:
        geometry = derive_poster_geometry(composed_size)
    font = ImageFont.load_default()
    max_w = width - int(width * 0.06) * 2

    title_band = Image.new("RGB", (width, geometry.title_band), "#120c06")
    draw = ImageDraw.Draw(title_band)
    y = 16
    for line in wrap_text_lines(draw, title, font, max_w)[:2]:
        draw.text((width // 2, y), line, font=font, fill="#f6e7b8", anchor="ma")
        y += font.size + 4

    caption_band = Image.new("RGB", (width, geometry.footer_band), "#120c06")
    draw = ImageDraw.Draw(caption_band)
    y = 14
    for line in wrap_text_lines(draw, caption, font, max_w)[:MAX_CAPTION_LINES]:
        draw.text((width // 2, y), line, font=font, fill="#efe2c0", anchor="ma")
        y += font.size + 4

    return {"title": title_band, "caption": caption_band}


def verify_legacy_text_preserved(
    old_poster: Path, composed_size: tuple[int, int], title: str, caption: str
) -> dict[str, bool]:
    """Check the given strings reproduce the old poster's text bands exactly."""
    geometry = _geometry_for_formula(composed_size, legacy=True)
    if geometry is None:
        geometry = derive_poster_geometry(composed_size)
    legacy = legacy_text_bands(composed_size, title, caption)
    with Image.open(old_poster) as img:
        rgb = img.convert("RGB")
        actual_title = rgb.crop(geometry.title_box)
        actual_caption = rgb.crop(geometry.caption_box)
    return {
        "title_preserved": legacy["title"].tobytes() == actual_title.tobytes(),
        "caption_preserved": legacy["caption"].tobytes() == actual_caption.tobytes(),
    }


def notdef_tile(font: ImageFont.FreeTypeFont) -> Image.Image | None:
    """Render the font's missing-glyph box as a template for image inspection."""
    canvas = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(canvas).text((6, 6), "\uffff", fill=255, font=font)
    bbox = canvas.getbbox()
    return canvas.crop(bbox) if bbox else None


def count_missing_glyph_boxes(
    band: Image.Image,
    font: ImageFont.FreeTypeFont,
    *,
    threshold: float = 0.90,
) -> int:
    """Count missing-glyph boxes drawn inside a poster text band.

    Text independent: correlates the band's ink against the font's own ``.notdef``
    raster, so it catches tofu without needing to know the intended string.
    """
    import numpy as np

    tile = notdef_tile(font)
    if tile is None:
        return 0
    template = np.asarray(tile, dtype=np.float32) / 255.0
    th, tw = template.shape
    pixels = np.asarray(band.convert("L"), dtype=np.float32)
    if pixels.size == 0 or th >= pixels.shape[0] or tw >= pixels.shape[1]:
        return 0
    span = float(pixels.max() - pixels.min())
    if span <= 0:
        return 0
    pixels = (pixels - pixels.min()) / span
    # Text occupies a small part of the band; scan only around the inked region.
    inked = np.argwhere(pixels > 0.35)
    if inked.size == 0:
        return 0
    y0 = max(0, int(inked[:, 0].min()) - th)
    y1 = min(pixels.shape[0], int(inked[:, 0].max()) + th + 1)
    x0 = max(0, int(inked[:, 1].min()) - tw)
    x1 = min(pixels.shape[1], int(inked[:, 1].max()) + tw + 1)
    pixels = pixels[y0:y1, x0:x1]
    if th >= pixels.shape[0] or tw >= pixels.shape[1]:
        return 0
    centred = template - template.mean()
    norm = float(np.sqrt((centred**2).sum())) or 1.0

    hits: list[tuple[int, int, float]] = []
    for y in range(pixels.shape[0] - th):
        for x in range(pixels.shape[1] - tw):
            window = pixels[y : y + th, x : x + tw]
            if window.max() < 0.35:
                continue
            w_centred = window - window.mean()
            w_norm = float(np.sqrt((w_centred**2).sum()))
            if w_norm < 1e-6:
                continue
            score = float((w_centred * centred).sum() / (w_norm * norm))
            if score >= threshold:
                hits.append((x, y, score))

    hits.sort(key=lambda item: -item[2])
    kept: list[tuple[int, int, float]] = []
    for x, y, score in hits:
        if all(
            abs(x - kx) >= tw * 0.6 or abs(y - ky) >= th * 0.6 for kx, ky, _ in kept
        ):
            kept.append((x, y, score))
    return len(kept)
