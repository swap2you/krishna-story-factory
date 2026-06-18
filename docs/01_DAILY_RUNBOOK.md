# Daily Runbook — Krishna Book Bedtime

Main morning manual for generating one Krishna Book bedtime package.

## 1. Open PowerShell

## 2. Go to project folder

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
```

## 3. Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Check next pending story

```powershell
Import-Csv input\series_plan.csv | Where-Object { $_.status -eq 'pending' } | Select-Object -First 1 chapter_no,slug,title,source_reference
```

Expected first pending story: `002_devaki-and-vasudeva-wedding`

## 5. Optional local test (no paid APIs)

```powershell
python run_daily_story.py --mode test --force
```

Check audio script has no `[pause]` markers and activity sheet PDF has three pages with a word-search grid.

## 6. Run real production generation

```powershell
python run_daily_story.py --mode prod --force
```

This generates the full package and sends WhatsApp template messages when cloud sender is enabled.

## 7. Confirm output folder

```powershell
Get-ChildItem output | Sort-Object Name -Descending | Select-Object -First 3
```

Expected: `output/002_devaki-and-vasudeva-wedding/` with story, audio, 3-page activity sheet, story card images, and manifest `package.package_link`.

Check audio size:

```powershell
(Get-Item output\002_devaki-and-vasudeva-wedding\narration.mp3).Length
```

Prod target: narration.mp3 > 500 KB when ElevenLabs is enabled.

## 8. Confirm logs

```powershell
Get-Content tracking\story_log.csv
Get-Content tracking\send_log.csv -Tail 10
```

Diagnose WhatsApp failures:

```powershell
.\scripts\diagnose_whatsapp_failure.ps1
```

## 9. If WhatsApp token expires

1. Open Meta for Developers and create a fresh temporary token.
2. Paste into `WHATSAPP_CLOUD_TOKEN` in local `.env` only.
3. Never commit `.env`.
4. Re-run:

```powershell
python scripts/test_whatsapp_cloud.py
```

## 10. If OpenAI or ElevenLabs fails

- Check `.env` flags: `OPENAI_TEXT_ENABLED`, `OPENAI_IMAGE_ENABLED`, `ELEVENLABS_ENABLED`
- Check API key balances and model names
- Re-run test mode first to confirm pipeline structure
- Fix keys locally, then rerun prod

## 11. If the story quality is bad

- Edit notes in `input/series_plan.csv` for the row
- Mark the row `pending` again if needed
- Improve `input/content_quality_rules.md` guidance
- Re-run with `--force` only after you intend to regenerate

## 12. Rerun with force

```powershell
python run_daily_story.py --mode prod --force
```

Use `--force` when you intentionally want to override the daily send guard or regenerate the current package.

## 13. Avoid duplicate sends

- Do not run prod twice the same morning without reason
- The daily send guard blocks repeat WhatsApp sends unless `--force` is used
- Check `tracking/story_log.csv` before sending again

## Quick reference

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod --force
Get-Content tracking\story_log.csv
Get-Content tracking\send_log.csv
```
