# Validation Artifacts

Validation date: `2026-06-18`

## Generated Output Folder

`C:\Development\Workspace\DevotionalRepo\krishna-story-factory\output\004_prahlada`

## Pipeline Result

```json
{
  "status": "SUCCESS",
  "output_dir": "C:\\Development\\Workspace\\DevotionalRepo\\krishna-story-factory\\output\\004_prahlada",
  "quality_status": "PASS",
  "whatsapp_status": "NOT_ATTEMPTED",
  "detail": "WhatsApp send disabled."
}
```

## Files Created

| File | Bytes |
| --- | ---: |
| `story.md` | 3200 |
| `audio_script.txt` | 481 |
| `whatsapp_caption.txt` | 273 |
| `activity_sheet.pdf` | 3636 |
| `story_card.png` | 15028 |
| `image_prompt.txt` | 236 |
| `parent_notes.md` | 299 |
| `manifest.json` | 1347 |
| `narration.mp3` | 66 |

All required files exist and are non-empty.

## Manifest Fields Verified

- `source_reference`: `Srimad-Bhagavatam Canto 7 Chapter 8`
- `library_id`: `srimad_bhagavatam`
- `age_range`: `7-11`
- `generated_at`: `2026-06-18T11:01:33-04:00`

`manifest.json` was validated with:

```powershell
.\.venv\Scripts\python.exe -m json.tool output\004_prahlada\manifest.json
```

## Quality Status

`PASS`

The latest `tracking/story_log.csv` entry records:

```text
2026-06-18,004,prahlada,Prahlada's Faith,C:\Development\Workspace\DevotionalRepo\krishna-story-factory\output\004_prahlada,SUCCESS,PASS,NOT_ATTEMPTED,manual,C:\Development\Workspace\DevotionalRepo\krishna-story-factory\output\004_prahlada\manifest.json,2026-06-18T11:01:33-04:00,
```

## Sender Status

`NOT_ATTEMPTED`

Reason: WhatsApp sending is disabled. No live OpenAI, ElevenLabs, WhatsApp, Telegram, Slack, or Discord API calls were made.

## Test Result

```text
1 passed in 1.13s
```

## Dashboard Status

- `dashboard.py` compile check passed.
- Streamlit startup check reached:

```text
URL: http://127.0.0.1:8507
Uvicorn server started on 127.0.0.1:8507
```

## Notes

- The queue had no pending story at the start of validation, so `004_prahlada` was temporarily set to `pending` and then restored to `done` by the CLI after generation.
- Pytest temp/cache paths were redirected to a workspace-local folder because the default Windows temp/cache locations were not writable in this session.
