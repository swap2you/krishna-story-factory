# Bhāva V1.7.1 — Release Candidate

## Identity

| Field | Value |
|-------|-------|
| Starting branch SHA | `df1dcf029dd57b6c46c0662661a9125edbcaaa7d` |
| Product SHA | `86d43f1d64e2ac738e68b5d1c7f0182b8b5c41d5` |
| Evidence commit | *(this docs commit after matrix)* |
| Final branch SHA | *(evidence tip after push)* |
| Branch | `feature/bhava-portal-v1` |

## Why V1.7.1

V1.7 published Story 009 and repaired the scheduler launch path, but the tip later tracked mutable `tracking/scheduler_health.json`, the installer still encoded PT1H / `StartWhenAvailable=false`, and validators still required `Start-Process`. Raw final matrix logs were also not bound to one exact product SHA.

## Scheduler source ↔ registered task

| Setting | Installer source | Registered task | Match |
|---------|------------------|-----------------|-------|
| Process | `.NET System.Diagnostics.Process` | wrapper unchanged | yes |
| Start-Process / NoNewWindow | forbidden | not used | yes |
| ExecutionTimeLimit | PT4H | PT4H | yes |
| StartWhenAvailable | true | true | yes |
| StopOnIdleEnd | false | false | yes |
| MultipleInstances | IgnoreNew | IgnoreNew | yes |
| Restart | 2 / 30m | 2 / 30m | yes |
| Triggers | MWF 10:00 + 12:00 (6) | 6 | yes |
| WakeToRun | false (explicit) | false | yes |

Final enabled XML: `docs/operations/SCHEDULER_V1_7_1_CONFIGURATION_FINAL_ENABLED.xml` (no `<Enabled>false</Enabled>`).

## Validation / no-op

| Gate | Result |
|------|--------|
| `-ValidateScheduler` | exit 0 |
| `-SimulateProduction` | exit 0 |
| Temp Task Scheduler probe | LastTaskResult **0** |
| Real registered same-day no-op | LastTaskResult **0** (`SKIPPED_ALREADY_COMPLETED_TODAY`) |
| Story 010 | pending / absent |

## Stories

| Item | State |
|------|-------|
| 001–008 | unchanged (manifest hashes frozen in safety baseline) |
| 009 | exact-eight, publishable true, quality PASS |
| 010 | pending / hidden |
| Queue | unchanged during repair |
| Drive | read-only review only |

## Testing (exact product SHA)

Evidence: `docs/product/uat/v1.7.1/runs/20260727-130534-86d43f1/`

| Suite | Result |
|-------|--------|
| pytest `-m "not slow"` | **417 passed**, 5 deselected, 0 failed |
| Playwright (5 projects) | **415 passed**, 10 skipped, 0 failed |
| lint / typecheck / unit / build | exit 0 |

Raw logs: `pytest-full.txt`, `playwright-full.txt` (not summary-only).

## Known limitations

- Safari/iOS WebKit autoplay policy → 10 intentional Playwright skips on webkit-mobile audio assertions.
- Cost guard remains **advisory-only** (`openai_tts_monthly_budget_usd_advisory`); not a hard spend cap.
- Runtime `tracking/scheduler_health.json` is gitignored telemetry.

## Verdict

Ready for final CoWork UAT after evidence commit lands on origin.
