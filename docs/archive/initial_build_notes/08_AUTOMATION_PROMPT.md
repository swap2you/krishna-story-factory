# 08 Daily Automation Prompt

Add and validate local daily automation scripts.

Required scripts:
- `scripts/run_daily_story_windows.ps1`
- `scripts/run_tests.ps1`
- `scripts/create_task_scheduler_job.ps1`

Windows Task Scheduler approach:
- Use local venv.
- Run the CLI daily.
- Write logs under `logs/`.
- Do not create a daemon or service.

Deliverable: scripts are safe, readable, and documented in `docs/DAILY_AUTOMATION_GUIDE.md`.
