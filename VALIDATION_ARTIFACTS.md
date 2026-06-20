# Validation Artifacts — Story Visual Generation

Date: 2026-06-20  
Story: **003 — Vasudeva's Promise and Kamsa's Fear**

## pytest

```text
69 passed
```

## Dry-run

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --generate-all `
  --dry-run
```

Artifacts saved: `visual_brief.json`, `line_art_prompt.txt`, `poster_art_prompt.txt`, `poster_copy.json`, `visual_generation_manifest.json` (no API image calls).

## Full generation

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --generate-all `
  --use-references `
  --force
```

| Field | Value |
|-------|-------|
| Model | gpt-image-1 |
| Quality | medium |
| Reference images used | false (PNG files not present) |
| Line art size | 1024x1536 |
| Poster size | 1024x1536 |
| Quality score | 100 |

## Final outputs

```text
output/003_vasudevas-promise/visual_brief.json
output/003_vasudevas-promise/line_art_prompt.txt
output/003_vasudevas-promise/line_art_raw.png
output/003_vasudevas-promise/line_art_portrait.png
output/003_vasudevas-promise/coloring_page.png
output/003_vasudevas-promise/coloring_page_print.pdf
output/003_vasudevas-promise/poster_art_prompt.txt
output/003_vasudevas-promise/poster_art_raw.png
output/003_vasudevas-promise/poster_copy.json
output/003_vasudevas-promise/story_poster.png
output/003_vasudevas-promise/story_poster_whatsapp.jpg
output/003_vasudevas-promise/visual_generation_manifest.json
```

## Notes

- Shared templates contain no hardcoded Vasudeva/Kamsa/Devaki names.
- Titles, quotes, and captions are composited locally with Pillow.
- Place approved style references at `assets/reference/line_art_reference.png` and `assets/reference/poster_reference.png` when available.

See [docs/09_STORY_VISUAL_GENERATION.md](docs/09_STORY_VISUAL_GENERATION.md).
