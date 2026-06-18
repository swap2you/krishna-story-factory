# Testing and Validation

## Required commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

## Optional live checks (local `.env` with real keys)

```powershell
python scripts/test_whatsapp_cloud.py
python run_daily_story.py --mode prod --force
```

## Required output files

```text
story.md
audio_script.txt
whatsapp_caption.txt
activity_sheet.pdf
story_card.png
image_prompt.txt
line_art_prompt.txt
parent_notes.md
manifest.json
narration.mp3
```

## Manifest source fields

- `story_source`
- `audio_source`
- `image_source`

## Quality gates

- All required files exist and are non-empty
- Story >= 800 words in prod; audio script >= 600 words in prod
- No `[pause]` in audio script; narration.mp3 > 500 KB in prod when ElevenLabs enabled
- WhatsApp caption must not mention "group"; must say "reply here" and "today"
- Activity sheet includes a real word-search grid (10+ words placed)
- Story 002 source guard blocks "King Kamsa" and unrelated pastimes

## New tests

```powershell
pytest tests/test_audio_sanitize.py tests/test_quality_guards.py tests/test_caption_drive.py -q
```
- Story sections present
- Prod with ElevenLabs requires real MP3 unless `ALLOW_PLACEHOLDER_AUDIO=true`
- `source_reference`, `library_id`, `age_range`, `generated_at` in manifest
