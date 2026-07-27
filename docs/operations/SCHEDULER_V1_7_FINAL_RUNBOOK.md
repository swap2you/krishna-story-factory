# Scheduler V1.7 — Final runbook

## Registered task

- Name: `Krishna Story Factory MWF`
- Wrapper: `scripts/run_daily_story_scheduled.ps1` (`v1.7.0-dotnet-process`)
- Limits: `ExecutionTimeLimit=PT4H`, `MultipleInstances=IgnoreNew`, `StartWhenAvailable=true`, `StopOnIdleEnd=false`
- Triggers: MWF 10:00 primary + 12:00 backup

## Safe probes

```powershell
.\scripts\run_daily_story_scheduled.ps1 -ValidateScheduler
.\scripts\run_daily_story_scheduled.ps1 -SimulateProduction
```

## Heartbeat

`tracking/scheduler_health.json` (runtime; not committed)

## Incident reference

`docs/operations/SCHEDULER_20260727_INCIDENT_REPORT.md` — `0xC000013A` / NoNewWindow console-control class.
