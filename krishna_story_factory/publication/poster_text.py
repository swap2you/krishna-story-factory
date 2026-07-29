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

from PIL import Image, ImageDraw, ImageFont

from .artifacts import append_image_credit_strip
from .fonts import missing_glyphs, resolve_unicode_fonts
from .identity import PublicationIdentity

# Unicode replacement character and the codepoints commonly substituted for a
# missing glyph by viewers. Any of these in public poster text is a defect.
TOFU_CODEPOINTS = ("\ufffd", "\u25a1", "\u25a0", "\u2b1b", "\u2b1c")


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


def _bands_for_art_height(art_height: int) -> tuple[int, int]:
    """Mirror of ``compose_poster`` band sizing. Keep in lockstep with it."""
    return max(int(art_height * 0.08), 72), max(int(art_height * 0.06), 56)


#: Flat backdrop colour that compose_poster paints behind the title/caption bands.
BAND_BACKDROP = (0x12, 0x0C, 0x06)


def derive_poster_geometry(size: tuple[int, int]) -> PosterGeometry:
    """Invert the composed-poster band geometry, or fail when ambiguous."""
    width, height = size
    solutions = [
        art_height
        for art_height in range(1, height)
        if art_height + sum(_bands_for_art_height(art_height)) == height
    ]
    if len(solutions) != 1:
        raise ValueError(
            f"Cannot uniquely recover poster artwork region for size {size}: "
            f"candidate art heights={solutions}"
        )
    art_height = solutions[0]
    title_band, footer_band = _bands_for_art_height(art_height)
    return PosterGeometry(
        width=width,
        height=height,
        art_height=art_height,
        title_band=title_band,
        footer_band=footer_band,
    )


def composed_size(poster_path: Path) -> tuple[int, int]:
    """Size of a finished poster with its credit strip removed."""
    with Image.open(poster_path) as img:
        width, height = img.size
    return (width, height - _infer_strip_height((width, height)))


def has_text_bands(poster_path: Path) -> bool:
    """True when a poster actually carries title/caption bands.

    Some posters are bare artwork plus a credit strip. Size arithmetic alone can
    produce a spurious decomposition for those, so confirm the band corners hold
    the flat backdrop colour that compose_poster paints.
    """
    with Image.open(poster_path) as img:
        rgb = img.convert("RGB")
        try:
            geometry = derive_poster_geometry(composed_size(poster_path))
        except ValueError:
            return False
        probes = [
            (2, 2),
            (rgb.width - 3, 2),
            (2, geometry.title_band - 2),
            (2, geometry.title_band + geometry.art_height + 2),
        ]
        return all(_near(rgb.getpixel(p), BAND_BACKDROP) for p in probes)


def _near(pixel: tuple[int, ...], target: tuple[int, int, int], tolerance: int = 12) -> bool:
    return all(abs(int(a) - int(b)) <= tolerance for a, b in zip(pixel[:3], target))


def extract_poster_art(master_path: Path, dest_path: Path) -> PosterGeometry:
    """Write the untouched artwork region of a composed poster to ``dest_path``."""
    with Image.open(master_path) as img:
        geometry = derive_poster_geometry(img.size)
        art = img.convert("RGB").crop(geometry.art_box)
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
        strip_h = strip_height if strip_height is not None else _infer_strip_height(rgb.size)
        composed_height = height - strip_h
        geometry = derive_poster_geometry((width, composed_height))
        return {
            "title": rgb.crop(geometry.title_box),
            "caption": rgb.crop(geometry.caption_box),
            "credit": rgb.crop((0, composed_height, width, height)),
            "full": rgb.copy(),
        }


def _infer_strip_height(size: tuple[int, int]) -> int:
    """Find the credit-strip height whose remainder is a valid composed poster."""
    width, height = size
    for candidate in range(40, max(41, int(height * 0.2))):
        try:
            derive_poster_geometry((width, height - candidate))
        except ValueError:
            continue
        if candidate == max(40, int((height - candidate) * 0.05)):
            return candidate
    raise ValueError(f"Cannot infer credit-strip height for poster size {size}")


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
    from ..images.generator import _wrap

    width, _ = composed_size
    geometry = derive_poster_geometry(composed_size)
    font = ImageFont.load_default()
    max_w = width - int(width * 0.06) * 2

    title_band = Image.new("RGB", (width, geometry.title_band), "#120c06")
    draw = ImageDraw.Draw(title_band)
    y = 16
    for line in _wrap(draw, title, font, max_w)[:2]:
        draw.text((width // 2, y), line, font=font, fill="#f6e7b8", anchor="ma")
        y += font.size + 4

    caption_band = Image.new("RGB", (width, geometry.footer_band), "#120c06")
    draw = ImageDraw.Draw(caption_band)
    y = 14
    for line in _wrap(draw, caption, font, max_w)[:2]:
        draw.text((width // 2, y), line, font=font, fill="#efe2c0", anchor="ma")
        y += font.size + 4

    return {"title": title_band, "caption": caption_band}


def verify_legacy_text_preserved(
    old_poster: Path, composed_size: tuple[int, int], title: str, caption: str
) -> dict[str, bool]:
    """Check the given strings reproduce the old poster's text bands exactly."""
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
