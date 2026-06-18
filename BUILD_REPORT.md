# Build Report — Krishna Book Bedtime v1

Date: 2026-06-18  
Validation commit: (see git hash after commit)

## Summary

End-to-end Krishna Story Factory v1 validation for story **001 — The Earth Prays for Krishna to Come**.

- Story generation, audio, images, activity PDF, and quality gates: **PASS**
- Google Drive API upload: **blocked locally** (`GOOGLE_DRIVE_UPLOAD_ENABLED=false` in `.env`; parent folder URL used as fallback link)
- WhatsApp `daily_krishna_story`: **attempted, failed** (expired Cloud API token — HTTP 401)

## Git commit hash

Run `git rev-parse HEAD` after commit (pre-commit baseline: `73daadb`).

## Commands run

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\diagnose_local_config.py
.\.venv\Scripts\python.exe scripts\test_google_drive_upload.py
.\.venv\Scripts\python.exe scripts\test_whatsapp_daily_template.py
.\.venv\Scripts\python.exe run_daily_story.py --mode prod --force
.\.venv\Scripts\python.exe scripts\check_audio_quality.py output\001_the-earth-prays-for-krishna\narration.mp3
```

## pytest result

```text
36 passed
```

## Drive test result

```text
GOOGLE_DRIVE_UPLOAD_ENABLED is false. Set it true in local .env to test upload.
```

Local OAuth client JSON exists at `credentials/google_drive_oauth_client.json` (not committed). Token file not present until first OAuth run.

**Action required (local `.env` only — not modified by this validation):**

```env
GOOGLE_DRIVE_UPLOAD_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials/google_drive_oauth_client.json
GOOGLE_DRIVE_TOKEN_FILE=credentials/google_drive_token.json
```

Then re-run `scripts/test_google_drive_upload.py` for `KSF_TEST_UPLOAD_<timestamp>`.

## WhatsApp template test result

```text
FAILED: HTTP 404 (initial template test)
Prod send: HTTP 401 TOKEN_EXPIRED (Authentication Error code 190)
```

Template name configured: `daily_krishna_story` (not `hello_world`). Refresh `WHATSAPP_CLOUD_TOKEN` in local `.env`, confirm template is **Approved** in Meta WhatsApp Manager, then re-run:

```powershell
.\.venv\Scripts\python.exe scripts\test_whatsapp_daily_template.py
```

## Fresh prod result JSON

```json
{
  "status": "SUCCESS",
  "output_dir": "output\\001_the-earth-prays-for-krishna",
  "quality_status": "PASS",
  "whatsapp_status": "FAILED_CLOUD",
  "detail": "WhatsApp template send failed for all 2 recipient(s).",
  "package_link": "https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei?usp=sharing",
  "drive_upload_status": "DISABLED",
  "whatsapp_template": "daily_krishna_story",
  "whatsapp_failure_reason": "TOKEN_EXPIRED"
}
```

## Output folder

`output/001_the-earth-prays-for-krishna/`

## Drive package link

Parent folder (link-only fallback): https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei?usp=sharing

Per-story folder `001_the-earth-prays-for-krishna` will be created after Drive upload is enabled.

## Uploaded Drive files

None (upload disabled). Local package files generated:

- activity_sheet.pdf
- audio_script.txt
- coloring_page.png / coloring_page_prompt.txt
- hero_image_prompt.txt / image_prompt.txt
- line_art_prompt.txt
- manifest.json
- narration.mp3
- parent_notes.md
- story.md
- story_card.png / story_card_square.png
- story_card_*_prompt.txt
- whatsapp_caption.txt

## WhatsApp recipients

| Recipient | Attempted | Sent | Status |
|-----------|-----------|------|--------|
| Swapnil Patil | yes | no | FAILED — TOKEN_EXPIRED |
| Sachi Patil | yes | no | FAILED — TOKEN_EXPIRED |

Template used: `daily_krishna_story` (3 body params: name, title, package link).

## Audio duration and size

- MP3 size: **3,028,158 bytes** (~2.9 MB)
- Audio script: **509 words**
- `[pause]` markers: **none**
- Repetition errors: **0**

## Story word count

- **1,002 words** (main story + sections in story.md)
- No unrelated pastimes (Kamsa, Devaki wedding, Gokula, etc.) in story 001 output

## Repetition gate result

**PASS** — no repeated closings, paragraphs, or 8-word phrase violations after cleanup.

## Activity sheet page count

**3 pages** (recap/questions, word search + drawing box, coloring + family activity + five-star challenge + parent reply note)

Word search words: EARTH, BRAHMA, PRAYER, VISHNU, DEVA, HOPE, COW, BURDEN, PROMISE, KRISHNA

## Image files generated

- story_card.png (1.6 MB)
- story_card_square.png (1.6 MB)
- coloring_page.png (1.0 MB)

## Code changes in this validation

- `scripts/diagnose_local_config.py` — safe local config status
- Story generator: best-candidate regeneration + field expansion pass; coloring prompt normalization
- Story 001 source guard; repetition gates; Drive uploader timestamp suffix
- CSV queue reset (001 done, 002–010 pending); RFC CSV quoting on plan updates
- Send log fields enriched for template/title/package link

## Known limitations

1. **Drive upload** requires enabling flags in local `.env` and completing OAuth (first browser login).
2. **WhatsApp token** must be refreshed periodically; expired token blocks send even when template is approved.
3. **Template approval** — if Meta returns 404, template may be pending review or name/language mismatch.
4. Per-story Drive folder link replaces parent URL only after upload succeeds.

## Exact morning command

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod
```

Use `--force` only to override the once-per-day send guard.
