# Content Guide — Krishna Book Bedtime

## Project

`krishna_book_bedtime` — sequential Krishna Book pastimes for children ages 6–12.

## Queue source of truth

`input/series_plan.csv`

Columns include:

- chapter_no, slug, title, project, library_id
- source_reference, scripture_reference, summary_seed
- age_range, package_type, status, notes

## Rules

See `input/content_quality_rules.md`.

## Generation prompts

- `prompts/story_generation_prompt.md`
- `prompts/audio_script_prompt.md`
- `prompts/image_prompt_prompt.md`
- `prompts/activity_sheet_prompt.md`
- `prompts/quality_review_prompt.md`

## Audio and images

- Audio script: 650–850 words, `<break time="..."/>` pacing, no `[pause]`
- Story card: one clear focal scene, square 1080x1080 direction
- Coloring page: thick outlines, no weapons
- Story 002: do not call Kamsa "king"; use "Devaki's powerful brother"

## Package link

Parents receive the Google Drive parent folder link in `whatsapp_caption.txt` when `GOOGLE_DRIVE_FOLDER_URL` is configured.

## Reset queue

```powershell
.\scripts\reset_krishna_book_queue.ps1
```
