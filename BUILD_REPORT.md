# Build Report

Version: Krishna Book Bedtime v1  
Date: 2026-06-18

## What was cleaned

- Archived legacy docs and build prompts to `docs/archive/initial_build_notes/`
- Replaced main docs with systematic v1 guides `docs/01`–`docs/07`
- Replaced prompt library with focused Krishna Book prompts under `prompts/`
- Reset queue to Krishna Book chapters 001–010 (`krishna_book_bedtime`)
- Removed old sample stories (Damodara, Fruit Seller, Gajendra, Prahlada, etc.) from active queue
- Cleared generated `output/*` from repo commit (local prod output kept until push)

## Docs that remain (main path)

- `docs/01_DAILY_RUNBOOK.md`
- `docs/02_SETUP_AND_KEYS.md`
- `docs/03_WHATSAPP_CLOUD.md`
- `docs/04_CONTENT_GUIDE_KRISHNA_BOOK.md`
- `docs/05_DASHBOARD_GUIDE.md`
- `docs/06_TESTING_AND_VALIDATION.md`
- `docs/07_TROUBLESHOOTING.md`

## Queue reset

- Project: `krishna_book_bedtime`
- Library: `krishna_book`
- Age range: `6-12`
- Chapters 001–010 from Krishna Book opening pastimes
- Sample state in repo: `001` done, `002`–`010` pending
- RFC-style CSV quoting on `summary_seed` and `notes` fields (one row per line)

## Code improvements

- Plan-specific mock/prod generation tied to queue row
- Two-page story-specific activity sheet PDF
- `line_art_prompt.txt` and `coloring_page_prompt.txt` outputs
- Manifest fields: `story_source`, `audio_source`, `image_source`
- Prod ElevenLabs required unless `ALLOW_PLACEHOLDER_AUDIO=true`
- WhatsApp CSV broadcast with REPLACE-phone skip and `daily_krishna_story` prep
- Dashboard shows project, flags, logs

## Validation commands and results

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/test_whatsapp_cloud.py
python run_daily_story.py --mode prod --force
```

| Check | Result |
|-------|--------|
| `pytest -q` | **15 passed** |
| Test pipeline | **SUCCESS** → `output/001_the-earth-prays-for-krishna/` |
| WhatsApp smoke | **SUCCESS** (hello_world, Meta wamid) |
| Prod pipeline | **SUCCESS**, quality **PASS**, WhatsApp **SENT_CLOUD** (1 recipient) |

## Real prod generation

Yes — prod run generated OpenAI story, ElevenLabs audio, OpenAI/fallback image, PDF, and sent `hello_world` to Swapnil Test only (wife placeholder skipped).

## Known limitations

- No WhatsApp group sending in v1
- No direct MP3/PDF/image WhatsApp upload yet
- `daily_krishna_story` template requires Meta approval
- Recommended production path: approved template + Google Drive package link
