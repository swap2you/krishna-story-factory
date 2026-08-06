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

## Temporary containment

| Item | Value |
|------|--------|
| Pre-containment | Four private reader routes HTTP **200** (2026-08-05T17:54:28Z) |
| Containment run | https://github.com/swap2you/krishna-story-factory/actions/runs/31036248800 |
| Method | Production-only Caddy `handle` denies (V2) before `handle /api/*` |
| Post-containment | 021/022 reader(+.txt) → **404**; 020 reader → **200** |
| Staging | Unaffected |

## Permanent production closure

| Item | Value |
|------|-------|
| Hotfix PR | https://github.com/swap2you/krishna-story-factory/pull/52 |
| Hotfix commit | `55babab819d4a7055d91cdedb3022a8092105374` |
| Develop merge | `76adbd777aed72bb981f8bb3a0df15cba45f55ba` (later tip `134c130…` after sync) |
| Promote PR | https://github.com/swap2you/krishna-story-factory/pull/56 |
| Main merge / LKG | `72eb171991102831da5d3993b5e2ad48447556d7` |
| Staging deploy | https://github.com/swap2you/krishna-story-factory/actions/runs/31038086192 (`76adbd7…`) |
| Production deploy | https://github.com/swap2you/krishna-story-factory/actions/runs/31042276803 (`72eb171…`) |
| CoWork verdict | PASS WITH NON-BLOCKING FINDINGS |

Post-production `/api/v1/version`: `environment=production`, `release_sha=72eb171…`,
`content_tag=bhava-content-001-020-v4`, `public_story_max=20`, `indexed_story_count=20`.

Post-production reader matrix: 020 md/txt **200**; 021/022/023 md/txt **404**;
pages 021/022/023 **404**; assets 021/022 **404**; sitemap excludes 021/022.

Re-verified 2026-08-05 evening (pre Story 023 recovery / 001–022 publish work):
021/022/023 page+API+reader+assets remain **404**; sitemap excludes 021–023;
`release_sha` still `72eb171…`; content still `bhava-content-001-020-v4` / max 20.

Committed production Caddy `@private_reader_api` handle deny is live with this
release (defense-in-depth). Temporary server-only incident patch is superseded
by committed config — do not leave undocumented server-only denies.

**New last-known-good baseline:** `72eb171…` (not `24a4904`; that target is
incompatible with the shared-content architecture).

## Related scheduler miss (Wed 2026-08-05)

Task **did run** at 10:00 AM local (`LastTaskResult=1`). Root cause: pronunciation
coverage FAIL before TTS — missing lexicon entry for **Tālavana**
(`logs/scheduler/daily_20260805_100002.log`). No paid full narration charged.
Story 023 remains pending with locked `story.md` under
`work/stories/023/20260805-100013-744694`.

## P2 follow-up (not in this P0)

Story 021 `narration_source_sha` metadata discrepancy vs shipped audio — do not
modify locked package manifests during this incident.
