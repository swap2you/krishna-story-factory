# Expected Daily Behavior

At 6:00 AM local time:

1. Windows Task Scheduler starts `Krishna Story Factory Daily`.
2. The runner uses the repository `.venv`.
3. It runs `run_daily_story.py --mode prod`.
4. The daily guard permits at most one successful normal production story per local calendar day.
5. It selects exactly one next-pending episode.
6. It generates and validates the eight final files.
7. Only after quality PASS does it create the story-specific Drive folder.
8. It uploads exactly eight files.
9. It writes the Drive link into caption and manifest.
10. It marks the episode done and advances once.
11. It leaves Git clean.
12. WhatsApp and Telegram remain disabled.
13. The user manually sends the caption/link.

Generated packages must never be pushed to Git main. Only code, tests, prompts, scripts, and documentation belong in Git.
