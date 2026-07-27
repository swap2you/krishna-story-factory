# Next real scheduled run checklist

1. Confirm task XML still points at `scripts\run_daily_story_scheduled.ps1` Start-Process wrapper.
2. Confirm queue: 008=done, 009=pending before run.
3. Confirm no stale `.pipeline.lock`.
4. Allow MWF 10:00 to claim 009 only when intentionally ready — **V1.6 forbids generating 009 during this stabilization**.
5. After any future real run: archive logs under `logs/scheduler`, verify exit 0, queue transition, Drive upload only if enabled.
6. 12:00 backup should no-op when day already complete.

Do not treat safe validation as historical production success.
