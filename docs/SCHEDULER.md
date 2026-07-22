# Scheduler — Krishna Story Factory MWF

## Task

| Field | Value |
| --- | --- |
| Name | `Krishna Story Factory MWF` |
| Days | Monday, Wednesday, Friday |
| Time | 06:00 local |
| Action | `scripts/run_daily_story_scheduled.ps1` via PowerShell |
| Entry | `.venv\Scripts\python.exe run_daily_story.py --mode prod` |
| Drive | Forced `GOOGLE_DRIVE_UPLOAD_ENABLED=true` for the run |
| WhatsApp / Telegram | Forced `false` for the run |
| Overlap | `MultipleInstances = IgnoreNew` |
| Limit | 60 minutes |
| Retry | 2 × every 30 minutes |
| `--force` | Never |

Legacy task `Krishna Story Factory Daily` must not stay enabled alongside MWF.

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

Senior devotee review is pending for the 001–006 lock; enable the task only when operations intentionally start MWF production.
