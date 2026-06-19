# Build Report — Krishna Book Bedtime v1.3

Date: 2026-06-18  
Base commit: `4d2f6f3`

## Summary

Fixed story word-count quality gate to measure **Main Story only**, upgraded story card and coloring prompt normalization, strengthened story 002 source guards, and validated story **002 — The Wedding and the Heavenly Voice** in prod.

## pytest result

```text
45 passed
```

## Story 002 quality result

```text
quality_status: PASS
Main Story: 1003 words (target 750–1050)
Total story.md: 1150 words (allowed; no warning)
Audio script: 705 words
Repetition: PASS
story_card_square_prompt: PASS (devotional/cinematic/ultra-realistic)
coloring_page_prompt: PASS (centered, no cropping, thick outlines, etc.)
```

## Commands run

```powershell
pytest -q
python run_daily_story.py --mode test --force
python run_daily_story.py --mode prod --force
python scripts/diagnose_local_config.py
```

## Output folder

`output/002_devaki-and-vasudeva-wedding/`

## Audio / MP3

- MP3 size: **3,721,552 bytes**
- Audio script: **705 words**
- No `[pause]` markers; `<break time="..."/>` only

## Activity sheet

3 pages (recap/questions, word search + drawing box, coloring + family activity)

## Drive upload status

```text
FAILED — ModuleNotFoundError: google.auth not installed in .venv
Run: pip install -r requirements.txt
Then enable GOOGLE_DRIVE_* vars in local .env and re-run test upload script
```

## WhatsApp template status

```text
Template: daily_krishna_story
Prod send: FAILED_CLOUD — TOKEN_EXPIRED (HTTP 401)
Story generation succeeded; WhatsApp failure did not block package creation
```

## Next pending story

`003_vasudevas-promise — Vasudeva's Promise and Kamsa's Fear`

## Morning command

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod
```

## Key code changes

- Quality gate counts **Main Story section** only; total markdown >1300 words is a warning
- `prompt_normalize.py` enforces cinematic/devotional card prompts and premium coloring prompts
- Story 002 source guard: recap must mention "eighth son"; blocks full promise sequence
- Story generation prompt expanded for story 002 scope and image direction
- Diagnostics print Drive enable instructions when upload disabled

## Known limitations

1. Drive upload requires `pip install -r requirements.txt` plus OAuth in local `.env`
2. WhatsApp token must be refreshed; template must be Approved in Meta
3. If audio sounds too plain, change ElevenLabs voice ID/settings — do not pad script length
