# Bhāva Brand Asset Lock V1

**Status:** LOCKED  
**Date:** 2026-07-23  
**Manifest:** `docs/brand/consolidated_manifest.json` (122 approved assets)  
**Registry:** `apps/web/config/brand-assets.json`

## Scope

This lock covers all 122 visual assets from the Bhāva Devotional Learning brand asset pipeline (Phases 1–10). Assets were approved through multi-phase QA documented in the consolidated manifest.

## Locked Asset Categories

| Category | Count | Production Folder | Format |
|----------|-------|-------------------|--------|
| Logo System | 12 | `brand/` | WebP + PNG (RGBA) |
| Platform Icons | 11 | `icons/` | WebP + PNG |
| Homepage Heroes | 10 | `heroes/` | WebP |
| Collection Covers | 15 | `collections/` | WebP |
| Canto Covers | 12 | `collections/` | WebP |
| Section Banners | 12 | `sections/` | WebP |
| Social Sharing | 10 | `social/` | WebP |
| Learning Icons | 22 | `icons/` | WebP + PNG (RGBA) |
| Empty States | 11 | `empty-states/` | WebP + PNG (RGBA) |
| Contact/FAQ | 7 | `brand/` + `icons/` | WebP |

## Import Status

- **Imported:** 114 / 122
- **Missing:** 8 (Phase 5 canto covers — see `docs/releases/BHAVA_V1_2_ASSET_IMPORT_BLOCKERS.md`)

## Naming Convention

All production assets use deterministic lowercase-kebab names:
- Logos: `logo-{variant}.webp` (e.g. `logo-primary-horizontal.webp`)
- Heroes: `hero-{purpose}.webp` (e.g. `hero-desktop-wide.webp`)
- Collections: `collection-{title}.webp` (e.g. `collection-krishna-book.webp`)
- Cantos: `collection-canto-{nn}.webp` (e.g. `collection-canto-01.webp`)
- Sections: `section-{purpose}.webp` (e.g. `section-featured.webp`)
- Social: `social-{platform-or-purpose}.webp`
- Icons: `icon-{purpose}.webp`
- Empty states: `empty-{state}.webp`

## Derivatives Generated

- **Responsive variants** at 640w, 1280w, 1920w for heroes, collections, banners, social (98 total)
- **Favicon/PWA:** `favicon-16.png`, `favicon-32.png`, `favicon-48.png`, `apple-touch-icon.png`, `pwa-192.png`, `pwa-512.png`, `og-icon-256.png`
- **AVIF:** Generated alongside WebP for all 114 assets
- **OG derivative:** `social/og-default-1200x630.webp`

## Rollback

Masters and rollback evidence stored under `.bhava/brand-import/` (gitignored). Import, validation, and optimization reports available there.

## Modification Policy

Do NOT modify locked assets without explicit review approval. Any changes must go through the brand asset pipeline with updated manifest checksums.
