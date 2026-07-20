# Series plan governance

`input/krishna_book_master_plan.csv` is the complete editorial plan. `input/series_plan.csv` is the
CLI-ready static projection. Both are tracked and contain metadata only. Execution state belongs in
ignored `tracking/queue_state.csv`; other run evidence belongs in ignored `tracking/*.csv` files.

To add an episode, add a unique, chronologically placed row to the master plan, add the corresponding
static row to `series_plan.csv`, then run:

```powershell
.\.venv\Scripts\python.exe scripts\validate_master_plan.py
```

The next application run automatically adds a pending runtime queue row. Do not add `status`, attempts,
errors, timestamps, or Drive IDs to either static plan.

To disable an episode, set `enabled=false` in the master plan and remove it from the static projection.
If it already has local runtime state, leave that ignored history intact or mark it `disabled` in
`tracking/queue_state.csv`. Never commit the runtime file.

Activity history (`tracking/activity_history.csv`) is also runtime-only and gitignored. Preferred
ActivityPacks for early episodes are documented in [11_ACTIVITY_ENGINE_V2.md](11_ACTIVITY_ENGINE_V2.md);
do not mutate the static master plan to encode activity status.

