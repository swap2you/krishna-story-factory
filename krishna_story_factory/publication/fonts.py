"""Centralized cross-platform Unicode font resolution for public exports.

Fail closed when no Unicode-complete TrueType font can render required glyphs.
Never fall back to ReportLab Helvetica or Pillow ImageFont.load_default() for
public copyright/rights text.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REQUIRED_GLYPH_SAMPLES = (
    "Bhāva",
    "Kṛṣṇa",
    "Pūtanā",
    "Rādhā",
    "Śrīmad-Bhāgavatam",
    "Caitanya-caritāmṛta",
    "Vaiṣṇava",
    "Śrīla Prabhupāda",
    "©",
    "·",
)

_FONT_CANDIDATES: tuple[tuple[Path, Path], ...] = (
    (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
    (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ),
    (
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ),
)

_REPORTLAB_REGULAR = "BhavaUnicode"
_REPORTLAB_BOLD = "BhavaUnicode-Bold"


class UnicodeFontError(RuntimeError):
    """Raised when no Unicode-complete font is available for public exports."""


@dataclass(frozen=True)
class UnicodeFontPair:
    regular_path: Path
    bold_path: Path
    reportlab_regular: str
    reportlab_bold: str

    def pillow_regular(self, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.regular_path), size)

    def pillow_bold(self, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.bold_path), size)


def _glyph_missing(font: ImageFont.FreeTypeFont, text: str) -> list[str]:
    missing: list[str] = []
    for ch in text:
        if ch.isspace():
            continue
        # Pillow: getmask1 / getbbox returning empty width indicates unsupported glyph
        # on many builds; also check font.getlength when available.
        try:
            length = float(font.getlength(ch))  # type: ignore[attr-defined]
            if length <= 0:
                missing.append(ch)
                continue
        except Exception:
            pass
        bbox = font.getbbox(ch)
        if bbox is None or (bbox[2] - bbox[0]) <= 0:
            missing.append(ch)
    return missing


def validate_font_glyph_coverage(font_path: Path, samples: tuple[str, ...] = REQUIRED_GLYPH_SAMPLES) -> list[str]:
    """Return list of sample strings that fail glyph coverage."""
    font = ImageFont.truetype(str(font_path), 24)
    failed: list[str] = []
    for sample in samples:
        missing = _glyph_missing(font, sample)
        if missing:
            failed.append(f"{sample!r} missing={''.join(missing)!r}")
    return failed


def _register_reportlab(pair: UnicodeFontPair) -> None:
    if _REPORTLAB_REGULAR not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_REPORTLAB_REGULAR, str(pair.regular_path)))
    if _REPORTLAB_BOLD not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_REPORTLAB_BOLD, str(pair.bold_path)))


@lru_cache(maxsize=1)
def resolve_unicode_fonts() -> UnicodeFontPair:
    """Resolve and validate a Unicode-complete regular/bold font pair."""
    errors: list[str] = []
    for regular, bold in _FONT_CANDIDATES:
        if not regular.is_file() or not bold.is_file():
            errors.append(f"missing:{regular}|{bold}")
            continue
        failed = validate_font_glyph_coverage(regular)
        if failed:
            errors.append(f"coverage:{regular}:{';'.join(failed)}")
            continue
        pair = UnicodeFontPair(
            regular_path=regular.resolve(),
            bold_path=bold.resolve(),
            reportlab_regular=_REPORTLAB_REGULAR,
            reportlab_bold=_REPORTLAB_BOLD,
        )
        _register_reportlab(pair)
        return pair
    raise UnicodeFontError(
        "No Unicode-complete font available for public Bhāva exports. "
        "Install Arial (Windows) or DejaVu Sans (Linux). Details: "
        + " | ".join(errors[:6])
    )


def get_reportlab_font_names() -> tuple[str, str]:
    pair = resolve_unicode_fonts()
    return pair.reportlab_regular, pair.reportlab_bold
