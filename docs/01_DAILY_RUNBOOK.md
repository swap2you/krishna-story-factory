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
Import-Csv tracking\queue_state.csv | Where-Object { $_.status -eq 'pending' } | Select-Object -First 1 chapter_no,slug
```

Expected first pending story after this release: `003_vasudeva-keeps-his-word`.

`input/series_plan.csv` contains tracked static metadata only. Never add execution status to it.

## 5. Optional local test (no paid APIs)

```powershell
.\scripts\run_test.ps1 --force
```

Check audio script has no `[pause]` markers. The Activity Engine V2 PDF must have 2–4
useful pages for normal packs (1 page only for simple types), no blank page, and every
page tied to the current pastime. See [11_ACTIVITY_ENGINE_V2.md](11_ACTIVITY_ENGINE_V2.md).

## 6. Run real production generation

```powershell
.\scripts\run_prod.ps1
```

This generates the full package and uploads exactly seven files to Google Drive when
Drive upload is enabled. WhatsApp/Telegram remain disabled.

## 7. Confirm output folder

```powershell
Get-ChildItem output | Sort-Object Name -Descending | Select-Object -First 3
```

Expected: `output/003_vasudeva-keeps-his-word/` with exactly seven final files, including
the multi-page activity sheet and manifest `package.package_link`.

## Component-only rebuild

To keep the approved story, narration, poster, caption, Drive folder, and queue state unchanged:

```powershell
.\scripts\run_prod.ps1 --chapter 001 --rebuild-components activity,coloring --debug
.\scripts\run_prod.ps1 --chapter 002 --rebuild-components activity,coloring --debug
```

Use `--no-upload` for local validation. Component rebuild replaces only
`activity_sheet.pdf`, `coloring_page.png`, and `manifest.json`; it never sends WhatsApp.

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

- Edit static notes in `input/series_plan.csv` only when the editorial plan changes
- Mark the row `pending` in ignored `tracking/queue_state.csv` when an intentional rerun is needed
- Improve `input/content_quality_rules.md` guidance
- Re-run with `--force` only after you intend to regenerate

## 12. Rerun with force

```powershell
.\scripts\run_prod.ps1 --chapter 003 --force
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
.\scripts\run_prod.ps1
Get-Content tracking\story_log.csv
Get-Content tracking\send_log.csv
```
