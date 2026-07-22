# Daily Operations (Windows)

All commands from the repo root unless noted.

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
```

## A. Inspect state

```powershell
git switch main
git pull --ff-only
.\.venv\Scripts\python.exe scripts\diagnose_local_config.py
```

Optional:

```powershell
Get-ScheduledTask -TaskName "Krishna Story Factory MWF" | Select-Object TaskName, State
Import-Csv tracking\queue_state.csv | Select-Object chapter_no, slug, status | Format-Table
```

## B. Check next pending story

```powershell
Import-Csv tracking\queue_state.csv | Where-Object { $_.status -eq 'pending' } | Select-Object -First 1 chapter_no, slug, status
```

Or:

```powershell
.\.venv\Scripts\python.exe scripts\diagnose_local_config.py
```

(`diagnose_local_config.py` prints `Next pending story`.)

After the 001–006 lock, expect **007** pending until it is successfully generated.

## C. Dry run / test mode (no paid APIs)

```powershell
.\scripts\run_test.ps1 --force
```

Test mode must not call paid APIs. Use it to confirm pipeline structure only.

## D. Generate one pending story (production)

```powershell
.\scripts\run_prod.ps1
```

Equivalent:

```powershell
.\.venv\Scripts\python.exe run_daily_story.py --mode prod
```

Expected sequence:

1. Provider preflight (ElevenLabs Renee → OpenAI Marin fallback).  
2. Select next pending row from `tracking/queue_state.csv`.  
3. Generate Story Format V2 + audio + images + activity PDF in staging.  
4. Validate exact eight files and quality gates.  
5. Atomic promote to `output/<chapter>_<slug>/`.  
6. If `GOOGLE_DRIVE_UPLOAD_ENABLED=true`, upload eight files and set package link.  
7. Advance queue only on full success.  

On failure: no upload, no queue advance, story remains pending.

Useful documented flags (optional): `--chapter 007`, `--force`, `--no-upload`, `--debug`. Prefer wrappers; do not invent flags.

## E. Validate the generated package

Replace `007_kamsa-begins-his-persecutions` with the actual folder name.

```powershell
$pkg = "output\007_kamsa-begins-his-persecutions"
Get-ChildItem $pkg | Select-Object Name, Length
.\.venv\Scripts\python.exe -c "from pathlib import Path; from krishna_story_factory.outputs import FINAL_OUTPUT_FILES; p=Path(r'$pkg'); print(sorted(x.name for x in p.iterdir() if x.is_file())); assert {x.name for x in p.iterdir() if x.is_file()}==set(FINAL_OUTPUT_FILES)"
Get-Content "$pkg\manifest.json" | Select-Object -First 40
(Get-Item "$pkg\narration.mp3").Length
Get-Item "$pkg\story_poster.png","$pkg\coloring_page.png","$pkg\simple_coloring_page.png","$pkg\activity_sheet.pdf"
```

Release / publishable evidence:

```powershell
.\scripts\test_all.ps1
.\.venv\Scripts\python.exe -m pytest tests/test_pilot_release_hash_evidence.py tests/test_release_artifacts_001_006.py tests/test_post_pr7_release_blockers.py -q
```

Drive readback (when credentials configured): use `scripts/test_google_drive_upload.ps1` for connectivity; production upload path already verifies folder contents / text links after upload. Confirm `manifest.package.package_link` and caption contain the Drive folder URL.

## F. Review Drive folder

Look for the per-story URL in:

- `output/<chapter>_<slug>/manifest.json` → `package.package_link`  
- `output/<chapter>_<slug>/whatsapp_caption.txt`  
- `tracking/latest_run_summary.json` / `logs/latest_run_summary.txt` (when written)  
- `logs/scheduler/daily_*.log` for scheduled runs  
- `tracking/storage_log.csv`

## G. Rerun / repair (no double queue advance)

- Failed run that never advanced: fix issue, rerun `.\scripts\run_prod.ps1` (same pending chapter).  
- Local-only regen without upload: `.\scripts\run_prod.ps1 --no-upload` (or with `--chapter NNN` when intentionally targeting a chapter).  
- Component rebuild (activity/coloring) without WhatsApp and without regenerating locked story text/audio:

```powershell
.\scripts\run_prod.ps1 --chapter 007 --rebuild-components activity,coloring --debug
```

- Safer multi-component rebuild tooling: `scripts/manual_rebuild_story.ps1` / `scripts/rebuild_story_packages.py` (see `docs/15_MANUAL_STORY_REBUILD_RUNBOOK.md`). Queue must stay unchanged for locked 001–006 unless approved.  
- Do **not** use `--force` casually; it overrides daily guards / intentional regeneration.

## H. Roll back to release tag

```powershell
git fetch --tags
git switch --detach v1.0.0-pilot-stories-001-006
```

Return to main:

```powershell
git switch main
git pull --ff-only
```

Tag restores code/config only. Local `output/` and Drive packages are separate. Full notes: [RELEASE_AND_ROLLBACK.md](RELEASE_AND_ROLLBACK.md).
