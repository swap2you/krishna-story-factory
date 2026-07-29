# Bhāva V1.6 — SHA-bound matrix summary

| Field | Value |
|-------|-------|
| Tested SHA | `1fae6d89a5578a94a7376dd4b3cd386bb7a19724` |
| Short SHA | `1fae6d8` |
| Branch | `feature/bhava-portal-v1` |
| Instance | `cursor-v16` @ http://127.0.0.1:3003 (API :8000) |
| Captured | see `metadata.json` |

## Results

| Gate | Exit | Notes |
|------|------|-------|
| pytest (`not slow`) | 0 | 392 passed, 5 deselected |
| lint:web | 0 | |
| typecheck:web | 0 | |
| test:web (vitest) | 0 | 2 passed |
| build:web | 0 | |
| Playwright (all projects) | 0 | **415 passed, 10 skipped, 0 failed** |

## Skips (justified)

All 10 skips are intentional iOS WebKit autoplay-policy skips for audio interaction tests on `webkit-mobile`:

- `e2e/v14-audio-all-stories.spec.ts` — Stories 001–008 play advancement (8)
- `e2e/v12-audio-routes.spec.ts` — play + modal arrow isolation (2)

Safari/iOS hardware remains a manual checklist item; Chromium/Firefox/WebKit desktop and Chromium mobile audio assertions passed.

## Safety spot-check (same tip)

- Stories 001–008 file SHA-256: **match** `BHAVA_V1_6_SAFETY_BASELINE.json`
- `tracking/queue_state.csv` SHA-256: **match** baseline
- Story 009 queue status: **pending**

## Cross-links

- Contrast: `docs/product/uat/v1.6/contrast/DEF_CONTRAST_01_BEFORE_AFTER.md`
- Design audit: `docs/product/uat/v1.6/design/PAGE_SECTION_AUDIT.md`
- Story 008 tabs: `docs/product/uat/v1.6/story-008/FULL_TAB_UAT.md`
- Scheduler: `docs/operations/SCHEDULER_V1_6_*`
- Drive: `docs/operations/STORY_008_DRIVE_RECONCILIATION.md`
- Lighthouse: `docs/product/uat/v1.6/performance/LIGHTHOUSE_BASELINE.md`
- Live notes: `docs/product/uat/v1.6/live/LIVE_UAT_NOTES.md`
