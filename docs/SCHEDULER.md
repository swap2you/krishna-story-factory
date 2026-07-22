# Scheduler — Krishna Story Factory MWF

## Task

| Field | Value |
| --- | --- |
| Name | `Krishna Story Factory MWF` |
| Days | Monday, Wednesday, Friday |
| Times | **10:00 AM** primary and **12:00 PM** backup (local Windows timezone) |
| Triggers | Six weekly triggers (MO/WE/FR × 10:00 and 12:00) |
| Action | `scripts/run_daily_story_scheduled.ps1` via PowerShell |
| Entry | `.venv\Scripts\python.exe run_daily_story.py --mode prod` |
| Drive | Forced `GOOGLE_DRIVE_UPLOAD_ENABLED=true` for the run |
| WhatsApp / Telegram | Forced `false` for the run |
| Overlap | `MultipleInstances = IgnoreNew` |
| StartWhenAvailable | **False** (missed day does not fire on next boot) |
| WakeToRun | **False** |
| Limit | 60 minutes (`PT1H`) |
| Retry | 2 × every 30 minutes (`PT30M`) — resume/fail only; does **not** bypass same-day guard |
| `--force` | Never |

Legacy task `Krishna Story Factory Daily` must not stay enabled alongside MWF.

## Same-day duplicate protection (mandatory)

Production mode without `--force` refuses a second successful story on the same calendar day (`SKIPPED_ALREADY_COMPLETED_TODAY` / equivalent).

Expected behavior:

1. If the **10:00 AM** run succeeds, the **12:00 PM** trigger exits cleanly as a same-day no-op (no generation, no paid APIs, no Drive upload, no queue advance).
2. If 10:00 is missed because the PC is off, **12:00** may generate the story if the PC is awake.
3. If both triggers are missed, do **not** run later merely because the PC starts (`StartWhenAvailable=False`).
4. Try again on the next scheduled Monday, Wednesday, or Friday.
5. Never create two stories on the same calendar day.

One queue-driven story per successful day.

## Install

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
# Install Disabled (safe default):
.\scripts\install_mwf_story_task.ps1
# Install and enable; also removes legacy Daily if present:
.\scripts\install_mwf_story_task.ps1 -Enable -RemoveLegacyDaily
```

## Verify

```powershell
.\scripts\test_mwf_story_task.ps1
Get-ScheduledTask -TaskName "Krishna Story Factory MWF" | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName "Krishna Story Factory MWF" | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult
```

Static-only (no Task Scheduler query):

```powershell
.\scripts\test_mwf_story_task.ps1 -StaticOnly
```

## Disable / remove

```powershell
Disable-ScheduledTask -TaskName "Krishna Story Factory MWF"
Unregister-ScheduledTask -TaskName "Krishna Story Factory MWF" -Confirm:$false
```

Re-running `install_mwf_story_task.ps1` without `-Enable` re-registers the task in **Disabled** state.

## Logs

- `logs/scheduler/daily_*.log` (runner keeps recent logs)  
- `tracking/run_history.csv`  
- Optional `tracking/latest_run_summary.json` / `logs/latest_run_summary.txt`

Senior devotee review remains pending for the 001–006 pilot lock. The MWF task is the production schedule once enabled (`-Enable`); do not leave the legacy Daily task enabled alongside it.
