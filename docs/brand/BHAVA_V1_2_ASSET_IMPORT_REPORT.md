# Bhāva V1.2 Asset Import Report

**Date:** 2026-07-23  
**Pipeline:** `import_bhava_brand_assets.py` → `optimize_bhava_brand_assets.py` → `validate_bhava_brand_assets.py`

## Summary

| Metric | Value |
|--------|-------|
| Manifest total | 122 |
| Imported | 114 |
| Missing | 8 (Phase 5 canto covers) |
| Checksum failures | 0 |
| Validation | PASS (0 errors, 11 warnings) |

## Production File Counts

| Folder | WebP | PNG | AVIF | Notes |
|--------|------|-----|------|-------|
| `brand/` | 20 | 13 | 14 | Logos + contact heroes; PNG kept for RGBA transparency |
| `heroes/` | 28 | 0 | 10 | 10 base + 18 responsive |
| `collections/` | 57 | 0 | 19 | 19 base + 38 responsive (covers + 4 cantos) |
| `sections/` | 41 | 0 | 12 | 12 base + 29 responsive |
| `social/` | 18 | 0 | 10 | 10 base + 8 responsive |
| `icons/` | 38 | 38 | 38 | 22 learning + 11 platform + 5 contact-FAQ icons |
| `empty-states/` | 11 | 11 | 11 | All with RGBA PNG fallback |

## Derivatives Generated

- **Responsive WebP:** 98 variants at 640w, 1280w, 1920w breakpoints
- **Favicon/PWA:** 7 derivatives (`favicon-16/32/48.png`, `apple-touch-icon.png`, `pwa-192/512.png`, `og-icon-256.png`)
- **OG default:** `social/og-default-1200x630.webp`
- **AVIF:** 114 (all imported assets)

## Size Budget Warnings

These assets exceed their category WebP budget. They were imported anyway (warn-only policy):

| Asset | Actual | Budget |
|-------|--------|--------|
| `brand/logo-primary-horizontal.webp` | 787 KB | 500 KB |
| `brand/logo-compact-horizontal.webp` | 573 KB | 500 KB |
| `brand/logo-stacked.webp` | 877 KB | 500 KB |
| `brand/logo-icon-only.webp` | 555 KB | 500 KB |
| `icons/browser-pinned-tab-1024.webp` | 81 KB | 50 KB |
| `icons/social-profile-avatar-2048.webp` | 105 KB | 50 KB |
| `heroes/hero-text-free-master.webp` | 381 KB | 300 KB |
| `sections/section-caitanya.webp` | 307 KB | 300 KB |
| `sections/section-contact.webp` | 301 KB | 300 KB |
| `social/social-podcast-cover.webp` | 603 KB | 400 KB |

Oversized logos are expected — high-res transparent PNGs compress larger in WebP. The responsive 640w/1280w variants will be used for most UI contexts.

## Key Paths

- **Registry:** `apps/web/config/brand-assets.json`
- **Manifest reference:** `docs/brand/consolidated_manifest.json`
- **Masters:** `.bhava/brand-import/masters/` (gitignored)
- **Rollback evidence:** `.bhava/brand-import/` (gitignored)
- **Reports:** `.bhava/brand-import/{import,validation,optimization}_report.json`

## Blockers

See `docs/releases/BHAVA_V1_2_ASSET_IMPORT_BLOCKERS.md` for the 8 missing Phase 5 canto covers.
