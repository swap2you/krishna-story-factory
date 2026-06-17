# Validation Artifacts

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

## Expected test result

```text
1 passed
```

## Expected pipeline result (test mode)

```json
{
  "status": "SUCCESS",
  "quality_status": "PASS",
  "whatsapp_status": "NOT_ATTEMPTED"
}
```

## Required output files

```text
story.md
audio_script.txt
whatsapp_caption.txt
activity_sheet.pdf
story_card.png
image_prompt.txt
parent_notes.md
manifest.json
narration.mp3
```

## Manifest fields verified

- `source_reference`
- `library_id`
- `age_range` (`7-11`)
- `generated_at`

## Regenerate locally

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode test --force
```

Next pending story in sample queue: `004_prahlada`.
