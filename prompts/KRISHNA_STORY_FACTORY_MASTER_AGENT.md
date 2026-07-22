# Krishna Story Factory — Master Agent Prompt

Canonical engineering/operations handoff. Use this prompt instead of historical repair diaries.

## Before any work

1. Read `README.md`.  
2. Read `docs/PROJECT_SNAPSHOT_V1.md`.  
3. Read `docs/CONTENT_STANDARD.md` (and `input/content_quality_rules.md` if needed).  
4. Read the current queue: `tracking/queue_state.csv` (next `pending` only).  
5. Confirm Stories **001–006** are locked unless the operator gave explicit approval to change them.

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
- **Never enable WhatsApp or Telegram** implicitly. Keep them disabled unless the operator explicitly requests and configures them.  
- **Never modify locked Stories 001–006** without explicit approval.

## Supported commands (do not invent flags)

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
.\scripts\run_prod.ps1
.\.venv\Scripts\python.exe run_daily_story.py --mode prod|test
```

Documented optional args on `run_daily_story.py`: `--force`, `--chapter`, `--rebuild`, `--rebuild-components`, `--rebuild-range`, `--preserve-queue`, `--replace-drive`, `--no-upload`, `--debug`, `--clean-reset`. Prefer wrappers `scripts/run_prod.ps1` / `scripts/run_test.ps1`.

## Queue and delivery

- Static plan: `input/series_plan.csv` (no runtime status).  
- Runtime: `tracking/queue_state.csv`.  
- Distribution: Drive via `GOOGLE_DRIVE_UPLOAD_ENABLED`.  
- Scheduler: `Krishna Story Factory MWF` (Mon/Wed/Fri 06:00) via `scripts/install_mwf_story_task.ps1` + `scripts/run_daily_story_scheduled.ps1`.

## Finish criteria

- Exact eight files locally.  
- `manifest.publishable` honest for prod PASS packages.  
- Drive folder matches when upload enabled.  
- Queue advanced only once on success.  
- No secrets, outputs, or runtime CSVs committed.  
- Run `.\scripts\test_all.ps1` before claiming done when code/docs changed.
