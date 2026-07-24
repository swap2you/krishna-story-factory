# Bhāva V1.4 — Logo Lock

## Problem found in V1.3 live UI

`logo-small-header.webp` is the approved **wide** header wordmark (3600×520). The app rendered it as a **44×44** rounded crop (`object-fit: cover`), which destroyed the mark and made the logo appear incorrect.

## Canonical checksums (from `apps/web/config/brand-assets.json`)

| Variant | Production path | SHA-256 |
|---------|-----------------|---------|
| primary horizontal | `/brand/logo-primary-horizontal.webp` | `8be35441f3a073b66dc5dc91940ca6edf33e76854d2d9327e0bf281468eb181e` |
| compact horizontal | `/brand/logo-compact-horizontal.webp` | `27ef8c6a720a06be88d885609b5935697131b39ab1cff47de5a4ba907636d074` |
| small header | `/brand/logo-small-header.webp` | see brand-assets.json `logo-small-header` |
| icon-only | `/brand/logo-icon-only.webp` | see brand-assets.json |
| dark background | `/brand/logo-dark-bg.webp` | see brand-assets.json |

## Locked application mapping

| Surface | Asset | Notes |
|---------|-------|-------|
| Desktop/tablet header | `logo-small-header.webp` | True aspect; height 32px; alt `bhāva` |
| Mobile header | `logo-icon-only.webp` + live HTML wordmark `bh`+`ā`+`va` | Macron preserved in live text |
| Footer | `logo-dark-bg.webp` | Dark variant |
| Favicon/PWA | icon-only / platform icons | Unchanged contract |

## Comparison page

Local-only: `/dev/logo-sheet` (not in primary nav).

## Spelling

Public wordmark spelling is **bhāva** (macron on ā). Live typography is authoritative when raster text is ambiguous.
