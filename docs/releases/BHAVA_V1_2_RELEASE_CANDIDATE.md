# Bhāva Portal V1.2 — Release Candidate Record

**Branch:** `feature/bhava-portal-v1`  
**Date:** 2026-07-23  
**Authoritative contract:** `MyPilotDropbox/bhava-v1.2-release/BHAVA_V1_2_CURSOR_MASTER_RELEASE_PROMPT.md`

## Candidate status

**BLOCKED for “READY FOR FINAL COWORK UAT”** until the approved Phase-5 recreated canto covers (1–7, 10) are supplied and imported. All other V1.2 phases completed on this branch with factory safety preserved.

## Delivered

| Area | Outcome |
| --- | --- |
| Safety baseline | `docs/releases/BHAVA_V1_2_SAFETY_BASELINE.json` — Stories 001–007 hashes, queue `008=pending` |
| Brand pipeline | Import/validate/optimize scripts; `apps/web/config/brand-assets.json`; 114/122 WebP assets |
| DEF-06 audio | Server waveform peaks; `play()` from click path; Playwright confirms `currentTime` advances (desktop Chromium/Firefox/WebKit) |
| DEF-07 keyboard | Player shortcuts ignore dialogs/inputs; modal arrows do not seek audio |
| Preachers | Client outline selection, Print, TXT export |
| Contact / About / FAQ | Steward identity + Harrisburg; mailto + copy fallback |
| Prayers / Printables / Nav | Honest planned taxonomy; live asset hub; Studio out of public nav |
| Future stories | Isolated fixtures only (`tests/portal/test_v12_future_story_fixtures.py`) |
| Dropbox hygiene | Release zip under `MyPilotDropbox/_processed/` (gitignored) |
| Reviews | Security, Codex technical, Claude adversarial, parent/teacher |

## Blockers (P0 brand)

Documented in `docs/releases/BHAVA_V1_2_ASSET_IMPORT_BLOCKERS.md`:

- Missing approved files from `bhava-brand-assets-v1-phase5-recreated-complete.zip` (cantos 1–7, 10).
- Master prompt forbids READY while the approved asset package is incomplete.

## Factory invariants (unchanged)

- Stories 001–007 packages not regenerated
- Real Story 008 not created
- Queue / scheduler / Drive / paid APIs not invoked
- `KrishnaBook.pdf` and `MyPilotDropbox/` not tracked
- No PR / merge / main / tags modified

## CoWork handoff

- Final SHA: use `git rev-parse HEAD` on `feature/bhava-portal-v1` (docs freeze base `a9adc03c52fe1da9a79b273a22a498ae23d7f85e`)
- Final prompt: `docs/reviews/BHAVA_V1_2_FINAL_COWORK_UAT_PROMPT.md`
- UAT evidence root: `docs/product/uat/v1.2/`
- Live instance during Cursor UAT: `cursor-v12` → http://127.0.0.1:3004 / http://127.0.0.1:8002
