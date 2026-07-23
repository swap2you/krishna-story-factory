# Python Test Execution — Bhāva Portal V1 UAT

Environment: Python 3.10.12 venv built fresh in the review sandbox (real Windows workstation
`.venv` is Python 3.13.5 — see report Environment section), dependencies installed from
`requirements.txt` plus `fastapi`, `httpx`, `sqlalchemy` for the portal API.

## Portal API tests — `tests/portal` (mission-critical for this UAT)

```
PYTHONPATH=apps/api pytest tests/portal -q
8 passed in 19.91s
```

All 8 tests in `test_api_read_only.py`, `test_catalog_discover_stories.py`, and
`test_package_hash_guard.py` passed, including the disabled-factory, path-traversal, and
content-type-fallback assertions cited in `api_health_and_safety_evidence.md`.

*Note:* on first attempt, all 3 tests in `test_api_read_only.py` failed with
`sqlite3.OperationalError: disk I/O error`. This was traced to SQLite being opened on the
network-mounted repository path, which does not support SQLite's locking model in this sandbox —
not an application defect. Re-run with the derived catalog DB redirected to local disk (repo
`output/` content unchanged) passed cleanly. This should not occur on the native Windows
workstation, which uses a local NTFS volume.

## Legacy Krishna Story Factory suite — `tests/` (excluding `tests/portal`)

`pytest --collect-only` reported **218 tests collected** in total (210 outside `tests/portal`).
Executed in batches to stay inside the sandbox's per-command execution window:

| Batch | Files | Result |
|---|---|---|
| 1 | test_activity_semantic_qa, test_adaptive_components, test_audio_sanitize, test_audio_waveform, test_caption_drive, test_coloring_blockers, test_csv_queue | 49 passed |
| 2 | test_final_repair_reliability, test_master_plan, test_matching_coverage | 29 passed |
| 3 | test_prompt_normalize, test_pronunciation_and_package_v2, test_quality_guards | 23 passed |
| 4 | test_release_artifacts_001_006, test_renee_rebuild_gates | 17 passed |
| 5 | test_story_005_activity_pack, test_story_format_v2, test_whatsapp_sender | 19 passed |
| 6 (partial) | test_openai_tts_fallback, test_pilot_release_hash_evidence, test_pipeline_test_mode | 18 passed before window elapsed |
| 7 (partial) | test_repetition, test_run_summary, test_runtime_state, test_scheduler_scripts | 9 passed before window elapsed |
| 8 (stalled) | test_daily_idempotency | 1 passed, did not complete in two attempts |

**Totals: 165 of ~210 legacy-suite tests executed to completion, 0 failures, 0 errors.**
Combined with the 8 portal tests: **173 tests passed, 0 failed, across everything this session
was able to run to completion.**

Not executed to completion in this session (not failed — simply did not finish inside the
sandbox's execution windows): the remainder of `test_openai_tts_fallback.py`,
`test_pilot_release_hash_evidence.py`, `test_pipeline_test_mode.py`,
`test_post_pr7_release_blockers.py`, `test_pr7_blocker_repairs.py`, the remainder of
`test_repetition.py`, `test_run_summary.py`, `test_runtime_state.py`,
`test_scheduler_scripts.py`, and `test_daily_idempotency.py` (this file alone did not produce a
second passing dot within 40s on two separate attempts and should be profiled for runtime).
Recommend a full native run via `scripts\test_all.ps1` to close this out.

## Frontend unit tests (`vitest`), typecheck, build

**Not executed.** `npm install` could not complete for `apps/web` in this sandbox (see
`00_METHODOLOGY_AND_LIMITATIONS.md`). `apps/web/components/story-grid.test.tsx` and
`apps/web/test/setup.ts` exist in the repository, so a `test:web` target does exist — it simply
could not be run here.

## Lint

**Not executed — and not claimed as PASS.** `scripts/test_bhava.ps1` itself does **not** call
`npm run lint:web` at any point (verified by reading the script), so lint has never been part of
the gated test pack even on the native workstation. `apps/web/eslint.config.mjs` exists and
`package.json` defines a `lint` script, so tooling is present; it has simply never been wired
into the automated test pack. See defect list.

## Dependency warnings

`npm install` in the real repository (exact command from the mission) fails outright with:

```
npm error code EBADPLATFORM
npm error notsup Unsupported platform for @next/swc-win32-x64-msvc@15.3.5: wanted {"os":"win32","cpu":"x64"} (current: linux/x64)
```

`pip install -r requirements.txt` produced no dependency conflicts once given enough time in this
sandbox (openai, google-api-python-client, pandas, numpy, pillow, reportlab, mutagen, miniaudio,
pypdfium2, imageio-ffmpeg, PyYAML all resolved cleanly).

## Secret scan

`git grep` for API-key-shaped patterns across all tracked files returned exactly one hit:
`tests/test_final_repair_reliability.py:146-147`, which is a **unit test asserting that
`sanitize_error_text` redacts a fake key** (`sk-proj-ABCDEFGHIJKLMNOPQRSTUV`) — a positive
control, not a leaked credential. `.env` is git-ignored and not tracked; only `.env.example`
(all blank/`false` placeholder values) is tracked. `credentials/` is git-ignored and not tracked.
