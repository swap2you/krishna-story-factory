# CLOSEOUT-B1 — Poster text compositor trace and root cause

Artifact correction inside the existing Bhāva Stories Production Launch.
Package version `2.1.1-copyright` → `2.1.2-copyright` for Stories 007 and 009.
No new product release, no provider calls, no narrative or narration change.

## 1. The two text bands, and who writes them

`story_poster.png` carries three text layers, written by two different code
paths at two different times. The closeout defect was in the older path.

| Layer | Written by | When |
| --- | --- | --- |
| Title band (top) | `krishna_story_factory/images/generator.py::compose_poster` | Story generation (v1.0) |
| Caption band (bottom of artwork) | `krishna_story_factory/images/generator.py::compose_poster` | Story generation (v1.0) |
| Credit strip (below caption) | `krishna_story_factory/publication/artifacts.py::append_image_credit_strip` | Copyright retrofit (2.1.x) |

The `2.1.1-copyright` retrofit rebuilt only the credit strip, and it already
used the validated Unicode resolver. That is why the credit line read correctly
while the title and caption above it still showed missing-glyph boxes: the
retrofit never touched them. They had been burned into the PNG a release
earlier.

## 2. Complete call path for the title and caption bands

```
run_daily_story.py
  └─ krishna_story_factory/pipeline.py
       └─ images/generator.py::generate_poster(settings, story_md, content, output_path, …)
            ├─ prod: ImageClient.generate(...) → work/candidates/poster_r*_c*.png   (artwork only, no text)
            │        vision_qa.review_image(...) selects the best candidate
            ├─ test: _placeholder_poster(...) synthesises a flat artwork canvas
            └─ images/generator.py::compose_poster(raw_path, output_path, title, one_liner)
                 ├─ title text      ← StoryContent.title                     (models.py, parsed from story.md front matter)
                 ├─ caption text    ← StoryContent.poster_one_liner or .takeaway
                 │                    (for 009 this is the fifth of the Five Lessons in story.md)
                 ├─ image master    ← raw_path (provider artwork or placeholder), pasted at y = title_band
                 ├─ font loader     ← images/generator.py::_font(size, bold=…)   ← ROOT CAUSE
                 ├─ wrapping        ← images/generator.py::_wrap(draw, text, font, max_w), first 2 lines kept
                 ├─ sizing          ← title 42 px bold, caption 24 px regular
                 │                    title_band = max(int(art_h * 0.08), 72)
                 │                    footer_band = max(int(art_h * 0.06), 56)
                 ├─ alignment       ← draw.text((width // 2, y), …, anchor="ma") — centred, top-anchored
                 ├─ encoding        ← Python str throughout; no transliteration, no encode/decode step
                 └─ save path       ← canvas.save(output_path, "PNG") → output/<NNN>_<slug>/story_poster.png
```

The retrofit then extends that canvas downward:

```
publication/artifacts.py::append_image_credit_strip(src, dest, year, ai_image, identity)
  ├─ font  ← publication/fonts.py::resolve_unicode_fonts().pillow_regular(20)   (already correct)
  └─ strip height = max(40, int(composed_height * 0.05)); placement = bottom_canvas_extension
```

## 3. Root cause

Before the fix, `images/generator.py::_font` was:

```python
def _font(size: int):
    for name in ("Segoe UI Bold", "Arial Bold", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()
```

Three failures compounded:

1. **The lookup names are not resolvable filenames.** `ImageFont.truetype`
   asks the OS for a font *file*. On Windows the installed files are
   `arialbd.ttf` and `segoeuib.ttf`; the space-separated display names
   `"Segoe UI Bold"` and `"Arial Bold"` raise `OSError`. `DejaVuSans-Bold.ttf`
   is not present on a stock Windows image either. All three candidates missed.
2. **The fallback was a bitmap font.** `ImageFont.load_default()` returns
   Pillow's bundled Aileron bitmap face, which covers little beyond Latin-1.
   `ū ā ṛ ṣ ṇ ṁ` and the em dash `—` have no glyph in it, so Pillow drew the
   `.notdef` box for each one.
