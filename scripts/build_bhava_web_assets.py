#!/usr/bin/env python
"""CLI: build Bhāva web-assets for every discovered story package under output/.

Usage:
    PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py
    PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py --output-root output --web-root data/web-assets
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from bhava_api.catalog.filesystem import discover_packages  # noqa: E402
from bhava_api.web_assets.builder import build_web_assets_for_package  # noqa: E402


def _story_no_from_dirname(dirname: str) -> str:
    m = re.match(r"^(\d{3})_", dirname)
    return m.group(1) if m else dirname[:3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Bhāva web-assets for all story packages")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output",
                        help="Root containing story packages (default: output/)")
    parser.add_argument("--web-root", type=Path, default=ROOT / "data" / "web-assets",
                        help="Destination for web-asset files (default: data/web-assets/)")
    parser.add_argument(
        "--recommended-playback-rate",
        type=float,
        default=None,
        help=(
            "Optional uniform playback rate for all stories. "
            "When omitted, per-story rates from recommended_playback_rates are used."
        ),
    )
    parser.add_argument(
        "--max-story",
        type=int,
        default=None,
        help="Optional upper story number inclusive (e.g. 20)",
    )
    parser.add_argument(
        "--story-no",
        type=str,
        default=None,
        help="Build only one story number (e.g. 011). Used by create-next-bhava-story.ps1.",
    )
    args = parser.parse_args()

    packages = discover_packages(args.output_root)
    if not packages:
        print("No packages discovered.", file=sys.stderr)
        sys.exit(1)

    only = args.story_no.strip().zfill(3) if args.story_no else None
    built = 0
    considered = 0
    for pkg in packages:
        story_no = _story_no_from_dirname(pkg.path.name)
        if only is not None and story_no != only:
            continue
        if args.max_story is not None:
            try:
                if int(story_no) > args.max_story:
                    continue
            except ValueError:
                continue
        considered += 1
        try:
            dest = build_web_assets_for_package(
                pkg.path,
                story_no,
                args.web_root,
                recommended_playback_rate=args.recommended_playback_rate,
            )
            print(f"  [OK] {story_no} -> {dest}")
            built += 1
        except Exception as exc:
            print(f"  [FAIL] {story_no}: {exc}", file=sys.stderr)

    if only is not None and considered == 0:
        print(f"No package found for story {only}.", file=sys.stderr)
        sys.exit(1)
    if only is not None and built == 0:
        sys.exit(1)

    print(f"\nBuilt {built}/{considered or len(packages)} web-asset packages.")


if __name__ == "__main__":
    main()
