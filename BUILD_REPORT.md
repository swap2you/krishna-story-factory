# Build Report

Version: Krishna Book Bedtime v1.2  
Date: 2026-06-18

## What changed

- Removed story/audio repetition padding; added repetition detection, cleanup, and quality FAIL gates
- Story target 750–1050 words; audio script 500–750 words; MP3 min 250 KB (no forced 4-minute filler)
- ElevenLabs voice settings configurable via `.env` (stability, style, speed, pronunciation dictionary)
- Improved story, audio, image, and coloring-page prompts (3D cinematic hero, cute coloring book style)
- Google Drive API upload module with OAuth + local sync fallback + `storage_log.csv`
- WhatsApp `daily_krishna_story` as default template in `.env.example`; `hello_world` marked smoke-test only
- Dashboard shows Drive status, package link, audio info, template name
- Scripts: `check_audio_quality.py`, `test_google_drive_upload.py`, `test_whatsapp_daily_template.py`

## Validation

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/check_audio_quality.py output\004_prayers-in-the-prison\narration.mp3
```

| Check | Result |
|-------|--------|
| `pytest -q` | **35 passed** |
| Test pipeline | **SUCCESS** |
| Repetition gate | **enabled** (no padding loops) |
| Drive upload | **DISABLED** until `GOOGLE_DRIVE_UPLOAD_ENABLED=true` + credentials |
| WhatsApp template (local `.env`) | Set `WHATSAPP_TEMPLATE_NAME=daily_krishna_story` for real parent messages |

## Known limitations

- Drive upload requires local OAuth credentials (not committed)
- `hello_world` in local `.env` sends smoke test only — switch to `daily_krishna_story` after Meta approval
- Pronunciation dictionary requires manual ElevenLabs setup if API field unsupported
