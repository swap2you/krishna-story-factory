#!/usr/bin/env python3
"""
Bhāva V1.2 Phase 1-2 — Brand Asset Import Pipeline

Reads consolidated_manifest.json (122 approved assets), locates source
files under the configurable source tree, copies masters into the
rollback-evidence path (.bhava/brand-import/masters/), and stages
optimized WebP + PNG web assets into the production folder hierarchy
under apps/web/public/.

Usage:
    python scripts/import_bhava_brand_assets.py [--source PATH] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SOURCE = REPO_ROOT / "MyPilotDropbox" / "bhava-brand-assets-v1"
MANIFEST_REL = "bhava-p13/refs/consolidated_manifest.json"

ROLLBACK_DIR = REPO_ROOT / ".bhava" / "brand-import"
MASTERS_DIR = ROLLBACK_DIR / "masters"
STAGING_DIR = ROLLBACK_DIR / "staging"

PUBLIC_ROOT = REPO_ROOT / "apps" / "web" / "public"
CONFIG_DIR = REPO_ROOT / "apps" / "web" / "config"
DOCS_BRAND = REPO_ROOT / "docs" / "brand"

PRODUCTION_DIRS = {
    "brand": PUBLIC_ROOT / "brand",
    "heroes": PUBLIC_ROOT / "heroes",
    "collections": PUBLIC_ROOT / "collections",
    "sections": PUBLIC_ROOT / "sections",
    "social": PUBLIC_ROOT / "social",
    "icons": PUBLIC_ROOT / "icons",
    "empty-states": PUBLIC_ROOT / "empty-states",
}

CATEGORY_TO_FOLDER: dict[str, str] = {
    "logo_system": "brand",
    "platform_icons": "icons",
    "homepage_heroes": "heroes",
    "collection_covers": "collections",
    "canto_covers": "collections",
    "section_banners": "sections",
    "social_sharing": "social",
    "learning_icons": "icons",
    "empty_states": "empty-states",
    "contact_faq": "brand",
}

CONTACT_FAQ_ICONS = {"I03_FIX.png", "I04_MAIL.png", "I05_SRC.png", "I06_TECH.png", "I07_TFB.png"}

# file-size budgets (WebP output) — warn but do not block
SIZE_BUDGETS_KB: dict[str, int] = {
    "brand": 500,
    "heroes": 300,
    "collections": 400,
    "sections": 300,
    "social": 400,
    "icons": 50,
    "empty-states": 100,
}


def _deterministic_name(entry: dict[str, Any]) -> str:
    """Derive a lowercase-kebab production filename from the manifest entry."""
    cat = entry["category"]
    fn = Path(entry["filename"]).stem

    name_map: dict[str, str] = {
        # --- Logo system ---
        "BHAVA_P1B1_01_PRIMARY_HORIZONTAL_TRANSPARENT_3600W": "logo-primary-horizontal",
        "BHAVA_P1B1_02_COMPACT_HORIZONTAL_TRANSPARENT_3600W": "logo-compact-horizontal",
        "BHAVA_P1B1_03_STACKED_TRANSPARENT_3000W": "logo-stacked",
        "BHAVA_P1B1_04_ICON_ONLY_TRANSPARENT_2048": "logo-icon-only",
        "BHAVA_P1B1_05_WORDMARK_ONLY_TRANSPARENT_3400W": "logo-wordmark",
        "BHAVA_P1B2_06_LIGHT_BACKGROUND_4200x1600": "logo-light-bg",
        "BHAVA_P1B2_07_DARK_BACKGROUND_4200x1600": "logo-dark-bg",
        "BHAVA_P1B2_08_MONOCHROME_NAVY_TRANSPARENT_3600W": "logo-mono-navy",
        "BHAVA_P1B2_09_MONOCHROME_WHITE_TRANSPARENT_3600W": "logo-mono-white",
        "BHAVA_P1B2_10_MONOCHROME_BLACK_TRANSPARENT_3600W": "logo-mono-black",
        "BHAVA_P1B3_11_GOLD_CEREMONIAL_4200x1600": "logo-gold-ceremonial",
        "BHAVA_P1B3_12_SMALL_HEADER_TRANSPARENT_3600x520": "logo-small-header",
        # --- Platform icons ---
        "bhava-apple-touch-icon-180": "apple-touch-icon-180",
        "bhava-favicon-16": "favicon-16",
        "bhava-favicon-32": "favicon-32",
        "bhava-pwa-icon-192": "pwa-icon-192",
        "bhava-pwa-icon-512": "pwa-icon-512",
        "bhava-android-adaptive-foreground-432": "android-adaptive-foreground-432",
        "bhava-browser-pinned-tab-master-1024": "browser-pinned-tab-1024",
        "bhava-maskable-icon-512": "maskable-icon-512",
        "bhava-whatsapp-group-icon-2048": "whatsapp-group-icon-2048",
        "bhava-windows-tile-310": "windows-tile-310",
        "bhava-social-profile-avatar-2048": "social-profile-avatar-2048",
        # --- Heroes ---
        "BHAVA_P3B1_01_DESKTOP_WIDE_HERO_1920x1080": "hero-desktop-wide",
        "BHAVA_P3B1_02_WEBSITE_BANNER_1920x800": "hero-website-banner",
        "BHAVA_P3B1_03_TABLET_CROP_1200x900": "hero-tablet-crop",
        "BHAVA_P3B1_04_MOBILE_PORTRAIT_1080x1440": "hero-mobile-portrait",
        "BHAVA_P3B1_05_TEXT_FREE_MASTER_3840x2160": "hero-text-free-master",
        "BHAVA_P3B2_01_DARK_TEXT_OVERLAY_SAFE_1920x1080": "hero-dark-overlay",
        "BHAVA_P3B2_02_LIGHT_TEXT_OVERLAY_SAFE_1920x1080": "hero-light-overlay",
        "BHAVA_P3B2_03_KRISHNA_BOOK_COLLECTION_HERO_1920x1080": "hero-krishna-book-collection",
        "BHAVA_P3B2_04_PARENT_CHILD_LEARNING_HERO_1920x1080": "hero-parent-child-learning",
        "BHAVA_P3B2_05_TEACHER_SUNDAY_SCHOOL_HERO_1920x1080": "hero-teacher-sunday-school",
        # --- Collection covers ---
        "BHAVA_P4B1_01_KRISHNA_BOOK_COVER_1600x2000": "collection-krishna-book",
        "BHAVA_P4B1_02_SRIMAD_BHAGAVATAM_COVER_1600x2000": "collection-srimad-bhagavatam",
        "BHAVA_P4B1_03_BHAGAVAD_GITA_COVER_1600x2000": "collection-bhagavad-gita",
        "BHAVA_P4B1_04_RAMA_KATHA_COVER_1600x2000": "collection-rama-katha",
        "BHAVA_P4B1_05_RAMAYANA_COVER_1600x2000": "collection-ramayana",
        "BHAVA_P4B2_06_RAMACARITAMANASA_COVER_1600x2000": "collection-ramacaritamanasa",
        "BHAVA_P4B2_07_DASAVATARA_COVER_1600x2000": "collection-dasavatara",
        "BHAVA_P4B2_08_CAITANYA_CARITAMRTA_COVER_1600x2000": "collection-caitanya-caritamrta",
        "BHAVA_P4B2_09_CAITANYA_BHAGAVATA_COVER_1600x2000": "collection-caitanya-bhagavata",
        "BHAVA_P4B2_10_PRABHUPADA_VANI_COVER_1600x2000": "collection-prabhupada-vani",
        "BHAVA_P4B3_11_PRAYERS_MANTRAS_COVER_1600x2000": "collection-prayers-mantras",
        "BHAVA_P4B3_12_BHAKTI_BLOG_COVER_1600x2000": "collection-bhakti-blog",
        "BHAVA_P4B3_13_TEACHER_RESOURCES_COVER_1600x2000": "collection-teacher-resources",
        "BHAVA_P4B3_14_SUNDAY_SCHOOL_COVER_1600x2000": "collection-sunday-school",
        "BHAVA_P4B3_15_PRINTABLES_COVER_1600x2000": "collection-printables",
        # --- Canto covers ---
        "BHAVA_P5B1_01_CANTO_1_RECREATED_1600x2000": "collection-canto-01",
        "BHAVA_P5B1_02_CANTO_4_RECREATED_1600x2000": "collection-canto-04",
        "BHAVA_P5B1_03_CANTO_10_RECREATED_1600x2000": "collection-canto-10",
        "BHAVA_P5B2_04_CANTO_2_RECREATED_1600x2000": "collection-canto-02",
        "BHAVA_P5B2_05_CANTO_3_RECREATED_1600x2000": "collection-canto-03",
        "BHAVA_P5B2_06_CANTO_5_RECREATED_1600x2000": "collection-canto-05",
        "BHAVA_P5B2_07_CANTO_6_RECREATED_1600x2000": "collection-canto-06",
        "BHAVA_P5B2_08_CANTO_7_RECREATED_1600x2000": "collection-canto-07",
        "BHAVA_P5B3_09_CANTO_8_1600x2000": "collection-canto-08",
        "BHAVA_P5B3_10_CANTO_9_1600x2000": "collection-canto-09",
        "BHAVA_P5B3_11_CANTO_11_1600x2000": "collection-canto-11",
        "BHAVA_P5B3_12_CANTO_12_1600x2000": "collection-canto-12",
        # --- Section banners ---
        "BNR_01_KBS": "section-krishna-book-stories",
        "BNR_02_FT": "section-featured",
        "BNR_03_SS": "section-sunday-school",
        "BNR_04_FP": "section-family-practice",
        "BNR_05_SPV": "section-prabhupada-vani",
        "BNR_06_BB": "section-bhakti-blog",
        "BNR_07_PM": "section-prayers-mantras",
        "BNR_08_PR": "section-printables-resources",
        "BNR_09_CA": "section-caitanya",
        "BNR_10_SL": "section-sloka-learning",
        "BNR_11_CT": "section-contact",
        "BNR_12_AB": "section-about",
        # --- Social ---
        "P7_01_OG": "social-og-default",
        "P7_02_X": "social-x-card",
        "P7_03_WA": "social-whatsapp-share",
        "P7_04_YT": "social-youtube-thumb",
        "P7_05_POD": "social-podcast-cover",
        "P7_06_STORY": "social-story-template",
        "P7_07_NEW": "social-new-story-post",
        "P7_08_FEST": "social-festival-template",
        "P7_09_TEACH": "social-teacher-spotlight",
        "P7_10_PRINT": "social-printable-promo",
        # --- Learning icons ---
        "I01_COL": "icon-coloring",
        "I02_DET": "icon-detail",
        "I03_SIM": "icon-simple",
        "I04_ACT": "icon-activity",
        "I05_WS": "icon-worksheet",
        "I06_CW": "icon-crossword",
        "I07_SD": "icon-study",
        "I08_DOT": "icon-dot-to-dot",
        "I09_SEQ": "icon-sequence",
        "I10_MAT": "icon-matching",
        "I11_MAZ": "icon-maze",
        "I12_MEM": "icon-memory",
        "I13_SLO": "icon-sloka",
        "I14_AUD": "icon-audio",
        "I15_READ": "icon-reading",
        "I16_TN": "icon-teacher-notes",
        "I17_PG": "icon-parent-guide",
        "I18_PRT": "icon-print",
        "I19_DWN": "icon-download",
        "I20_BMK": "icon-bookmark",
        "I21_PLY": "icon-play",
        "I22_SRC": "icon-search",
        # --- Empty states ---
        "E01_SOON": "empty-coming-soon",
        "E02_STORY": "empty-no-stories",
        "E03_ACT": "empty-no-activities",
        "E04_SLOKA": "empty-no-slokas",
        "E05_SEARCH": "empty-no-search-results",
        "E06_REVIEW": "empty-no-reviews",
        "E07_SOURCE": "empty-no-source",
        "E08_AUDIO": "empty-no-audio",
        "E09_OFF": "empty-offline",
        "E10_DONE": "empty-all-done",
        "E11_ERROR": "empty-error",
        # --- Contact / FAQ ---
        "H01_CONTACT": "hero-contact-page",
        "H02_FAQ": "hero-faq-page",
        "I03_FIX": "icon-fix",
        "I04_MAIL": "icon-mail",
        "I05_SRC": "icon-source-ref",
        "I06_TECH": "icon-tech-support",
        "I07_TFB": "icon-feedback",
    }

    base = name_map.get(fn)
    if not base:
        base = fn.lower().replace("_", "-").replace(" ", "-")
    return base


def _target_folder(entry: dict[str, Any]) -> str:
    cat = entry["category"]
    fn = entry["filename"]
    if cat == "contact_faq" and fn in CONTACT_FAQ_ICONS:
        return "icons"
    return CATEGORY_TO_FOLDER.get(cat, "brand")


def _light_dark_context(entry: dict[str, Any]) -> str:
    fn = entry["filename"].upper()
    if "DARK" in fn:
        return "dark"
    if "LIGHT" in fn:
        return "light"
    if "TRANSPARENT" in fn or entry.get("mode") == "RGBA":
        return "transparent"
    return "neutral"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 16):
            h.update(chunk)
    return h.hexdigest()


def _find_source(source_root: Path, entry: dict[str, Any]) -> Path | None:
    """Locate a source image by archive_path first, then rglob by filename."""
    # Try archive_path relative to source root (extracted zip structure)
    archive = entry.get("archive_path", "")
    pkg_stem = Path(entry.get("package", "")).stem
    candidates = [
        source_root / archive,
        source_root / pkg_stem / archive,
    ]
    # Also look inside bhava-brand-assets-v1-phase* extracted dirs
    for c in candidates:
        if c.is_file():
            return c

    # rglob by exact filename
    fname = entry["filename"]
    hits = list(source_root.rglob(fname))
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # prefer non-archive, non-QA paths
        for h in hits:
            parts_lower = str(h).lower()
            if "archive" not in parts_lower and "10_qa" not in parts_lower:
                return h
        return hits[0]
    return None


def load_manifest(source_root: Path) -> list[dict[str, Any]]:
    manifest_path = source_root / MANIFEST_REL
    if not manifest_path.is_file():
        # try repo-level docs/brand copy
        alt = DOCS_BRAND / "consolidated_manifest.json"
        if alt.is_file():
            manifest_path = alt
        else:
            print(f"ERROR: Manifest not found at {manifest_path}", file=sys.stderr)
            sys.exit(1)
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["assets"]


def run_import(source_root: Path, dry_run: bool = False) -> dict[str, Any]:
    assets = load_manifest(source_root)
    print(f"Manifest loaded: {len(assets)} assets")

    # Ensure directories exist
    for d in [MASTERS_DIR, STAGING_DIR, CONFIG_DIR, DOCS_BRAND]:
        d.mkdir(parents=True, exist_ok=True)
    for d in PRODUCTION_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

    registry: list[dict[str, Any]] = []
    imported = 0
    missing_list: list[dict[str, str]] = []
    warnings: list[str] = []
    checksum_failures: list[str] = []
    skipped_identical = 0

    for entry in assets:
        src = _find_source(source_root, entry)
        prod_name = _deterministic_name(entry)
        folder_key = _target_folder(entry)
        target_dir = PRODUCTION_DIRS[folder_key]

        if src is None:
            missing_list.append({
                "filename": entry["filename"],
                "category": entry["category"],
                "phase": entry["phase"],
            })
            continue

        # Verify checksum
        actual_hash = sha256_file(src)
        expected_hash = entry.get("sha256", "")
        checksum_ok = actual_hash == expected_hash
        if not checksum_ok and expected_hash:
            checksum_failures.append(
                f"{entry['filename']}: expected {expected_hash[:16]}… got {actual_hash[:16]}…"
            )

        # Master copy (preserve original in rollback dir)
        master_subdir = MASTERS_DIR / folder_key
        master_subdir.mkdir(parents=True, exist_ok=True)
        master_dest = master_subdir / entry["filename"]

        ext = entry.get("extension", Path(entry["filename"]).suffix).lower()
        is_png = ext == ".png"
        is_rgba = entry.get("mode") == "RGBA"

        # Production output: prefer WebP for raster
        webp_name = prod_name + ".webp"
        png_name = prod_name + ".png"

        # Stage paths
        staging_sub = STAGING_DIR / folder_key
        staging_sub.mkdir(parents=True, exist_ok=True)

        prod_webp = target_dir / webp_name
        prod_png = target_dir / png_name if is_rgba else None

        if dry_run:
            print(f"  [DRY] {entry['filename']} -> {folder_key}/{webp_name}")
            imported += 1
        else:
            # Copy master (skip if identical checksum already exists)
            if master_dest.is_file() and sha256_file(master_dest) == actual_hash:
                pass  # master already present
            else:
                shutil.copy2(src, master_dest)

            try:
                from PIL import Image

                img = Image.open(src)
                # Strip metadata by re-encoding from raw pixel data
                clean = img.copy()
                clean.info = {}

                # WebP output (staging first)
                staged_webp = staging_sub / webp_name
                quality = 85 if img.size[0] * img.size[1] > 500_000 else 90
                if is_rgba:
                    clean.save(staged_webp, "WEBP", quality=quality, method=4)
                else:
                    if clean.mode != "RGB":
                        clean = clean.convert("RGB")
                    clean.save(staged_webp, "WEBP", quality=quality, method=4)

                # Swap staging -> production (no silent overwrite)
                if prod_webp.is_file():
                    existing_hash = sha256_file(prod_webp)
                    new_hash = sha256_file(staged_webp)
                    if existing_hash == new_hash:
                        skipped_identical += 1
                        os.remove(staged_webp)
                    else:
                        backup = ROLLBACK_DIR / "replaced" / folder_key
                        backup.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(prod_webp), str(backup / webp_name))
                        shutil.move(str(staged_webp), str(prod_webp))
                else:
                    shutil.move(str(staged_webp), str(prod_webp))

                # For RGBA logos, also keep a PNG for transparency fidelity
                if is_rgba and is_png:
                    staged_png = staging_sub / png_name
                    clean_rgba = img.copy()
                    clean_rgba.info = {}
                    clean_rgba.save(staged_png, "PNG", optimize=True)
                    if prod_png and prod_png.is_file():
                        existing_hash = sha256_file(prod_png)
                        new_hash = sha256_file(staged_png)
                        if existing_hash == new_hash:
                            os.remove(staged_png)
                        else:
                            backup = ROLLBACK_DIR / "replaced" / folder_key
                            backup.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(prod_png), str(backup / png_name))
                            shutil.move(str(staged_png), str(prod_png))
                    elif prod_png:
                        shutil.move(str(staged_png), str(prod_png))

                # Size budget check
                budget_kb = SIZE_BUDGETS_KB.get(folder_key, 500)
                actual_kb = prod_webp.stat().st_size / 1024 if prod_webp.is_file() else 0
                if actual_kb > budget_kb:
                    warnings.append(
                        f"SIZE OVER BUDGET: {folder_key}/{webp_name} "
                        f"= {actual_kb:.0f} KB (budget {budget_kb} KB)"
                    )

                imported += 1

            except Exception as exc:
                warnings.append(f"CONVERT ERROR: {entry['filename']}: {exc}")
                # Still count as imported if master was copied
                imported += 1

        # Build registry entry
        w, h = entry.get("width", 0), entry.get("height", 0)
        reg = {
            "logicalId": prod_name,
            "sourceMaster": entry["filename"],
            "productionPath": f"/{folder_key}/{webp_name}",
            "dimensions": {"width": w, "height": h},
            "lightDarkContext": _light_dark_context(entry),
            "responsiveVariants": [],
            "altTextPurpose": _alt_text(entry, prod_name),
            "checksum": expected_hash,
            "approvalState": "approved",
            "category": entry["category"],
            "phase": entry["phase"],
        }
        if is_rgba and is_png:
            reg["pngFallback"] = f"/{folder_key}/{png_name}"
        registry.append(reg)

    # Write brand-assets.json
    brand_config = {
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "assetCount": len(registry),
        "assets": registry,
    }
    config_path = CONFIG_DIR / "brand-assets.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(brand_config, f, indent=2, ensure_ascii=False)
    print(f"Registry written: {config_path} ({len(registry)} entries)")

    # Copy manifest into docs/brand/
    manifest_src = source_root / MANIFEST_REL
    if manifest_src.is_file():
        shutil.copy2(manifest_src, DOCS_BRAND / "consolidated_manifest.json")
        print(f"Manifest copied to {DOCS_BRAND / 'consolidated_manifest.json'}")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": str(source_root),
        "manifest_total": len(assets),
        "imported": imported,
        "missing": len(missing_list),
        "missing_assets": missing_list,
        "checksum_failures": checksum_failures,
        "skipped_identical": skipped_identical,
        "warnings": warnings,
        "registry_path": str(config_path),
    }

    report_path = ROLLBACK_DIR / "import_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Import report: {report_path}")

    print(f"\nIMPORT COMPLETE: {imported}/{len(assets)} imported, "
          f"{len(missing_list)} missing, {skipped_identical} skipped (identical)")
    if checksum_failures:
        print(f"  {len(checksum_failures)} checksum mismatch(es)")
    if warnings:
        print(f"  {len(warnings)} warning(s)")
        for w in warnings[:10]:
            print(f"    [WARN] {w}")

    return report


def _alt_text(entry: dict[str, Any], prod_name: str) -> str:
    """Generate semantic alt text from the production name and category."""
    cat_labels = {
        "logo_system": "Bhāva logo",
        "platform_icons": "Bhāva app icon",
        "homepage_heroes": "Bhāva homepage hero image",
        "collection_covers": "Collection cover art",
        "canto_covers": "Śrīmad-Bhāgavatam canto cover",
        "section_banners": "Section banner",
        "social_sharing": "Social media sharing image",
        "learning_icons": "Learning activity icon",
        "empty_states": "Empty state illustration",
        "contact_faq": "Contact/FAQ asset",
    }
    base = cat_labels.get(entry["category"], "Brand asset")
    desc = prod_name.replace("-", " ").replace("logo ", "").replace("icon ", "")
    return f"{base} — {desc}"


def main():
    parser = argparse.ArgumentParser(description="Import Bhāva brand assets")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="Root of extracted brand asset tree")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be imported without copying")
    args = parser.parse_args()

    if not args.source.is_dir():
        print(f"ERROR: Source directory not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    run_import(args.source, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
