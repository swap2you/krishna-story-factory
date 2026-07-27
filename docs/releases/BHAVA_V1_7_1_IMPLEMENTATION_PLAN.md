# Bhāva V1.7.1 — Implementation Plan

## Mission

Repair reproducibility and SHA-bound evidence contradictions after V1.7 product success:

1. Remove mutable `tracking/scheduler_health.json` from Git.
2. Align `install_mwf_story_task.ps1` and validators with the accepted PT4H / `.NET Process` task.
3. Re-register the enabled task from source without production generation.
4. Prove same-day no-op `LastTaskResult=0` without Story 010.
5. Capture complete raw pytest + Playwright logs for one exact product SHA, then commit evidence only.

## Starting state (reconciled)

| Item | Value |
|------|-------|
| Branch | `feature/bhava-portal-v1` |
| Starting SHA | `df1dcf029dd57b6c46c0662661a9125edbcaaa7d` |
| Origin match | yes (ff-only pull) |
| Differs from `223d29f` | yes — tip adds tracked `tracking/scheduler_health.json` + `docs/operations/SCHEDULER_20260727_EVENTS_RAW.json` |
| Prior product matrix SHA | `72a3ff19daa3a506015222c7c316dd6294fc8b6d` |
| Prior evidence SHA | `223d29fee82061b53095cd8fb1fafb4df46310fc` |
| main | `3bae97850ef8b934bbec3a48f42f92fbe6de169f` (unchanged) |
| Tags | unchanged (`v1.0.0-pilot-stories-001-006`, `v1.1.0-stories-001-007-operational`, backup tag) |

## Hard constraints

- Do not modify Stories 001–009, generate 010, mutate queue, call providers, mutate Drive, open PR, or merge.
- Only safe ValidateScheduler / SimulateProduction and same-day no-op on the registered task.

## Phases

| Phase | Work |
|-------|------|
| 0 | Reconcile tip; freeze safety baseline |
| 1 | Untrack health telemetry; gitignore |
| 2 | Installer PT4H / StartWhenAvailable / StopOnIdleEnd |
| 3 | Validators + pytest require `.NET Process` and registered-task checks |
| 4 | Re-register enabled task; export final XML |
| 5 | Validate + Simulate + temp probe + real no-op |
| 6 | Product SHA → full matrix raw logs → evidence-only commit |
| 7 | Story 009 / portal read-only validation |
| 8–9 | Release candidate + CoWork prompt |
| 10 | Final safety gate |

## WakeToRun decision

`WakeToRun = false` — matches the accepted V1.7 registered configuration and is not authorized to wake the machine for story generation.
