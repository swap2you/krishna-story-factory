# Krishna Story Factory — Automation and Governance Final Report

## Release state

- Initial branch: `fix/adaptive-activities-and-character-lineart`
- Final branch: `fix/adaptive-activities-and-character-lineart`
- Pull request: https://github.com/swap2you/krishna-story-factory/pull/1 (draft)
- Merge: not attempted because the required Story 003 production gate did not pass
- Overall status: `BLOCKED_EXTERNAL_SERVICES`

## Commits created

- `bad5ea2` — normal revert of accidental runtime-only commit `da22fa3`
- `72e574e` — separate runtime queue state from static plan
- `c0a4c0c` — source guards, captions, reflections, and episode boundaries
- `f313808` — complete Krishna Book master series plan
- `492b085` — unattended Windows scheduler scripts
- `a4f8ae4` through `35108e2` — production-found Story 003 guard, repair, metadata, and activity hardening

The valid implementation commit `b7a0032` remains in history. No force push was used.

## Static plan and runtime state

Tracked static metadata lives in `input/krishna_book_master_plan.csv` and
`input/series_plan.csv`. Mutable status, attempts, errors, completion time, and Drive folder IDs live
in ignored `tracking/queue_state.csv`. All runtime logs under `tracking/*.csv` are ignored; tracked
header-only examples live in `tracking/templates/`.

Queue migration result: Story 001 done, Story 002 done, Story 003 pending, Story 004 pending. Static
plans remain unchanged during normal execution, and runtime files are no longer tracked.

## Existing package repairs

Story 001 now uses the source-aligned message received in Brahma's heart, includes the required
reflection, uses optional activity wording, and links to its actual story folder:
https://drive.google.com/drive/folders/1_7R1uj_WtW0CfuhfMAz_d3FSF1zsHbo-?usp=sharing

Story 002 now identifies Kamsa as Devaki's brother and Ugrasena's son, includes the required
reflection, uses weekend-project wording, and links to its actual story folder:
https://drive.google.com/drive/folders/1pr9ZMwnzE8bx7mgreAguduQFDzc8XC0V?usp=sharing

Both narrations were regenerated with ElevenLabs. Only `story.md`, `narration.mp3`,
`whatsapp_caption.txt`, and `manifest.json` were replaced. Each remote folder was verified to contain
exactly seven final files. Approved posters, coloring pages, and activity PDFs were not regenerated.

## Master plan and source governance

The master plan contains 93 unique episodes and covers every Krishna Book chapter from 1 through 90.
Story 003 is **Vasudeva Keeps His Word**, bounded to SB 10.1.56–61. Story 004 covers Narada's warning
and the imprisonment decision and was not generated.

Generation now constructs a source-fact brief, feeds source failures into repair, enforces required
reflections, and runs a post-generation boundary guard. Story 003 additionally has a deterministic
source-boundary sanitizer and a six-event, source-specific truthfulness activity path; neither bypasses
the normal source, quality, audio, activity, coloring, or poster gates.

## Validation

- Tests: 70 passed
- Required `pytest -q`: passed
- Required `python run_daily_story.py --mode test --force`: passed
- Master-plan validation: 93 episodes, Chapters 1–90 covered, next active episode 003
- Story 001/002 non-regeneration check during Story 003 attempts: hashes unchanged
- Scheduler static validation: passed
- Tracked-file policy: no `.env`, credentials, generated media, output packages, or runtime CSV rows
- Secret review: only documented placeholders and credential field names were found; no secret values
  are tracked
- Git working tree before this report: clean

## Story 003 production result

Story 003 did **not** complete and was not uploaded. It remains pending. Production attempts failed
closed while hardening source and activity quality. The final external failure was ElevenLabs quota:
1,549 credits remained while 1,619 were required for the validated narration. Earlier activity QA
scores of 18–28 exposed generic placeholders; those were replaced by a source-specific activity and
covered by tests, but paid production QA could not be rerun after the narration quota failure.

- Story 003 Drive link: none
- Next pending episode: Story 003, not Story 004
- No process lock remains

## Scheduler and delivery

Task scripts configure `Krishna Story Factory Daily` for the current user at 5:30 AM local time with
start-when-available, `IgnoreNew`, a 60-minute timeout, two retries at 30-minute intervals, explicit
venv Python, scheduler logging, and runtime history. The command never uses `--force`.

The task is not installed or enabled because the release contract prohibits installation before Story
003 production passes. Therefore, next scheduled run is not available.

- WhatsApp: disabled
- Telegram: disabled
- Google Drive: enabled for production
- Pilot delivery recommendation: Google Drive generation only

## Exact rollback procedure

1. If the task is installed after this blocker is cleared, run
   `powershell -ExecutionPolicy Bypass -File scripts/remove_daily_story_task.ps1`.
2. Preserve ignored `tracking/queue_state.csv` outside the repository.
3. Revert the eventual merge commit with `git revert <merge-sha>`; do not force-push.
4. If reverting individual branch commits instead, revert newest to oldest through `72e574e`, retaining
   `bad5ea2` unless intentionally restoring the accidental runtime commit.
5. Restore the preserved runtime queue file if needed. Never commit it or the runtime logs.

## Remaining blockers

1. Replenish or reset ElevenLabs quota sufficiently for a validated 3–6 minute narration.
2. Rerun `python run_daily_story.py --mode prod`; require all Story 003 gates and exact-seven Drive
   verification to pass.
3. Mark the draft PR ready, verify checks, squash-merge, then install and validate the scheduled task.

## Required summary

```text
KRISHNA STORY FACTORY — AUTOMATION FINAL

Tests: PASS (70)
Runtime State Migration: PASS
Story 001 Repair: PASS
Story 002 Repair: PASS
Master Series Plan: PASS (93 episodes)
Krishna Book Chapters Covered: 1-90
Story 003: BLOCKED — ElevenLabs quota; remains pending
Story 003 Drive: NOT CREATED
Next Pending: 003 — Vasudeva Keeps His Word
Git Working Tree: CLEAN before final report commit
Pull Request: https://github.com/swap2you/krishna-story-factory/pull/1 (draft)
Merge: NOT ATTEMPTED — production gate failed
Scheduled Task: NOT INSTALLED — production gate failed
Next Scheduled Run: N/A
WhatsApp: DISABLED
Telegram: DISABLED
Overall: BLOCKED_EXTERNAL_SERVICES
```
