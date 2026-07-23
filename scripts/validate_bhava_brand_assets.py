#!/usr/bin/env python3
"""
Bhāva V1.2 — Brand Asset Validation

Checks all imported brand assets against the consolidated manifest:
  - Presence of every approved asset in production directories
  - SHA-256 checksum of masters vs manifest
  - Image dimensions match expectations
  - File-size budget compliance
  - brand-assets.json registry completeness & schema
  - Responsive variant existence (after optimize step)

Usage:
    python scripts/validate_bhava_brand_assets.py [--strict]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = REPO_ROOT / "apps" / "web" / "public"
CONFIG_DIR = REPO_ROOT / "apps" / "web" / "config"
ROLLBACK_DIR = REPO_ROOT / ".bhava" / "brand-import"
MASTERS_DIR = ROLLBACK_DIR / "masters"
DOCS_BRAND = REPO_ROOT / "docs" / "brand"

SIZE_BUDGETS_KB: dict[str, int] = {
    "brand": 500,
    "heroes": 300,
    "collections": 400,
    "sections": 300,
    "social": 400,
    "icons": 50,
    "empty-states": 100,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 16):
            h.update(chunk)
    return h.hexdigest()


def validate() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    passed: list[str] = []

    # 1. Load manifest
    manifest_path = DOCS_BRAND / "consolidated_manifest.json"
    if not manifest_path.is_file():
        errors.append(f"Manifest not found at {manifest_path}")
        return _result(errors, warnings, passed)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assets = manifest["assets"]
    passed.append(f"Manifest loaded: {len(assets)} assets")

    # 2. Load brand-assets.json registry
    registry_path = CONFIG_DIR / "brand-assets.json"
    if not registry_path.is_file():
        errors.append(f"Registry not found at {registry_path}")
    else:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        reg_assets = registry.get("assets", [])
        reg_ids = {a["logicalId"] for a in reg_assets}
        passed.append(f"Registry loaded: {len(reg_assets)} entries")

        if len(reg_assets) != len(assets):
            warnings.append(
                f"Registry has {len(reg_assets)} entries vs {len(assets)} manifest assets"
            )

        required_fields = [
            "logicalId", "sourceMaster", "productionPath", "dimensions",
            "lightDarkContext", "responsiveVariants", "altTextPurpose",
            "checksum", "approvalState",
        ]
        for i, entry in enumerate(reg_assets):
            for field in required_fields:
                if field not in entry:
                    errors.append(f"Registry entry {i} ({entry.get('logicalId', '?')}): missing '{field}'")

    # 3. Check production files exist
    missing_production = []
    present_production = []
    size_over_budget = []

    if registry_path.is_file():
        for entry in reg_assets:
            prod_path_rel = entry.get("productionPath", "")
            if prod_path_rel.startswith("/"):
                prod_path_rel = prod_path_rel[1:]
            prod_path = PUBLIC_ROOT / prod_path_rel

            if not prod_path.is_file():
                missing_production.append(prod_path_rel)
            else:
                present_production.append(prod_path_rel)
                # Size budget
                folder_key = prod_path_rel.split("/")[0] if "/" in prod_path_rel else "brand"
                budget_kb = SIZE_BUDGETS_KB.get(folder_key, 500)
                actual_kb = prod_path.stat().st_size / 1024
                if actual_kb > budget_kb:
                    size_over_budget.append(
                        f"{prod_path_rel}: {actual_kb:.0f} KB > {budget_kb} KB budget"
                    )

            # Check PNG fallback if declared
            png_fallback = entry.get("pngFallback")
            if png_fallback:
                png_rel = png_fallback.lstrip("/")
                png_path = PUBLIC_ROOT / png_rel
                if not png_path.is_file():
                    warnings.append(f"PNG fallback missing: {png_rel}")

    if missing_production:
        errors.append(f"{len(missing_production)} production files missing")
        for mp in missing_production[:20]:
            errors.append(f"  MISSING: {mp}")
    else:
        passed.append(f"All {len(present_production)} production WebP files present")

    if size_over_budget:
        for s in size_over_budget:
            warnings.append(f"SIZE OVER BUDGET: {s}")
    else:
        passed.append("All assets within file-size budgets")

    # 4. Master checksum verification (spot-check)
    masters_checked = 0
    masters_ok = 0
    if MASTERS_DIR.is_dir():
        for master_file in MASTERS_DIR.rglob("*"):
            if not master_file.is_file():
                continue
            fname = master_file.name
            manifest_entry = next((a for a in assets if a["filename"] == fname), None)
            if manifest_entry and manifest_entry.get("sha256"):
                masters_checked += 1
                actual = sha256_file(master_file)
                if actual == manifest_entry["sha256"]:
                    masters_ok += 1
                else:
                    errors.append(
                        f"Master checksum mismatch: {fname} "
                        f"expected {manifest_entry['sha256'][:16]}… "
                        f"got {actual[:16]}…"
                    )
    if masters_checked > 0:
        passed.append(f"Master checksums: {masters_ok}/{masters_checked} verified")

    # 5. Check responsive variants (populated by optimize step)
    responsive_found = 0
    if registry_path.is_file():
        for entry in reg_assets:
            variants = entry.get("responsiveVariants", [])
            for v in variants:
                vpath = PUBLIC_ROOT / v.get("path", "").lstrip("/")
                if vpath.is_file():
                    responsive_found += 1
                else:
                    warnings.append(f"Responsive variant missing: {v.get('path', '?')}")
    if responsive_found > 0:
        passed.append(f"{responsive_found} responsive variants verified")

    # 6. Dimension validation via Pillow (if available)
    try:
        from PIL import Image
        dim_checked = 0
        dim_ok = 0
        for entry in reg_assets:
            prod_rel = entry.get("productionPath", "").lstrip("/")
            prod_path = PUBLIC_ROOT / prod_rel
            if not prod_path.is_file():
                continue
            expected = entry.get("dimensions", {})
            ew, eh = expected.get("width", 0), expected.get("height", 0)
            if ew == 0 or eh == 0:
                continue
            dim_checked += 1
            with Image.open(prod_path) as img:
                aw, ah = img.size
            # WebP may differ slightly from source if responsive; check master dims
            # For the base WebP, width/height should match source (no resize yet)
            if aw == ew and ah == eh:
                dim_ok += 1
            elif aw <= ew and ah <= eh:
                dim_ok += 1  # optimized smaller is fine
            else:
                warnings.append(
                    f"Dimension mismatch: {prod_rel} "
                    f"expected {ew}x{eh}, got {aw}x{ah}"
                )
        if dim_checked:
            passed.append(f"Dimensions: {dim_ok}/{dim_checked} match or smaller")
    except ImportError:
        warnings.append("Pillow not available — skipping dimension checks")

    return _result(errors, warnings, passed)


def _result(errors, warnings, passed):
    ok = len(errors) == 0
    result = {
        "valid": ok,
        "errors": errors,
        "warnings": warnings,
        "passed": passed,
    }

    report_path = ROLLBACK_DIR / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    status = "PASS" if ok else "FAIL"
    print(f"\n{'='*60}")
    print(f"VALIDATION {status}")
    print(f"{'='*60}")
    for p in passed:
        print(f"  [OK] {p}")
    for w in warnings:
        print(f"  [WARN] {w}")
    for e in errors:
        print(f"  [ERR] {e}")
    print(f"\n{len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")
    print(f"Report: {report_path}")

    if not ok:
        sys.exit(1)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate Bhāva brand assets")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    result = validate()
    if args.strict and result.get("warnings"):
        print(f"\n--strict mode: {len(result['warnings'])} warnings treated as errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
