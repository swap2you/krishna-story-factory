# Story Visual Generation

Krishna Story Factory can turn each completed `story.md` into two premium devotional visuals:

1. **Line-art portrait** — a portrait-format coloring page for children ages 6–13.
2. **Cinematic poster** — an ultra-realistic 3D devotional story flyer with local typography.

The system is story-driven: prompts, briefs, and compositors read the current story only. Shared templates never hardcode characters from any single pastime.

## What gets produced

For each story output folder:

| File | Purpose |
|------|---------|
| `visual_brief.json` | Structured scene/character brief from the story |
| `line_art_prompt.txt` | Rendered OpenAI prompt for coloring art |
| `line_art_raw.png` | Raw API artwork (no local title) |
| `line_art_portrait.png` | Final coloring page with title/border |
| `coloring_page.png` | Alias used by activity sheet |
| `coloring_page_print.pdf` | Print-ready A4/Letter PDF |
| `poster_art_prompt.txt` | Rendered cinematic poster prompt |
| `poster_art_raw.png` | Raw poster artwork without typography |
| `poster_copy.json` | Title, quote, one-liner, captions |
| `story_poster.png` | Final poster with local typography |
| `story_poster_whatsapp.jpg` | Compressed preview for sharing |
| `visual_generation_manifest.json` | Model, sizes, reference usage, quality |

## Why a structured visual brief?

The text model analyzes `story.md` and returns strict JSON (characters, central scene, beats, quotes, must-include/avoid). That brief feeds both image prompts so:

- Characters and relationships stay faithful to the story
- The emotional turning point drives composition
- Child-safety and devotional tone are enforced before any image call

If JSON parsing fails, the system retries once with a repair instruction and never continues with incomplete data.

## Why local typography?

Image models misspell text. Final titles, heavenly quotations, captions, and borders are added with **Pillow** after generation. The AI prompts explicitly reserve clean areas but do not rely on the model for spelling.

## Reference images (optional)

Place approved private style references here:

- `assets/reference/line_art_reference.png`
- `assets/reference/poster_reference.png`

When `IMAGE_USE_STYLE_REFERENCES=true` and files exist, they guide layout richness, line quality, lighting, and mood only. The **current story always overrides** reference characters, events, title, and quotation.

If references are missing, generation continues with text templates only and logs that style references were not used.

## Environment settings

See `.env.example`:

```env
OPENAI_IMAGE_ENABLED=true
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_QUALITY=high
OPENAI_IMAGE_OUTPUT_FORMAT=png
IMAGE_USE_STYLE_REFERENCES=true
IMAGE_LINE_ART_SIZE=1024x1536
IMAGE_POSTER_SIZE=1024x1536
IMAGE_GENERATE_LINE_ART=true
IMAGE_GENERATE_POSTER=true
IMAGE_ADD_LOCAL_TYPOGRAPHY=true
VISUAL_QUALITY_THRESHOLD=80
```

Prefer `gpt-image-2` when available; the client falls back to your configured GPT Image model.

## Commands

### Both visuals (dry-run — prompts only, no API)

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --generate-all `
  --dry-run
```

### Line art only

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --line-art-only
```

### Poster only

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --poster-only
```

### Full generation with references

```powershell
.\.venv\Scripts\python.exe scripts\generate_story_visuals.py `
  --story output\003_vasudevas-promise\story.md `
  --output output\003_vasudevas-promise `
  --generate-all `
  --use-references `
  --force
```

PowerShell wrapper: `scripts/generate_story_visuals.ps1`

Validate outputs: `scripts/validate_story_visuals.py --output <folder> --require-all`

## Daily pipeline integration

After narration is generated, the daily pipeline:

1. Builds `visual_brief.json` from `story.md`
2. Generates line art and cinematic poster (when enabled)
3. Composes local typography
4. Continues with the existing story card (coloring is skipped when `IMAGE_GENERATE_LINE_ART=true`)
5. Builds the activity sheet using `coloring_page.png`
6. Records visual outputs in `manifest.json` under `outputs` and `visuals`
7. Uploads final files to Google Drive when configured

## Replacing reference images

Drop new PNGs at the paths above (same filenames). No code changes required. Use `--force` to regenerate an existing story package.

## Cost and quality

- Portrait sizes (`1024x1536`) cost more than square but match print and WhatsApp sharing.
- `OPENAI_IMAGE_QUALITY=high` improves detail; use dry-run first to review prompts.
- `VISUAL_QUALITY_THRESHOLD` gates automated checks; low scores are logged in the manifest.

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| Square instead of portrait | Check `IMAGE_LINE_ART_SIZE` / `IMAGE_POSTER_SIZE`; see manifest `actual_sizes` |
| Misspelled text in art | Enable `IMAGE_ADD_LOCAL_TYPOGRAPHY`; regenerate raw art only |
| Malformed hands | Regenerate with `--force`; tighten `must_include` in brief |
| Cluttered layout | Reduce supporting beats; simplify central scene in brief |
| Wrong characters | Regenerate brief; verify story.md relationships |
| Reference overpowering story | Use `--no-references` or replace reference with looser style sample |
| Line art too dark | Compositor auto-contrasts; regenerate with lighter raw art |
| Coloring spaces too small | Edit brief `line_art_focus`; regenerate line art |

## Limitations

Exact pixel-for-pixel replication across stories is not guaranteed. Consistency comes from fixed prompt templates, optional style references, structured briefs, and local typography—not from copying one approved image literally.
