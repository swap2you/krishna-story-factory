# Scheduler V1.7.1 — Install validation

## Re-register

```powershell
.\scripts\install_mwf_story_task.ps1 -Enable -RemoveLegacyDaily
```

| Check | Result |
|-------|--------|
| Product SHA | `86d43f1d64e2ac738e68b5d1c7f0182b8b5c41d5` |
| Installer exit | 0 |
| `test_mwf_story_task.ps1` | PASS |
| Task state | Ready (enabled) |
| ExecutionTimeLimit | PT4H |
| StartWhenAvailable | true |
| StopOnIdleEnd | false |
| MultipleInstances | IgnoreNew |
| Triggers | 6 (MWF 10:00 + 12:00) |
| WakeToRun | false (explicit policy) |
| Action | `scripts\run_daily_story_scheduled.ps1` |
| WorkingDirectory | repository root |
| NextRunTime | 2026-07-29 10:00:00 |
| Final XML | `docs/operations/SCHEDULER_V1_7_1_CONFIGURATION_FINAL_ENABLED.xml` |
| XML contains `<Enabled>false</Enabled>` | **no** |

Installer source now fully reproduces the accepted production task without manual post-install edits.


Note: Windows Export-ScheduledTask for an enabled Ready task may omit the <Enabled> element entirely. This export contains **no** <Enabled>false</Enabled>. Live state = Ready.

