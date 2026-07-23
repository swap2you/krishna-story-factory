# Bhāva Portal V1 — UAT Candidate

Status: **READY FOR COWORK LIVE REVIEW** on branch `feature/bhava-portal-v1` (no PR/merge in this cycle).

## Git

- Branch: `feature/bhava-portal-v1`
- Previous SHA: `6eb72c9f798b60d7435e91fe1b14a1d0b186d628`
- Final SHA: `89f1fc3b13fc7a32c507383c1f6455803c27d648`
- PR: none created
- `main` / `master` / tags: unchanged

## Dynamic runtime

- Instances: `default`, `cursor`, `cowork`, `codex`, `claude` (+ arbitrary names)
- Preferred examples: cursor 3000/8000, cowork 3001/8001, codex 3002/8002, claude 3003/8003
- Collision handling: search forward in range; never kill foreign processes
- Runtime file: `.bhava/instances/<name>/runtime.json`
- List: `.\scripts\list_bhava_instances.ps1`
- Native UAT instance kept running: `cursor-uat` @ http://127.0.0.1:3000 / http://127.0.0.1:8000

## Catalog

- Startup index + live refresh (15–30s) + public GET `refresh_if_stale()`
- Publish gates enforced for public inclusion
- Fixture coverage: `tests/portal/test_catalog_live_refresh.py` (11 portal tests pass)
- Real Story 008 generated: **NO**

## Defects DEF-01…DEF-13

All mapped **fixed** in `docs/reviews/BHAVA_V1_COWORK_UAT.md` closure table.

## Testing surface

- Portal API tests including live catalog refresh: PASS
- Frontend unit / lint / typecheck / build: PASS
- Playwright: **180 passed** (chromium/firefox/webkit desktop + chromium/webkit mobile)
- axe critical/serious checks on key routes: PASS
- CI: Python matrix + web matrix + Playwright Chromium fixtures

## Verdict

**READY FOR COWORK LIVE REVIEW**
