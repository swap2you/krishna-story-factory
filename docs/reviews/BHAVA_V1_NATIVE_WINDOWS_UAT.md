# Bhāva Portal V1 — Native Windows UAT

Date: 2026-07-23  
Branch: `feature/bhava-portal-v1`  
Previous SHA: `6eb72c9f798b60d7435e91fe1b14a1d0b186d628`  
Runtime: dynamic multi-instance via `scripts/start_bhava_local.ps1` + `scripts/bhava_runtime.py`

## Result

**PASS** — Playwright `180 passed` across chromium/firefox/webkit desktop + chromium/webkit mobile.

## Scope

Native Windows pass closing CoWork UAT conditions:

- Cross-platform npm install without mandatory win32 binaries (`optionalDependencies` + `scripts/ensure_native_optionals.cjs`)
- Collision-free instance ports (preferred ranges 3000–3099 / 8000–8099)
- Automatic catalog refresh with publish gates
- DEF-05…DEF-13 product fixes
- Playwright + axe evidence under `docs/product/uat/live/`

## Commands used

```powershell
.\scripts\stop_bhava_local.ps1 -AllInstances
npm ci
.\scripts\test_bhava.ps1   # optional full pack; portal+web smoke used during resume
.\scripts\run_bhava_uat.ps1 -InstanceName cursor-uat -PreferredWebPort 3000 -PreferredApiPort 8000 -KeepRunning
```

## Selected runtime

- Instance: `cursor-uat`
- Web: `http://127.0.0.1:3000`
- API: `http://127.0.0.1:8000`
- Mode: production
- Collision: false

## Automatic catalog behavior (production expectation)

When the Monday/Wednesday/Friday factory publishes a new exact-eight-file package under `output/`:

1. The API fingerprint notices the new/changed `manifest.json` within the 15–30s refresh window.
2. `refresh_if_stale()` re-indexes without mutating packages.
3. Public GET endpoints expose only publishable PASS packages.
4. Next.js force-dynamic catalog routes surface the story without a portal restart or code commit.
5. Incomplete, failed, or unpublished packages never appear on public routes.

Real Story 008 was **not** generated in this UAT.

## Safety

- Stories 001–007 present and untouched
- Queue unchanged; Story 008 remains pending
- Scheduler / Drive / paid APIs not invoked
- Factory Studio real actions remain disabled
- `main` / tags unchanged

## Evidence

See `docs/product/uat/live/` (`runtime.json`, `uat-summary.json`, axe/responsive/console/network placeholders, browser summary).
