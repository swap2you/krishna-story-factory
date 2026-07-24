# 01 — Git / SHA / Runtime Validation

**Reviewer:** Independent CoWork UAT (Claude, non-interactive session)
**Branch:** `feature/bhava-portal-v1`
**Date:** 2026-07-24

## Branch SHA

- Mission-specified branch SHA: `b51c0a877ee654207f146b3b19d8179f7a3ee620`
- Independently verified `git rev-parse HEAD`: `b51c0a877ee654207f146b3b19d8179f7a3ee620`
- **Match: CONFIRMED**

## Product (tested) SHA

- Mission-specified tested SHA: `fe57b4661712845b12bf313ea46321d71723c1bb`
- Independently verified via `git rev-parse fe57b46` and `git log -1 --format=%H fe57b46`: `fe57b4661712845b12bf313ea46321d71723c1bb`
- **Match: CONFIRMED**

## Commit distance (evidence-only after product SHA)

```
b51c0a8 test: attach Bhava v1.5 Playwright and pytest evidence logs
ef63e47 test: complete Bhava v1.5 full release validation
fe57b46 fix(audio): fall back to native MP3 when blob playback is unsupported   <- tested/product SHA
```

HEAD is exactly two commits ahead of the tested product SHA, and both intervening commits are test/evidence commits (`test:` prefix, `docs/product/uat/...` and log payloads only). This matches the mission's expectation ("exactly two documentation/evidence commits ahead of the product-code SHA"). No application code changed after `fe57b46`.

## Minor documentation discrepancy (non-blocking)

`docs/releases/BHAVA_V1_5_RELEASE_CANDIDATE.md` states:

> **Tested SHA:** `fe57b46fbb273b9689cadb59c663fd0992d9a983`

This full 40-character SHA does **not** exist in the repository and does not match the real commit. The short form `fe57b46` happens to match by abbreviation coincidence, but the full string in that document is incorrect. The mission-provided full SHA (`fe57b4661712845b12bf313ea46321d71723c1bb`) is the one that is real and independently verified above.

- Severity: P3 (documentation accuracy only; does not affect runtime, safety, or release content)
- Recommended correction: fix the full SHA string in `BHAVA_V1_5_RELEASE_CANDIDATE.md` to `fe57b4661712845b12bf313ea46321d71723c1bb`.

## Runtime instance

Read from `.bhava/instances/cursor-v15/runtime.json` and cross-checked against `docs/product/uat/v1.5/runs/20260724-181701-fe57b46/run-metadata.json`:

| Field | Value |
|---|---|
| Instance name | cursor-v15 |
| Web URL | http://127.0.0.1:3005 |
| API URL | http://127.0.0.1:8003 |
| Web PID | 3352 |
| API PID | 123980 |
| Mode | production |
| Preferred ports | 3000 / 8000 (collision=true, fell back to 3005/8003) |

Instance was healthy at connection time; the existing cursor-v15 instance was reused per mission instruction (no new instance started, so no instance was stopped at the end of this review).

## Verdict for this section

**CONFIRMED.** Branch SHA, product SHA, and runtime instance all match mission expectations. One non-blocking documentation typo noted above.
