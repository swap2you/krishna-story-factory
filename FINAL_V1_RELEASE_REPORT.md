# Krishna Story Factory V1 — Final Release Report

Date: 2026-06-21  
Branch: `fix/final-v1-story-factory`

## Architecture

- **Single master prompt:** `prompts/DAILY_STORY_MASTER.md` with section loader in `prompts_loader.py`
- **Seven final outputs only:** story.md, narration.mp3, story_poster.png, coloring_page.png, activity_sheet.pdf, whatsapp_caption.txt, manifest.json
- **Intermediate work:** `.work/<run_id>/` (poster/coloring candidates, vision reviews) — deleted after success unless `DEBUG_ARTIFACTS=true`
- **Transactional pipeline:** generate → repair loop → pre-publish QA → Drive upload (7 files) → update caption/manifest → post-publish QA → mark done
- **Real vision QA:** OpenAI vision model scores poster and coloring candidates; threshold 86
- **Image model policy:** prefer `gpt-image-2`; remap forbidden `gpt-image-1` to `gpt-image-2`; explicit fallback `gpt-image-1.5` on API failure
- **Archived prompts:** `prompts/_archive/` (legacy story/image/visual prompt files)

## Files removed from active path

- Fragmented prompts under `prompts/` and `prompts/visuals/` (archived)
- Obsolete output variants: story cards, wide cards, raw PNGs, prompt text files, visual brief JSON, print PDF, WhatsApp JPEG duplicate
- Legacy visual pipeline no longer invoked by daily pipeline (modules remain but unused)

## Tests

```text
36 passed
```

## Story 001 — The Earth Prays for Krishna to Come

| Metric | Value |
|--------|-------|
| Status | SUCCESS |
| Main story words | 895 |
| Audio words | 606 |
| Audio duration | 203.7 s |
| Audio size | 3,259,289 bytes |
| Poster vision score | 87 |
| Coloring vision score | 94 |
| Reference images used | false (approved PNGs not present) |
| Drive | UPLOADED (7 files) |
| Drive link | https://drive.google.com/drive/folders/1_7R1uj_WtW0CfuhfMAz_d3FSF1zsHbo-?usp=sharing |

Uploaded files: story.md, narration.mp3, story_poster.png, coloring_page.png, activity_sheet.pdf, whatsapp_caption.txt, manifest.json

## Story 002 — The Wedding and the Heavenly Voice

| Metric | Value |
|--------|-------|
| Status | SUCCESS |
| Main story words | 911 |
| Audio words | 608 |
| Audio duration | 194.8 s |
| Audio size | 3,116,765 bytes |
| Poster vision score | 97 |
| Coloring vision score | 92 |
| Reference images used | false |
| Drive | UPLOADED (7 files) |
| Drive link | https://drive.google.com/drive/folders/1pr9ZMwnzE8bx7mgreAguduQFDzc8XC0V?usp=sharing |

## Queue state after validation

| Chapter | Status |
|---------|--------|
| 001 | done |
| 002 | done |
| 003 | **pending** (next) |
| 004–010 | pending |

Second prod run generated **002**, not 001. Next pending is **003**.

## Commands used

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe run_daily_story.py --mode prod --clean-reset --no-upload
.\.venv\Scripts\python.exe run_daily_story.py --mode prod
```

## Morning command

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\.venv\Scripts\Activate.ps1
.\scripts\run_prod.ps1
```

## WhatsApp

`SKIPPED_DISABLED` / `SKIPPED_RELEASE_SCOPE` — out of scope for this release; does not block generation or Drive upload.

## Known limitations

- Approved reference PNGs (`assets/reference/approved_line_art.png`, `approved_poster.png`) were not present; generation used high-quality text prompts only.
- Story 001 ran before image-model remap; story 002 used `gpt-image-2`.
- Vision QA depends on configured OpenAI vision/text model availability.
- Exact pixel replication across stories is not guaranteed; consistency comes from master prompt, optional references, candidate selection, and local poster typography (title + one-liner only).

## Repair cycles used

1 implementation cycle + 1 prod validation cycle (001 + 002). No fourth-cycle escalation required.
