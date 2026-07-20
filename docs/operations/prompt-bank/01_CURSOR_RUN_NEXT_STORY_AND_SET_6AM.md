You are the autonomous operator for:

C:\Development\Workspace\DevotionalRepo\krishna-story-factory

Goal:
Generate exactly one next-pending Krishna Book story from scratch, validate its complete seven-file package, upload it to its own Google Drive folder, advance the queue exactly once, and change the existing Windows scheduled task to run every morning at 6:00 AM local time.

Do not ask the user to run terminal commands.
Do not send WhatsApp or Telegram.
Do not expose secrets.
Do not use `--force`.
Do not create a second story in the same calendar day.
Do not commit generated content or runtime state.
Own all commands, repairs, validation, Git checks, and scheduler updates.

Current expected state:
- `main` matches `origin/main`.
- Stories 001–004 are complete.
- Story 005 is next pending.
- Google Drive upload is enabled.
- Scheduler exists and is enabled.
- Scheduler currently runs at 5:30 AM and must be changed to 6:00 AM.
- WhatsApp and Telegram are disabled.

## 1. Preflight

1. Switch to `main`.
2. Pull latest `origin/main`.
3. Confirm working tree is clean.
4. Use repository interpreter only:
   `.\.venv\Scripts\python.exe`
5. If `.venv` is missing, run the repository bootstrap script.
6. Run full tests using the repository test wrapper.
7. Confirm:
   - master plan has 93 episodes;
   - Krishna Book Chapters 1–90 are covered;
   - Story 005 is next pending;
   - Drive upload is enabled;
   - WhatsApp disabled;
   - Telegram disabled;
   - no process lock remains;
   - no story has already completed today.

If a story already completed today:
- do not generate another story;
- validate the existing latest package;
- continue only with scheduler update and final reporting.

## 2. Daily idempotency

Verify or implement a hard normal-run guard:

- At most one successful production story per local calendar day.
- `--force` or explicit component rebuild may override, but normal scheduler/manual prod cannot.
- The guard must use runtime state or `tracking/run_history.csv`, not Git history.
- If a second same-day normal run is attempted, exit successfully with:
  `SKIPPED_ALREADY_COMPLETED_TODAY`.
- Add tests if this guard is missing.
- Do not alter the static master plan.

## 3. Generate the next story

Run the normal production pipeline once:

`.\.venv\Scripts\python.exe run_daily_story.py --mode prod`

Expected:
- Story 005 is selected.
- Stories 001–004 are not regenerated.
- The pipeline performs its own bounded repair loops.
- The run creates exactly seven final files.
- The package is uploaded to a new per-story Drive folder.
- Story 005 becomes done.
- Story 006 becomes next pending.

If a correctable component fails:
- repair only that component;
- rerun within bounded attempts;
- continue until PASS.

If an external service quota blocks completion:
- stop cleanly;
- leave Story 005 pending;
- do not upload a partial package;
- report the exact service and required action.

## 4. Validate every final artifact

Validate actual files, not just manifest claims.

### story.md
- source-faithful to Story 005 boundaries;
- no later pastimes;
- no invented scripture quotation;
- age 6–12 readability;
- coherent recap, main story, moral, takeaway, challenge, parent note, bedtime reflection;
- no repeated paragraphs or padded ending;
- source references present.

### narration.mp3
- real playable MP3;
- ElevenLabs source;
- no placeholder audio;
- no spoken performance tags;
- no repeated closing;
- no clipping or accidental silence;
- duration and size recorded;
- Sanskrit names reasonably pronounced.

### story_poster.png
- real image;
- story-specific;
- readable title and one-line summary;
- no malformed key anatomy;
- correct characters and roles;
- no modern objects;
- devotional and child-safe;
- visual QA threshold met.

### coloring_page.png
- real line art;
- poster/story identity preserved;
- correct character ages and roles;
- no wrong iconography;
- no cropped primary figures;
- clean black-and-white printable lines;
- large colorable spaces;
- visual QA threshold met.

### activity_sheet.pdf
- dynamic, story-specific ActivityPack;
- 2–4 pages unless the chosen type justifies one page;
- not a generic worksheet;
- no blank or nearly blank pages;
- no raw JSON/Python dictionary text;
- locally rendered labels;
- age-level variants or multi-level engagement;
- no embedded `coloring_page.png`;
- activity QA threshold met;
- answer key hidden in manifest when applicable.

### whatsapp_caption.txt
- uses the per-story Drive folder link;
- reflects activity send mode;
- does not claim WhatsApp was sent;
- parent-friendly and concise.

### manifest.json
- exactly seven final filenames;
- correct episode metadata;
- correct Drive folder ID/link;
- correct audio/image/activity QA metrics;
- correct queue transition;
- no intermediate/debug filenames;
- no secrets.

## 5. Validate Google Drive

1. Open/list the created Story 005 Drive folder.
2. Confirm exactly these seven filenames:
   - story.md
   - narration.mp3
   - story_poster.png
   - coloring_page.png
   - activity_sheet.pdf
   - whatsapp_caption.txt
   - manifest.json
3. Confirm no raw candidates, prompt files, debug reports, or intermediates.
4. Confirm folder permissions are appropriate for sharing/viewing.
5. Confirm manifest and caption use this exact folder link.

## 6. Scheduler update to 6:00 AM

Update the existing task:

`Krishna Story Factory Daily`

Requirements:
- daily at 6:00 AM local time;
- current Windows user;
- enabled;
- uses repository venv Python;
- runs `run_daily_story.py --mode prod`;
- no `--force`;
- working directory is repository root;
- `IgnoreNew` overlap prevention;
- 60-minute execution timeout;
- retry twice at 30-minute intervals;
- start when available if missed;
- scheduler logs under `logs/scheduler/`;
- WhatsApp disabled;
- Telegram disabled;
- Drive enabled.

Do not manually trigger the scheduled task after changing it.

Verify:
- task state is Ready;
- next run is the next 6:00 AM;
- command and arguments are correct.

## 7. Git and main

A production run must leave Git clean because runtime/output files are ignored.

- Do not commit Story 005 package.
- Do not commit runtime CSV rows.
- If code fixes were required, commit only source/tests/docs/scripts on a new branch and open a PR.
- Do not push direct code changes to `main`.
- If no code changed, do not create a pointless commit.
- Confirm `main` remains clean and aligned with `origin/main`.

## 8. Final report

Print:

KRISHNA STORY FACTORY — DAILY RUN COMPLETE

Tests:
Daily Guard:
Generated Story:
Story Source Boundary:
Local Seven Files:
Drive Folder:
Drive Seven Files:
Story Words:
Audio Duration:
Audio Size:
Poster QA:
Coloring QA:
Activity Type:
Activity Pages:
Activity QA:
Queue Transition:
Next Pending:
Scheduler Time:
Scheduler Enabled:
Next Scheduled Run:
WhatsApp:
Telegram:
Git Working Tree:
Overall:

Valid results:
- PASS
- SKIPPED_ALREADY_COMPLETED_TODAY
- BLOCKED_EXTERNAL_SERVICE
- BLOCKED_QUALITY_FAILURE

Do not report PASS unless generation, validation, Drive upload, queue advance, scheduler update, and clean Git state all pass.