3. **The fallback was silent.** Nothing validated glyph coverage before
   drawing, so the pipeline wrote a defective poster and reported success. The
   boxes then became part of the released PNG and survived every later
   hash-preserving retrofit.

Only two released posters were affected, because only two carry non-ASCII
characters in a text band: Story 007's caption (`Yoga-māyā`, `Kaṁsa`) and
Story 009's title and caption (`Pūtanā`, `Kṛṣṇa`, `—`).

## 4. The fix

- `_font` now delegates to the central fail-closed resolver in
  `krishna_story_factory/publication/fonts.py`, returning
  `resolve_unicode_fonts().pillow_bold(size)` or `.pillow_regular(size)`.
  `ImageFont.load_default()` is gone from this module, including from the
  test-mode placeholder helpers.
- `compose_poster` calls `assert_text_renderable(font, [text], context=…)`
  for the title and the caption before drawing, so a font without the needed
  glyphs raises instead of producing tofu.
- `publication/fonts.py::_glyph_missing` now compares each rendered glyph
  against the font's own `.notdef` raster. The previous width-only check
  passed a `.notdef` box, because a box has a perfectly ordinary advance width.
- The two alternate compositors, `visuals/poster_compositor.py` and
  `visuals/line_art_compositor.py`, were switched to the same resolver so the
  defect cannot reappear through another entry point.

## 5. How the released posters were repaired

`scripts/fix_story_poster_unicode.py` never re-renders artwork and never calls
a provider:

1. Read the clean pre-credit master from
   `output/_archive/pre-copyright/<NNN>/2.0/story_poster.png`. The broken live
   poster is not used as a rendering source.
2. `publication/poster_text.py::derive_poster_geometry` inverts the band
   arithmetic of `compose_poster` to recover the exact artwork rectangle, and
   `extract_poster_art` crops it out unmodified.
3. Recompose the title and caption over that artwork with the resolved Unicode
   fonts, then append exactly one credit strip.
4. **Wording guard.** `verify_legacy_text_preserved` redraws the candidate
   title and caption with `ImageFont.load_default()` and requires the result to
   match the superseded poster's bands byte-for-byte. This proves the rebuild
   changed the typeface and nothing else. Story 009's caption keeps its source
   spelling `anyone's` with a straight apostrophe, exactly as `story.md` line 65
   reads; only the `Kṛṣṇa’s` apostrophe is typographic.
5. Verify zero `.notdef` boxes in all three bands with
   `count_missing_glyph_boxes`, which template-matches the band's ink against
   the `.notdef` raster and so needs no knowledge of the intended string.
6. Carry the other seven package files over byte-for-byte, stamp the Rights
   version in `story.md`, rewrite the manifest hashes, and swap the package
   atomically after archiving the predecessor.

## 6. Evidence in this folder

| File | Content |
| --- | --- |
| `009-poster-full.png` | Corrected Story 009 poster |
| `009-poster-title.png` | Corrected title band — `Pūtanā — Kṛṣṇa’s Astonishing Mercy` |
| `009-poster-caption.png` | Corrected caption band |
| `009-poster-credit.png` | Credit strip |
| `009-poster-superseded-*.png` | The same crops from archived `2.1.1-copyright`, showing the boxes |
| `007-poster-*.png` | The same set for Story 007 |
| `glyph-validation.json` | Per-band `.notdef` box counts, fonts, hashes, artwork-identity check |

Regenerate with:

```powershell
.\.venv\Scripts\python.exe scripts\build_poster_closeout_evidence.py
```

Regression coverage lives in `tests/test_poster_text_glyphs.py`, which
discovers band-bearing posters from `output/` rather than hardcoding a list, so
a future story with diacritics is covered automatically. It also asserts that
the superseded 007 and 009 posters still *fail*, keeping the detector honest.
