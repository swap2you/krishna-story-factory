# Testing and Validation

## Required commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

## Optional live checks (local `.env` with real keys)

```powershell
python scripts/test_whatsapp_cloud.py
python run_daily_story.py --mode prod
```

## Required output files

```text
story.md
narration.mp3
story_poster.png
coloring_page.png
activity_sheet.pdf
whatsapp_caption.txt
manifest.json
```

## Manifest source fields

- `audio_source`
- `source_reference`
- `scripture_reference`
- `package.package_link`
- `activity.recommended_send_mode`

## Quality gates

- All required files exist and are non-empty
- Story >= 700 words in prod; audio script >= 525 words in prod
- No `[pause]` in audio script; narration.mp3 > 500 KB in prod when ElevenLabs enabled
- WhatsApp caption uses the per-story manifest link and activity-aware wording
- Activity PDF is one or two pages and passes structural and vision QA
- Story source guards enforce the selected episode boundary and required relationships

## New tests

```powershell
pytest tests/test_audio_sanitize.py tests/test_quality_guards.py tests/test_caption_drive.py -q
```
- Story sections present
- Prod with ElevenLabs requires real MP3 unless `ALLOW_PLACEHOLDER_AUDIO=true`
- source, age, quality, activity, package link, and Drive result in manifest
