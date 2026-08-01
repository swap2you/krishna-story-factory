# Krishna Story Factory — Master Agent Prompt

Canonical engineering/operations handoff. Use this prompt instead of historical repair diaries.

## Before any work

1. Read `README.md`.  
2. Read `docs/PROJECT_SNAPSHOT_V1.md`.  
3. Read `docs/CONTENT_STANDARD.md` (and `input/content_quality_rules.md` if needed).  
4. Read the current queue: `tracking/queue_state.csv` (next `pending` only).  
5. Confirm Stories **001–006** are locked unless the operator gave explicit approval to change them.  
6. Confirm current state: Stories **001–020** complete/public; next pending is **021** (private; not generated). Scheduler **Disabled**.

## Hard rules

- **Never skip sequence.** Process the next pending episode only.  
- **One pending story per run.** Do not generate the following episode in the same run.  
- Use **Story Format V2** only (`docs/CONTENT_STANDARD.md`).  
- Run **source guards**; stay inside `must_include` / `must_avoid` / chapter boundaries.  
- Preserve the **exact eight-file** package:  
  `story.md`, `narration.mp3`, `story_poster.png`, `coloring_page.png`, `simple_coloring_page.png`, `activity_sheet.pdf`, `whatsapp_caption.txt`, `manifest.json`.  
- TTS: **ElevenLabs Renee** if preflight passes; otherwise **OpenAI Marin**.  
- **No duplicate paid chunks** when a valid generation-verified candidate already passes.  
- Build in **staging**, validate, then **atomic promote** to `output/<chapter>_<slug>/`.  
- Upload to **Google Drive only after local PASS**.  
- **Read back** Drive (exact eight files / hashes or link verification).  
- **Advance the queue only on complete success** (local + Drive when upload enabled).  
- On partial failure: **do not upload**, **do not advance**, leave story `pending`.  
- **Never enable WhatsApp or Telegram** implicitly. Keep sending disabled unless the operator explicitly requests and configures them.  
- **Never modify locked Stories 001–006** without explicit approval.  
- **Do not enable the MWF scheduler** unless explicitly approved (install defaults Disabled).  
- Follow-along cues remain `needs_alignment` — backlog D-09; no paid transcription in this release (`docs/backlog/FOLLOW_ALONG_ALIGNMENT.md`).

## Supported commands (do not invent flags)

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
.\scripts\create-next-bhava-story.ps1
.\scripts\run_prod.ps1
.\.venv\Scripts\python.exe run_daily_story.py --mode prod|test
```

Documented optional args on `run_daily_story.py`: `--force`, `--chapter`, `--rebuild`, `--rebuild-components`, `--rebuild-range`, `--preserve-queue`, `--replace-drive`, `--no-upload`, `--debug`, `--clean-reset`. Prefer `scripts/create-next-bhava-story.ps1` or wrappers `scripts/run_prod.ps1` / `scripts/run_test.ps1`.

Release (see runbooks; v3 is the staging candidate being prepared):

```powershell
.\scripts\release-bhava.ps1 -Status
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20 -DryRun
```

## Queue and delivery

- Static plan: `input/series_plan.csv` (no runtime status).  
- Runtime: `tracking/queue_state.csv`.  
- Distribution: Drive via `GOOGLE_DRIVE_UPLOAD_ENABLED` after local PASS.  
- Scheduler: `Krishna Story Factory MWF` (Mon/Wed/Fri 10:00 AM + 12:00 PM backup) via `scripts/install_mwf_story_task.ps1` + `scripts/run_daily_story_scheduled.ps1`. Install defaults **Disabled**; keep Disabled. Same-day production guard is mandatory (noon no-ops after a successful 10 AM run).  
- Stack: Node **24**, Python **3.14**. Content: `bhava-content-001-020-v2` exists; **v3** staging candidate in preparation. Production stays on older web/content until later approval.

## Finish criteria

- Exact eight files locally.  
- `manifest.publishable` honest for prod PASS packages.  
- Drive folder matches when upload enabled.  
- Queue advanced only once on success.  
- No secrets, outputs, or runtime CSVs committed.  
- Run `.\scripts\test_all.ps1` before claiming done when code/docs changed.
