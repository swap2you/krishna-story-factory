# Scheduler V1.6 — Registered task audit

**Task:** `Krishna Story Factory MWF`  
**Captured:** 2026-07-27T12:25:41.3647928Z

## Action

- Command: `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`
- Arguments: `-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Development\Workspace\DevotionalRepo\krishna-story-factory\scripts\run_daily_story_scheduled.ps1" -ProjectRoot "C:\Development\Workspace\DevotionalRepo\krishna-story-factory"`
- Points at fixed Start-Process wrapper (`run_daily_story_scheduled.ps1`): **True**

## Triggers / policy

See `SCHEDULER_V1_6_CONFIGURATION.xml` and `SCHEDULER_V1_6_TASK_RAW.txt` for full export (MWF 10:00/12:00, account, no-overlap, retry).

## Honest production success observation

- Pre-repair 2026-07-24 10:00 failed (stderr abort).
- Safe validation mode proves registration/wrapper health but **does not** prove a post-repair scheduled production success has been observed.
- Actual post-repair scheduled production success observed: **no** (not claimed).

## Artifacts

- `SCHEDULER_V1_6_CONFIGURATION.xml`
- `SCHEDULER_V1_6_VALIDATION_RUN.md` (after validate)
