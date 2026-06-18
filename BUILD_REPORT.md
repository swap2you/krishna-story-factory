# Build Report

Version: Krishna Book Bedtime v1.1 (parent-ready quality)  
Date: 2026-06-18

## What changed in this upgrade

- Audio script sanitizer removes `[pause]` and unsupported bracket tags before ElevenLabs
- Bedtime audio targets 650–850 words with `<break time="..."/>` pacing
- Prod quality gates: story >= 800 words, audio script >= 600 words, MP3 > 500 KB
- 3-page activity sheet with real 12x12 word-search grid and answer key in manifest
- Separate image prompts: hero, square card, wide card, coloring page, line art
- Optional `coloring_page.png` and `story_card_square.png` generation
- Google Drive package link support via `.env` (`GOOGLE_DRIVE_FOLDER_URL`, optional local sync)
- WhatsApp caption template: reply here, today, package link, no group wording
- WhatsApp failure diagnostics with structured reasons (`TOKEN_EXPIRED`, etc.)
- `daily_krishna_story` template body params: name, title, package link
- Story 002 source guard blocks “King Kamsa” and unrelated pastimes

## Validation commands and results

```powershell
pytest -q
python run_daily_story.py --mode test --force
python run_daily_story.py --mode prod --force
.\scripts\diagnose_whatsapp_failure.ps1
```

| Check | Result |
|-------|--------|
| `pytest -q` | **28 passed** |
| Test pipeline | **SUCCESS** |
| Prod pipeline | **SUCCESS**, quality **PASS** |
| Prod output | `output/002_devaki-and-vasudeva-wedding/` |
| narration.mp3 size | **3,809,324 bytes (~3.8 MB)** |
| Images generated | `story_card.png`, `story_card_square.png`, `coloring_page.png` (OpenAI) |
| Activity sheet | **3 pages** with word-search grid |
| Drive link | Empty in prod (set `GOOGLE_DRIVE_FOLDER_URL` in local `.env`) |
| WhatsApp | **FAILED_CLOUD** — `TOKEN_EXPIRED` (Meta OAuth 401); generation still succeeded |

## Queue state after prod validation

- `001` done, `002` done (prod run), `003`–`010` pending
- Next prod story: `003_vasudevas-promise`

## Known limitations

- WhatsApp token must be refreshed locally when expired
- Drive link requires local `.env` configuration (not committed)
- Ambient audio mix is config-ready but not fully implemented
- v1 sends individual CSV recipients only, not WhatsApp groups
