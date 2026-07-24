# 11 — Scheduler Operations ("Krishna Story Factory MWF")

## Sandbox limitation (disclosed up front)

This review runs in a Linux sandbox with bash + Claude-in-Chrome only — there is no Windows PowerShell / Task Scheduler access available. `Get-ScheduledTask`, `Get-ScheduledTaskInfo`, and `Export-ScheduledTask` **could not be executed against the live Windows Task Scheduler** from this environment. All findings below are either (a) independent static/source verification, performed by this reviewer, or (b) independent analysis of on-disk operational log evidence — not a live query of the registered task object itself.

## (a) Configuration verified — independent static check

The product ships its own self-test, `scripts/test_mwf_story_task.ps1`, which supports a `-StaticOnly` mode specifically for environments without live Task Scheduler access (this reviewer's exact situation). Rather than merely reading that script and trusting its narrative, its assertions were **independently re-implemented and re-run in this sandbox** via direct `grep` checks against the actual current file contents of `scripts/run_daily_story_scheduled.ps1` and `scripts/install_mwf_story_task.ps1`:

| Assertion (mirrors `test_mwf_story_task.ps1`'s static checks) | Result |
|---|---|
| Runner uses `Start-Process` (so stderr warnings are non-terminating) | OK |
| Runner does NOT use `Tee-Object` (the historical abort-causing pattern) | OK |
| Runner redirects stderr separately via `RedirectStandardError` | OK |
| Runner invokes the venv Python (`.venv\Scripts\python.exe`) | OK |
| Runner uses safe production args (`--mode prod`, no `--force`) | OK |
| WhatsApp send disabled (`WHATSAPP_SEND_ENABLED = "false"`) | OK |
| Telegram send disabled (`TELEGRAM_SEND_ENABLED = "false"`) | OK |
| Drive upload enabled by default (`GOOGLE_DRIVE_UPLOAD_ENABLED = "true"`) | OK |
| Installer sets no-overlap policy (`MultipleInstances IgnoreNew`) | OK |
| Installer sets retry policy (`RestartCount 2`, `Minutes 30`) | OK |
| Installer wires primary 10:00 trigger | OK |
| Installer wires backup 12:00 trigger | OK |
| `StartWhenAvailable = $false` | OK |
| `WakeToRun = $false` | OK |
| Monday / Wednesday / Friday all wired | OK |
| Task name `Krishna Story Factory MWF` present | OK |

**All 16 independently-reproduced static assertions pass.** This is genuine independent verification of the intended configuration, not a restatement of prior claims.

## (b) Actual scheduled-run history — independent log analysis (important finding)

`tracking/run_history.csv` (local-only, correctly `.gitignore`d — not expected to be repo-tracked) and `logs/scheduler/*.log` were read directly. Today (2026-07-24) is a Friday, an MWF trigger day. The real run history shows:

| Timestamp | Result | Detail |
|---|---|---|
| 2026-07-24T10:00:02 | **FAILED** | `python.exe : Poster reference image not found...` error surfaced via the **old** `Tee-Object -FilePath ...` pattern at `run_daily_story_scheduled.ps1:23` |
| 2026-07-24T12:00:02 | **FAILED** | `python.exe : Traceback...` again via the **old** `Tee-Object` pattern at the same line |
| 2026-07-24T12:44:20 | FAILED | Manual attempt: "production recovery is not enabled" (missing `--enable-production-recovery` flag) |
| 2026-07-24T12:46:17 | FAILED | Manual attempt, same recovery-flag error |
| 2026-07-24T12:47:01 → 12:55:32 | **SUCCESS** | Story 008 produced. Detail: **"Upload disabled by flag."** |

Corresponding on-disk log files `logs/scheduler/daily_20260724_100002.log` and `daily_20260724_120002.log` were read directly and confirm the same `Tee-Object -FilePath $Lo...` line-23 error signature for both the 10:00 and 12:00 entries.

## Interpretation — distinguishing configuration vs. execution vs. observed outcome, as the mission requires

1. **Configuration verified:** Yes — independently, via static source re-check (above). The current runner script (`run_daily_story_scheduled.ps1`) genuinely no longer contains `Tee-Object` and genuinely uses `Start-Process` + `RedirectStandardError`, exactly matching its own code comment's stated fix rationale ("Critical: do NOT pipe native stderr through PowerShell's error stream... was aborting the 2026-07-24 Story 008 run... leaving a stale `.pipeline.lock`").

2. **The two real scheduled firings visible in this log evidence (10:00 and 12:00 on 2026-07-24, the actual MWF trigger times) both ran the OLD, pre-fix version of the script** — both failed with exactly the `Tee-Object`/stderr-abort bug the fix addresses. This is strong, independent confirmation that (a) the scheduler's triggers are real and genuinely fire on schedule (10:00 primary + 12:00 backup, matching the installer's design) and (b) the historical bug narrative in the code comment is accurate and log-evidenced, not just asserted.

3. **The eventual Story 008 success (12:47–12:55) does not appear to be a scheduled-task-triggered run.** It occurred 45 minutes after the 12:00 scheduled failure, was preceded by two manually-flagged recovery attempts referencing command-line flags (`--enable-production-recovery` / `BHAVA_ENABLE_PRODUCTION_RECOVERY`), and its own detail ("Upload disabled by flag") differs from the scheduled runner's default (`GOOGLE_DRIVE_UPLOAD_ENABLED = "true"`). This pattern is consistent with a **manual/direct invocation of `run_daily_story.py`** (the underlying Python entry point) rather than a Task-Scheduler-triggered run of the wrapper script.

4. **Therefore: an actual post-repair scheduled production run, triggered by the real Windows Task Scheduler and using the current fixed script, has not been observed in the evidence available to this review.** The fix is source-verified-correct and the historical failure is log-confirmed, but there is no log entry showing the *fixed* script running via a genuine MWF trigger and succeeding (or even running and failing for an unrelated reason) — only the pre-fix script's two real scheduled failures, followed by an out-of-band manual recovery.

## Recommendation (non-blocking for this release, since Story 008 itself is verified correct and safely gated — see file 10)

Before relying on the scheduler unattended for Story 009 and beyond, confirm one genuine end-to-end scheduled success: either wait for the next Mon/Wed/Fri 10:00 or 12:00 trigger, or manually trigger the registered task once (`Start-ScheduledTask -TaskName "Krishna Story Factory MWF"`) and confirm via `Get-ScheduledTaskInfo`'s `LastTaskResult` that the *current* script completes and uploads successfully end-to-end without manual intervention. This is a real Windows Task Scheduler action outside this sandbox's reach and was not performed by this review.

## Verdict for this section

**PASS WITH NON-BLOCKING NOTES.** Configuration is independently verified correct. Scheduler triggers are independently confirmed to be real and active (two genuine firings observed today). The specific pre-fix failure mode is log-confirmed. However, a genuine post-repair scheduled success has not yet been observed — this is an open operational item to close out before the next unattended run, not a release blocker for the v1.5 product/UAT itself.
