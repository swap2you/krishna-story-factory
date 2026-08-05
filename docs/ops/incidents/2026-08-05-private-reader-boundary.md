# P0 Incident — Private Reader Public Boundary

**Recorded (UTC):** 2026-08-05T17:54:28Z  
**Starting develop:** `6cf260d4792201d6fc66ea0ccc2f2375b242d1f8`  
**Production main:** `c25973d29c200e7a4911c61b4c8d6b652cda0076`

## Pre-containment probe (no body content logged)

| URL | HTTP | Length | Content-Type | SHA-256 |
|-----|------|--------|--------------|---------|
| `/api/v1/stories/021/reader` | 200 | 10568 | text/markdown | C2B68DDC…CE3D4 |
| `/api/v1/stories/021/reader.txt` | 200 | 10708 | text/plain | 91227FAB…7796 |
| `/api/v1/stories/022/reader` | 200 | 10347 | text/markdown | 833AB1D7…BF5E4 |
| `/api/v1/stories/022/reader.txt` | 200 | 10483 | text/plain | 684E31C9…9386 |
| `/api/v1/stories/020/reader` | 200 | 10109 | text/markdown | 31C614BC…F114 |
| `/stories/021` | 404 | — | — | — |
| `/api/v1/stories/021` | 404 | — | — | — |

## Root cause

`apps/api/bhava_api/routes/reader.py` served `reader.md` / `reader.txt` from
`web_assets_root` **before** `_get_story_record()`, bypassing the indexed catalog
ceiling on the shared content mount.

## Permanent fix

Catalog-first resolution for both reader handlers; production-only Caddy
defense-in-depth for private reader API paths; production smoke hardening.

## P2 follow-up (not in this P0)

Story 021 `narration_source_sha` metadata discrepancy vs shipped audio — do not
modify locked package manifests during this incident.
