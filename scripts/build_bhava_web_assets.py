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
    args = parser.parse_args()

    packages = discover_packages(args.output_root)
    if not packages:
        print("No packages discovered.", file=sys.stderr)
        sys.exit(1)

    built = 0
    for pkg in packages:
        story_no = _story_no_from_dirname(pkg.path.name)
        try:
            dest = build_web_assets_for_package(pkg.path, story_no, args.web_root)
            print(f"  [OK] {story_no} -> {dest}")
            built += 1
        except Exception as exc:
            print(f"  [FAIL] {story_no}: {exc}", file=sys.stderr)

    print(f"\nBuilt {built}/{len(packages)} web-asset packages.")


if __name__ == "__main__":
    main()
