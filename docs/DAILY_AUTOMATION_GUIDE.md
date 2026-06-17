# Daily Automation Guide

Use Windows Task Scheduler. Do not create a server.

## Script

Use:

```text
scripts/run_daily_story_windows.ps1
```

## Manual test

```powershell
.\scripts\run_daily_story_windows.ps1
```

## Create scheduled task manually

1. Open Task Scheduler.
2. Create Basic Task.
3. Name: `Krishna Story Factory Daily`.
4. Trigger: Daily.
5. Time: choose your morning time, for example 7:00 AM.
6. Action: Start a Program.
7. Program/script:

```text
powershell.exe
```

8. Arguments:

```text
-ExecutionPolicy Bypass -File "C:\path\to\krishna-story-factory\scripts\run_daily_story_windows.ps1"
```

9. Start in:

```text
C:\path\to\krishna-story-factory
```

## Daily send guard

The app blocks more than one sent story per day unless `--force` is used.

Use force only for testing:

```powershell
python run_daily_story.py --mode prod --force
```
