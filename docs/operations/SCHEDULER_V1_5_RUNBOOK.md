# Scheduler V1.5 Runbook

## Purpose

Keep Mon/Wed/Fri 10:00 primary and 12:00 backup production **atomic, resumable, and idempotent**.

## Safe behaviors

| Situation | Expected result | Exit code |
|-----------|-----------------|-----------|
| Next pending story, no prior success today | Start or resume missing stages only | 0 on success |
| Successful package already completed today | No-op skip (`SKIPPED_ALREADY_COMPLETED_TODAY`) | 0 |
| Partial prior run with locked story/narration | Resume only after `--enable-production-recovery` or `BHAVA_ENABLE_PRODUCTION_RECOVERY=1` | 0 on success; non-zero if recovery not enabled |
| Concurrent second instance | `MultipleInstances=IgnoreNew`; lock rejects live peer | ignored / 1 |
| Stale `.pipeline.lock` (dead PID / aged) | Reclaimed; stuck `processing` → `pending` | continues |
| Incomplete folder in `output/` | Quarantined under `work/stories/_quarantine_incomplete/` | continues |
| Python stderr warnings | Logged; **do not** abort the runner | Python exit code only |

## Commands

Validate task wiring:

```powershell
.\scripts\test_mwf_story_task.ps1
```

Reinstall schedule (does not enable unless `-Enable`):

```powershell
.\scripts\install_mwf_story_task.ps1 -Enable
```

Manual no-upload dry path is still `run_daily_story.py --mode test`.

Story 008 recovery (explicit only):

```powershell
$env:BHAVA_ENABLE_PRODUCTION_RECOVERY = "1"
.\.venv\Scripts\python.exe run_daily_story.py --mode prod --chapter 008 --resume-from work\stories\008\20260724-100002 --enable-production-recovery
```

## Evidence files

- Before: `docs/operations/SCHEDULER_V1_5_CONFIGURATION_BEFORE.xml`
- After: `docs/operations/SCHEDULER_V1_5_CONFIGURATION_AFTER.xml`
- Forensics: `docs/operations/STORY_008_PARTIAL_RUN_FORENSICS.md`

## Operator notes

1. Never delete reusable `story.md` / `narration.mp3` under `work/stories/008/`.
2. Public `output/` must contain only exact-eight packages.
3. `LastTaskResult` must be `0` only for success or intentional no-op.
4. Do not re-enable paid generation for locked stages.
