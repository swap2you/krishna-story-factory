# Event timeline — 2026-07-27 scheduler incident

| Time (local) | Source | Observation |
|--------------|--------|-------------|
| 08:26:13–08:26:14 | `logs/scheduler/validate_20260727_082613.log` | Prior V1.6 `-ValidateScheduler` exit 0 (safe) |
| 10:00:00 | Task Scheduler dynamic info | `LastRunTime` for `Krishna Story Factory MWF` |
| 10:00:08 | filesystem | `daily_20260727_100008.stdout.log` created (0 bytes) |
| 10:00:08 | filesystem | `daily_20260727_100008.stderr.log` created (0 bytes) |
| after 10:00:08 | absence | No merged `daily_*.log` for this stamp; no queue mutation; no `work/stories/009` |
| unknown exact kill time | Task result | `LastTaskResult=3221225786` (`0xC000013A`) recorded for the run |
| 10:25:07 | unrelated | `cursor-v16` API log write (portal instance; not story generation) |
| ~11:04 (repair freeze) | operator | Production task **Disabled** for V1.7 repair |

## Task Scheduler Operational channel

Query `Microsoft-Windows-TaskScheduler/Operational` for 09:30–12:30 returned no events in this session. Timeline therefore relies on task dynamic info + filesystem artifacts (explicitly noted).
