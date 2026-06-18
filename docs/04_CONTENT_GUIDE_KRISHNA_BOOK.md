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

## Important

- Generate only the current pending row
- Do not mix unrelated pastimes
- Stay faithful to Krishna Book sequence from chapter 1 onward

## Reset queue

```powershell
.\scripts\reset_krishna_book_queue.ps1
```
