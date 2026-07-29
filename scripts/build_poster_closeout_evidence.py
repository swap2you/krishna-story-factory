"""Build the CLOSEOUT-B1 poster evidence bundle.

Renders title/caption/credit crops for the corrected posters, the matching
crops from the superseded archive so the defect and the fix sit side by side,
and a machine-readable glyph report. Reads packages only; writes only under
``docs/product/launch/final-poster-closeout``.

    .\\.venv\\Scripts\\python.exe scripts\\build_poster_closeout_evidence.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from krishna_story_factory.publication.fonts import resolve_unicode_fonts  # noqa: E402
from krishna_story_factory.publication.poster_text import (  # noqa: E402
    composed_size,
    count_missing_glyph_boxes,
    derive_poster_geometry,
    poster_band_crops,
)

OUT = ROOT / "docs" / "product" / "launch" / "final-poster-closeout"
STORIES = ("007", "009")
SUPERSEDED_VERSION = "2.1.1-copyright"
MASTER_VERSION = "2.0"
BANDS = ("title", "caption", "credit")


def package_dir(story: str) -> Path:
    return next((ROOT / "output").glob(f"{story}_*"))


def archive_dir(story: str, version: str) -> Path:
    return ROOT / "output" / "_archive" / "pre-copyright" / story / version


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def band_report(poster: Path) -> dict:
    """Missing-glyph box counts per band, probed with several .notdef templates."""
    fonts = resolve_unicode_fonts()
    templates: dict[str, ImageFont.FreeTypeFont] = {
        "resolved_bold_42": fonts.pillow_bold(42),
        "resolved_regular_24": fonts.pillow_regular(24),
        "pillow_default": ImageFont.load_default(),
    }
    crops = poster_band_crops(poster)
    report: dict[str, dict] = {}
    for band in BANDS:
        report[band] = {
            "missing_glyph_boxes": {
                name: count_missing_glyph_boxes(crops[band], font)
                for name, font in templates.items()
            }
        }
    return report


def artwork_matches_master(poster: Path, master: Path) -> bool:
    """The sacred artwork region must be byte-identical to the 2.0 master."""
    geometry = derive_poster_geometry(composed_size(poster))
    with Image.open(poster) as live, Image.open(master) as original:
        live_art = live.convert("RGB").crop(geometry.art_box)
        master_art = original.convert("RGB").crop(
            derive_poster_geometry(original.size).art_box
        )
        return live_art.tobytes() == master_art.tobytes()


def write_crops(poster: Path, prefix: str) -> dict[str, str]:
    crops = poster_band_crops(poster)
    written: dict[str, str] = {}
    for name in ("full", *BANDS):
        dest = OUT / f"{prefix}-{name}.png"
        crops[name].save(dest, "PNG")
        written[name] = dest.relative_to(ROOT).as_posix()
    return written


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fonts = resolve_unicode_fonts()
    evidence: dict = {
        "closeout_id": "CLOSEOUT-B1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "resolved_font_regular": str(fonts.regular_path),
        "resolved_font_bold": str(fonts.bold_path),
        "stories": {},
    }

    for story in STORIES:
        folder = package_dir(story)
        poster = folder / "story_poster.png"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        publication = manifest.get("publication") or {}
        superseded = archive_dir(story, SUPERSEDED_VERSION) / "story_poster.png"
        master = archive_dir(story, MASTER_VERSION) / "story_poster.png"

        entry: dict = {
            "package": folder.name,
            "version": manifest.get("version"),
            "supersedes": publication.get("supersedes"),
            "archive_relative": publication.get("archive_relative"),
            "masters_relative": publication.get("masters_relative"),
            "poster_sha256": sha256(poster),
            "superseded_poster_sha256": sha256(superseded),
            "master_poster_sha256": sha256(master),
            "artwork_region_identical_to_master": artwork_matches_master(poster, master),
            "glyph_validation": publication.get("poster_text_glyph_validation"),
            "artifact_note": (publication.get("artifact_notes") or {})
            .get("images", {})
            .get("story_poster.png"),
            "corrected": band_report(poster),
            "superseded": band_report(superseded),
            "crops": write_crops(poster, f"{story}-poster"),
            "superseded_crops": write_crops(superseded, f"{story}-poster-superseded"),
        }
        evidence["stories"][story] = entry

    corrected_clean = all(
        counts == 0
        for story in evidence["stories"].values()
        for band in story["corrected"].values()
        for counts in band["missing_glyph_boxes"].values()
    )
    superseded_defective = all(
        any(
            count > 0
            for band in story["superseded"].values()
            for count in band["missing_glyph_boxes"].values()
        )
        for story in evidence["stories"].values()
    )
    evidence["result"] = {
        "corrected_posters_free_of_missing_glyph_boxes": corrected_clean,
        "superseded_posters_reproduce_the_defect": superseded_defective,
        "artwork_preserved": all(
            story["artwork_region_identical_to_master"]
            for story in evidence["stories"].values()
        ),
        "ok": corrected_clean and superseded_defective,
    }

    target = OUT / "glyph-validation.json"
    target.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(evidence["result"], indent=2))
    print(f"wrote {target}")
    return 0 if evidence["result"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
