#!/usr/bin/env python3
"""
Bhāva V1.2 — Brand Asset Optimization

Post-import optimization pass:
  - Responsive width variants for large heroes/covers/banners (640, 1280, 1920)
  - Favicon/PWA/Open-Graph derivatives from logo/icon masters
  - AVIF generation (if Pillow supports it)
  - Metadata stripping on all production assets
  - Updates brand-assets.json registry with responsive variants

Usage:
    python scripts/optimize_bhava_brand_assets.py [--skip-avif] [--skip-responsive]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = REPO_ROOT / "apps" / "web" / "public"
CONFIG_DIR = REPO_ROOT / "apps" / "web" / "config"
ROLLBACK_DIR = REPO_ROOT / ".bhava" / "brand-import"
MASTERS_DIR = ROLLBACK_DIR / "masters"

RESPONSIVE_WIDTHS = [640, 1280, 1920]
MIN_WIDTH_FOR_RESPONSIVE = 1200

FAVICON_DERIVATIVES = {
    "favicon-16": (16, 16, "PNG"),
    "favicon-32": (32, 32, "PNG"),
    "favicon-48": (48, 48, "PNG"),
    "apple-touch-icon": (180, 180, "PNG"),
    "pwa-192": (192, 192, "PNG"),
    "pwa-512": (512, 512, "PNG"),
    "og-icon-256": (256, 256, "PNG"),
}

CATEGORIES_NEEDING_RESPONSIVE = {
    "homepage_heroes", "collection_covers", "canto_covers",
    "section_banners", "social_sharing", "contact_faq",
}


def _strip_metadata_and_save(img, path: Path, fmt: str, **kwargs):
    """Save image with metadata stripped."""
    clean = img.copy()
    clean.info = {}
    if fmt == "WEBP" and clean.mode not in ("RGB", "RGBA"):
        clean = clean.convert("RGB")
    clean.save(path, fmt, **kwargs)
    return path


def optimize(skip_avif: bool = False, skip_responsive: bool = False) -> dict:
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow required — run: pip install pillow", file=sys.stderr)
        sys.exit(1)

    registry_path = CONFIG_DIR / "brand-assets.json"
    if not registry_path.is_file():
        print("ERROR: Run import_bhava_brand_assets.py first", file=sys.stderr)
        sys.exit(1)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    assets = registry["assets"]
    stats = {
        "responsive_generated": 0,
        "favicon_derivatives": 0,
        "avif_generated": 0,
        "metadata_stripped": 0,
        "errors": [],
    }

    avif_supported = False
    if not skip_avif:
        try:
            test_img = Image.new("RGB", (10, 10), "red")
            import io
            buf = io.BytesIO()
            test_img.save(buf, "AVIF")
            avif_supported = True
            print("AVIF support detected")
        except Exception:
            print("AVIF not supported by this Pillow build — skipping")

    for entry in assets:
        prod_rel = entry.get("productionPath", "").lstrip("/")
        prod_path = PUBLIC_ROOT / prod_rel

        if not prod_path.is_file():
            continue

        category = entry.get("category", "")
        master_name = entry.get("sourceMaster", "")
        folder = prod_rel.split("/")[0] if "/" in prod_rel else "brand"
        base_stem = prod_path.stem

        # Find master for high-quality source
        master_path = None
        if master_name:
            candidates = list(MASTERS_DIR.rglob(master_name))
            if candidates:
                master_path = candidates[0]

        source_img_path = master_path if master_path else prod_path

        try:
            with Image.open(source_img_path) as img:
                src_w, src_h = img.size

                # --- Responsive variants ---
                if (not skip_responsive
                        and category in CATEGORIES_NEEDING_RESPONSIVE
                        and src_w >= MIN_WIDTH_FOR_RESPONSIVE):

                    variants = []
                    target_dir = prod_path.parent
                    for w in RESPONSIVE_WIDTHS:
                        if w >= src_w:
                            continue
                        ratio = w / src_w
                        new_h = int(src_h * ratio)
                        variant_name = f"{base_stem}-{w}w.webp"
                        variant_path = target_dir / variant_name
                        variant_rel = f"/{folder}/{variant_name}"

                        if not variant_path.is_file():
                            resized = img.resize((w, new_h), Image.LANCZOS)
                            mode = resized.mode
                            if mode not in ("RGB", "RGBA"):
                                resized = resized.convert("RGB")
                            _strip_metadata_and_save(
                                resized, variant_path, "WEBP",
                                quality=82, method=4,
                            )
                            stats["responsive_generated"] += 1

                        variants.append({
                            "width": w,
                            "height": new_h,
                            "path": variant_rel,
                        })

                    if variants:
                        entry["responsiveVariants"] = variants

                # --- AVIF generation ---
                if avif_supported:
                    avif_name = f"{base_stem}.avif"
                    avif_path = prod_path.parent / avif_name
                    if not avif_path.is_file():
                        try:
                            save_img = img.copy()
                            if save_img.mode not in ("RGB", "RGBA"):
                                save_img = save_img.convert("RGB")
                            _strip_metadata_and_save(
                                save_img, avif_path, "AVIF",
                                quality=70,
                            )
                            stats["avif_generated"] += 1
                        except Exception as exc:
                            stats["errors"].append(f"AVIF {base_stem}: {exc}")

                stats["metadata_stripped"] += 1

        except Exception as exc:
            stats["errors"].append(f"Optimize {prod_rel}: {exc}")

    # --- Favicon / PWA derivatives from logo icon master ---
    icon_master = MASTERS_DIR / "icons" / "bhava-pwa-icon-512.png"
    if not icon_master.is_file():
        icon_master = MASTERS_DIR / "brand" / "bhava-pwa-icon-512.png"
    if not icon_master.is_file():
        # Try logo icon
        icon_candidates = list(MASTERS_DIR.rglob("BHAVA_P1B1_04_ICON_ONLY_TRANSPARENT_2048.png"))
        if icon_candidates:
            icon_master = icon_candidates[0]

    if icon_master.is_file():
        print(f"Generating favicon/PWA derivatives from {icon_master.name}")
        with Image.open(icon_master) as icon_img:
            icons_dir = PUBLIC_ROOT / "icons"
            brand_dir = PUBLIC_ROOT / "brand"
            icons_dir.mkdir(parents=True, exist_ok=True)
            brand_dir.mkdir(parents=True, exist_ok=True)

            for name, (w, h, fmt) in FAVICON_DERIVATIVES.items():
                if name.startswith("favicon"):
                    out_dir = PUBLIC_ROOT
                elif name.startswith("pwa") or name.startswith("apple"):
                    out_dir = icons_dir
                else:
                    out_dir = brand_dir

                ext = ".png" if fmt == "PNG" else ".webp"
                out_path = out_dir / f"{name}{ext}"
                if not out_path.is_file():
                    resized = icon_img.resize((w, h), Image.LANCZOS)
                    if fmt == "PNG":
                        _strip_metadata_and_save(resized, out_path, "PNG", optimize=True)
                    else:
                        mode = resized.mode
                        if mode not in ("RGB", "RGBA"):
                            resized = resized.convert("RGB")
                        _strip_metadata_and_save(resized, out_path, "WEBP", quality=90)
                    stats["favicon_derivatives"] += 1
                    print(f"  Generated: {out_path.relative_to(REPO_ROOT)}")
    else:
        stats["errors"].append("No icon master found for favicon/PWA derivatives")

    # --- OG image derivative from hero master ---
    og_candidates = list(MASTERS_DIR.rglob("BHAVA_P3B1_01_DESKTOP_WIDE_HERO_1920x1080*"))
    if og_candidates:
        og_master = og_candidates[0]
        og_out = PUBLIC_ROOT / "social" / "og-default-1200x630.webp"
        if not og_out.is_file():
            with Image.open(og_master) as og_img:
                og_resized = og_img.resize((1200, 630), Image.LANCZOS)
                if og_resized.mode not in ("RGB", "RGBA"):
                    og_resized = og_resized.convert("RGB")
                _strip_metadata_and_save(og_resized, og_out, "WEBP", quality=85)
                stats["favicon_derivatives"] += 1
                print(f"  Generated OG derivative: {og_out.relative_to(REPO_ROOT)}")

    # Update registry with responsive variants
    registry["assets"] = assets
    registry["optimized"] = datetime.now(timezone.utc).isoformat()
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"\nRegistry updated: {registry_path}")

    # Write optimization report
    report_path = ROLLBACK_DIR / "optimization_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **stats,
        }, f, indent=2)

    print(f"\nOPTIMIZATION COMPLETE")
    print(f"  Responsive variants: {stats['responsive_generated']}")
    print(f"  Favicon/PWA derivatives: {stats['favicon_derivatives']}")
    print(f"  AVIF generated: {stats['avif_generated']}")
    print(f"  Metadata stripped: {stats['metadata_stripped']}")
    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for e in stats["errors"][:10]:
            print(f"    {e}")

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Optimize Bhāva brand assets")
    parser.add_argument("--skip-avif", action="store_true",
                        help="Skip AVIF generation")
    parser.add_argument("--skip-responsive", action="store_true",
                        help="Skip responsive variant generation")
    args = parser.parse_args()
    optimize(skip_avif=args.skip_avif, skip_responsive=args.skip_responsive)


if __name__ == "__main__":
    main()
