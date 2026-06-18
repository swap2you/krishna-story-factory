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
- Story sections present
- Prod with ElevenLabs requires real MP3 unless `ALLOW_PLACEHOLDER_AUDIO=true`
- `source_reference`, `library_id`, `age_range`, `generated_at` in manifest
