# Story 008 Partial Run Forensics — 2026-07-24

## Summary

The 10:00 MWF production run **started Story 008**, generated valid `story.md` and `narration.mp3`, then **aborted at the start of poster generation**. The abort was caused by the scheduled PowerShell runner treating Python **stderr warnings as terminating errors** (`$ErrorActionPreference = "Stop"` + `*>&1 | Tee-Object`). The process was killed before `finally: release_pipeline_lock`, leaving:

1. Stale `.pipeline.lock` (timestamp `2026-07-24T10:00:03`)
2. Queue row `008` stuck in `processing` (attempts=1)
3. Incomplete folder in public `output/008_the-meeting-of-nanda-and-vasudeva/`
4. 12:00 backup failing in ~3s on `RuntimeError: Another pipeline run appears to be in progress (.pipeline.lock exists).`
5. Task Scheduler `LastTaskResult = 1` for both runs

This is **not** a finished Story 008 release. Artifacts were moved to a recovery workspace; public `output/` no longer contains the partial package.

## Scheduled task configuration (before repair)

Captured in `docs/operations/SCHEDULER_V1_5_CONFIGURATION_BEFORE.xml`.

| Field | Value |
|-------|--------|
| TaskName | Krishna Story Factory MWF |
| Action | `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ...\scripts\run_daily_story_scheduled.ps1 -ProjectRoot ...` |
| WorkingDirectory | repo root |
| Triggers | Mon/Wed/Fri 10:00 and 12:00 |
| MultipleInstancesPolicy | IgnoreNew |
| ExecutionTimeLimit | PT1H |
| RestartOnFailure | 2 × PT30M |
| StartWhenAvailable | false (installer) |
| LogonType | InteractiveToken |
| WHATSAPP/TELEGRAM | forced false in runner |
| GOOGLE_DRIVE_UPLOAD_ENABLED | true in runner |

## Stage timeline (10:00 run)

| Stage | Status | Evidence |
|-------|--------|----------|
| queue claim | complete | `tracking/queue_state.csv` → 008 `processing` at 10:00:12 |
| story generation | complete | `story.md` mtime 10:03:23, 16114 bytes, title/chapter OK |
| story validation | complete | Source guard passed (file written) |
| narration chunking | complete | `.narration_chunks/chunk_001.mp3`, `chunk_002.mp3` |
| narration assembly | complete | `narration.mp3` 5,612,995 bytes, **350.76s**, mtime 10:04:21 |
| poster generation | **first failing stage** | Warning logged: `Poster reference image not found; continuing without reference.` then runner abort; no poster file |
| detailed/simple coloring | not reached | |
| activity / caption / manifest | not reached | |
| package QA / atomic publish | not reached | |
| catalog refresh | N/A (incomplete package; catalog requires exact eight) | |
| Drive upload | not reached | |
| queue completion | **not done** — left `processing` | |

Exact first failing mechanism: **PowerShell NativeCommandError on Python stderr**, not an uncaught Python exception from poster generation itself. The warning is non-fatal in Python (`logging.warning` in `images/generator.py`).

## 12:00 backup

| Item | Value |
|------|--------|
| Duration | ~3.4 seconds |
| Log | `logs/scheduler/daily_20260724_120002.log` |
| Failure | Traceback → lock already held by stale `.pipeline.lock` |
| Generation | none |

## Preserved recovery workspace

```text
work/stories/008/20260724-100002/
  story.md
  narration.mp3
  .narration_chunks/
  pipeline_work_45eb48df7fa8/   # empty candidate dirs from aborted poster start
  RECOVERY_MANIFEST.json
```

Public path `output/008_the-meeting-of-nanda-and-vasudeva/` was removed after copy so the final output namespace does not retain a partial package.

## Reuse decision

| Artifact | Valid? | Action |
|----------|--------|--------|
| story.md | yes (Story 008 / Nanda–Vasudeva / Krishna Book Ch.5) | lock and reuse — do not regenerate |
| narration.mp3 | yes (~5.8 min MP3) | lock and reuse — do not regenerate |
| images/PDF/caption/manifest | missing | generate only after Phase 1 repair + explicit recovery enablement |

## Root-cause chain

1. **Primary:** `scripts/run_daily_story_scheduled.ps1` uses `$ErrorActionPreference = "Stop"` and pipes native stderr through PowerShell, converting harmless Python warnings into terminating `NativeCommandError`, aborting mid-run and returning exit code 1.
2. **Secondary:** `acquire_pipeline_lock` has no PID/staleness reclaim; killed runs leave permanent locks.
3. **Tertiary:** Production `_run_once` writes directly into `output/`, so partial packages land in the public namespace before atomic publish.
4. **Quaternary:** Interrupted `processing` queue rows are not auto-recovered; `read_next_pending` skips them, so 12:00 cannot resume 008 even after lock cleanup without manual repair.

## Required repairs (Phase 1)

1. Capture Python exit code without treating stderr as terminating.
2. PID + stale-lock reclaim; reset stuck `processing` safely.
3. Stage state machine + staging directory outside public `output/`.
4. Atomic promote only after exact-eight validation.
5. 12:00 idempotent resume / successful no-op when complete.
6. Runbook + post-repair scheduler XML export.
