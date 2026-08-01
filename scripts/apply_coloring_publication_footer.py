#!/usr/bin/env python3
"""Apply local PIL publication footer strips to coloring pages (001–020).

Does not regenerate illustrations or call paid APIs. Extends the canvas with a
bottom credit strip via append_image_credit_strip when a warm-cream footer is
not already present. Safe to re-run (skips images that already have a footer).

Usage:
    python scripts/apply_coloring_publication_footer.py
    python scripts/apply_coloring_publication_footer.py --max-story 20 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from krishna_story_factory.publication.artifacts import append_image_credit_strip  # noqa: E402
from krishna_story_factory.publication.identity import load_identity  # noqa: E402
from krishna_story_factory.publication.work_manifest import first_publication_year  # noqa: E402

COLORING_NAMES = ("coloring_page.png", "simple_coloring_page.png")
# Matching append_image_credit_strip fill color.
_CREAM = (0xF7, 0xF1, 0xE6)


def discover_package(output_root: Path, story_no: str) -> Path | None:
    matches = [p for p in sorted(output_root.glob(f"{story_no}_*")) if p.is_dir()]
    if len(matches) == 1:
        return matches[0]
    return None


def has_publication_footer(image_path: Path) -> bool:
    """Detect the warm-cream credit strip applied by append_image_credit_strip."""
    with Image.open(image_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        strip_h = max(40, int(height * 0.05))
        band = rgb.crop((0, height - strip_h, width, height))
        # Sample every Nth pixel for speed; avoid deprecated getdata().
        sample_step = 4
        close = 0
        dark = 0
        total = 0
        bw, bh = band.size
        for y in range(0, bh, sample_step):
            for x in range(0, bw, sample_step):
                px = band.getpixel((x, y))
                total += 1
                if all(abs(int(px[i]) - _CREAM[i]) <= 18 for i in range(3)):
                    close += 1
                if (int(px[0]) + int(px[1]) + int(px[2])) / 3 < 90:
                    dark += 1
        if total == 0:
            return False
        cream_ratio = close / total
        # Warm cream majority + some ink (credit glyphs).
        return cream_ratio >= 0.55 and dark >= 40


def apply_to_package(
    package: Path,
    *,
    identity,
    dry_run: bool,
) -> list[dict]:
    notes: list[dict] = []
    manifest_path = package / "manifest.json"
    year = None
    ai_image = False
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            manifest = {}
        rights = manifest.get("rights") or {}
        year = first_publication_year(rights if isinstance(rights, dict) else {})
        images = manifest.get("images") or {}
        ai_image = bool(images.get("model")) if isinstance(images, dict) else False

    for name in COLORING_NAMES:
        path = package / name
        if not path.is_file():
            notes.append({"file": name, "status": "missing"})
            continue
        if has_publication_footer(path):
            notes.append({"file": name, "status": "skipped_existing_footer"})
            continue
        if dry_run:
            notes.append({"file": name, "status": "would_apply"})
            continue
        note = append_image_credit_strip(
            path,
            path,
            year=year,
            ai_image=False,  # coloring pages use compact © line, not poster AI wording
            identity=identity,
        )
        notes.append({"file": name, "status": "applied", **note})
        _ = ai_image  # reserved for future poster-style wording if needed
    return notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "output")
    parser.add_argument("--max-story", type=int, default=20)
    parser.add_argument("--min-story", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    identity = load_identity(ROOT)
    applied = 0
    skipped = 0
    missing_pkg = 0

    for number in range(args.min_story, args.max_story + 1):
        story_no = f"{number:03d}"
        package = discover_package(args.output_root, story_no)
        if package is None:
            print(f"  [MISS] {story_no}: no package folder")
            missing_pkg += 1
            continue
        notes = apply_to_package(package, identity=identity, dry_run=args.dry_run)
        for note in notes:
            status = note.get("status")
            label = "DRY" if args.dry_run and status == "would_apply" else status
            print(f"  [{label}] {story_no}/{note.get('file')}")
            if status in {"applied", "would_apply"}:
                applied += 1
            elif status == "skipped_existing_footer":
                skipped += 1

    print(
        f"\nDone. apply/would_apply={applied} skipped_existing={skipped} "
        f"missing_packages={missing_pkg} dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
