# Scheduler V1.7 — Safe validation

## Commands

```powershell
.\scripts\run_daily_story_scheduled.ps1 -ValidateScheduler
.\scripts\run_daily_story_scheduled.ps1 -SimulateProduction
```

## Results

| Mode | Exit | Queue unchanged | Provider calls | Drive | Heartbeat |
|------|------|-----------------|----------------|-------|-----------|
| `-ValidateScheduler` (pwsh + PS 5.1) | 0 | yes | 0 | none | process probe OK |
| `-SimulateProduction` | 0 | yes | 0 | none | `tracking/scheduler_health.json` written |

## Wrapper

- Version: `v1.7.0-dotnet-process`
- Launch: `System.Diagnostics.Process` with `UseShellExecute=false`, `CreateNoWindow=true`, redirected stdout/stderr via `ReadToEndAsync`
- No `Start-Process` / `NoNewWindow` on the production child path

## Notes

Validation never invokes `--mode prod`, providers, Drive upload, or Story 009 generation.
Simulate selects next pending story (`009`) read-only and uses `.pipeline.validate.lock`.
