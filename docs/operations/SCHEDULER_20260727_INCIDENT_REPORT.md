# Scheduler incident report — 2026-07-27 10:00

## Summary

| Field | Value |
|-------|-------|
| Task | `Krishna Story Factory MWF` |
| LastRunTime | 2026-07-27 10:00:00 |
| LastTaskResult (decimal) | `3221225786` |
| LastTaskResult (hex) | `0xC000013A` |
| Meaning | `STATUS_CONTROL_C_EXIT` — terminated by console-control/termination event |
| Public Story 009 | **none** |
| Queue 009 after incident | `pending`, attempts `0` |

## Registered configuration at incident (before repair)

| Setting | Value |
|---------|-------|
| Action | `powershell.exe -File ...\run_daily_story_scheduled.ps1 -ProjectRoot ...` |
| WorkingDirectory | repository root |
| LogonType | InteractiveToken |
| ExecutionTimeLimit | **PT1H** |
| MultipleInstancesPolicy | IgnoreNew |
| RestartOnFailure | 2 / PT30M |
| StartWhenAvailable | **false** |
| StopOnIdleEnd (IdleSettings) | **true** |
| DisallowStartIfOnBatteries | false |
| Wrapper child launch | `Start-Process ... -Wait -NoNewWindow` with stdout/stderr redirect |

## File evidence (cited)

1. `logs/scheduler/daily_20260727_100008.stdout.log` — created **2026-07-27 10:00:08**, **length 0**
2. `logs/scheduler/daily_20260727_100008.stderr.log` — created **2026-07-27 10:00:08**, **length 0**
3. No merged `daily_20260727_100008.log` — wrapper never reached post-process log merge / history append
4. `tracking/queue_state.csv` — chapter `009` still `pending`, `attempts=0`, empty `last_error` / `completed_at`
5. No `work/stories/009/` tree; no `.pipeline.lock` retained
6. Task Scheduler Operational log query for 09:30–12:30 returned **no matching events** in this environment (insufficient channel data; not treated as contradictory)

## Termination stage (evidence-based)

```text
inside wrapper after Start-Process opened redirect files,
before queue claim / before measurable Python generation progress
```

Rationale: redirect files exist (wrapper reached `Start-Process`), both streams empty, queue attempts unchanged, no stage/work artifacts, no merged daily log (wrapper `finally`/post-wait path did not complete cleanly under termination).

## Hypothesis evaluation

| Hypothesis | Assessment |
|------------|------------|
| `ExecutionTimeLimit=PT1H` killed a long run | **Unlikely as sole cause** — empty streams + `attempts=0` imply no long generation completed; limit remains a latent defect for future long runs |
| `-NoNewWindow` allowed console-control propagation | **Most probable** — matches `0xC000013A` semantics and observed Start-Process flags |
| User/session logoff / console shutdown | Possible contributor under InteractiveToken; not proven by retained OS events here |
| Cursor/PowerShell cleanup stopped parent | Possible; not proven |
| Task re-registered/stopped while active | No evidence in retained files |
| Noon trigger interference | Unlikely at 10:00 start; noon is separate trigger |
| Stale lock aborted child | No retained lock; queue untouched |
| Idle/power policy (`StopOnIdleEnd=true`) | Plausible contributor to hard stop; aligns with control-event class |
| Security software | Unresolved / no evidence |
| Wrapper exited but child remained | Empty redirects + task result control-exit argue tree termination, not clean wrapper exit |

## Root-cause classification

```text
most probable with evidence
```

**Conclusion:** The 10:00 action launched the V1.6 wrapper, which started Python via `Start-Process -NoNewWindow`. The process tree received a console-control/termination event (`0xC000013A`) before Story 009 was claimed or any generation output was flushed. Contributing registered defects: `-NoNewWindow` child path, `ExecutionTimeLimit=PT1H`, `StopOnIdleEnd=true`, `StartWhenAvailable=false`.

Do **not** claim “fixed” until Phases 3–6 replace the launch path, correct task limits, and prove validation/simulation/no-op results.
