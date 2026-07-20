# Testing and Validation

## Required commands

```powershell
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
```

## Optional live checks (local `.env` with real keys)

```powershell
python scripts/test_whatsapp_cloud.py
.\scripts\run_prod.ps1
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
- Activity PDF is 2–4 pages for normal packs (1–2 for simple types), passes structural and vision QA (≥88), and is not a generic worksheet
- ActivityPack pages each include a story_connection; answer keys stay in the manifest only
- See [11_ACTIVITY_ENGINE_V2.md](11_ACTIVITY_ENGINE_V2.md)
- Story source guards enforce the selected episode boundary and required relationships

## New tests

```powershell
pytest tests/test_audio_sanitize.py tests/test_quality_guards.py tests/test_caption_drive.py -q
```
- Story sections present
- Prod with ElevenLabs requires real MP3 unless `ALLOW_PLACEHOLDER_AUDIO=true`
- source, age, quality, activity, package link, and Drive result in manifest
