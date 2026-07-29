# Codex Technical Review — Bhāva Portal V1.5

**Branch:** `feature/bhava-portal-v1`  
**Tested SHA:** `fe57b46`  
**Date (UTC):** 2026-07-24

## Scope

Factory scheduler recovery, Story 008 atomic publish, catalog freshness, audio playback machine, portal redesign surfaces, Knowledge gates, CI-aligned pytest + Playwright.

## Findings

| Severity | Finding | Status |
|----------|---------|--------|
| P0 | Partial Story 008 left in public `output/` after scheduled abort | Closed — quarantine + staging + atomic publish |
| P0 | Scheduler PowerShell stderr abort | Closed — Start-Process runner |
| P0 | Audio no advancement (DEF-06) / WebKit blob unsupported | Closed — blob-first + native MP3 fallback |
| P1 | Catalog incomplete packages discoverable | Closed — publish gates + exact-eight |
| P1 | Homepage bedtime-only positioning | Closed — platform tagline + audiences |
| P2 | Mobile vanani assertion hit hidden nav link | Closed — heading assertion |

## Technical notes

- Staging under `work/stories/` with `atomic_replace_package_dir` prevents incomplete public exposure.
- Audio: Chromium/Firefox use blob prefetch; Playwright WebKit marks blob unsupported (`MEDIA_ERR_SRC_NOT_SUPPORTED`) and plays allowlisted `narration.mp3` in-gesture.
- Exact-eight + `publishable` + quality PASS required before catalog inclusion.

## Verdict

**Pass for CoWork UAT** — no open P0/P1 on tested SHA.
