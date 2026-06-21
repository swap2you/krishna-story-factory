# Activity and Line Art Release Report

## Release status

- Branch: `fix/adaptive-activities-and-character-lineart`
- Commit: this release commit, message `Add adaptive story activities and character-accurate line art`
- Overall: **PASS**

## Locked components

The component rebuild preserved `story.md`, `narration.mp3`, `story_poster.png`, `whatsapp_caption.txt`, queue state, WhatsApp behavior, and the seven-file output contract. WhatsApp was not sent.

Locked SHA-256 evidence:

| Story | File | SHA-256 |
|---|---|---|
| 001 | `story.md` | `AD6B1FF16CDD8BD1EA0A501AA9B9BCC48C38CB8956A1709CEEE8BE2B59EBD842` |
| 001 | `narration.mp3` | `7D2EE79B50D048222BF6504CB8BB0A907EBF9709168A222B4DCDD787B6EF3932` |
| 001 | `story_poster.png` | `A0229FA3BFC4F1D33F8F30A58D6B81BFCCCE28B290623310DC05896C15D145AA` |
| 002 | `story.md` | `8BD8E972973501AD97142D339E38A5ABCA80581AF178ABB259800F055FB9FC8D` |
| 002 | `narration.mp3` | `6F8E2B849D246E63D69376294CCC4E63B610B1B5389735B6D65A1A0BA2C1AB39` |
| 002 | `story_poster.png` | `1559CCCF3294A3DA1FA904FC029268793B738073F88A946D90C88621BBD5BD1A` |

Queue SHA-256 remained `6F72BB25F210B79CF4DBCEF460C47D27F39ABA08EAC30ED51A2FC70B743E7B62` during both rebuilds.

## PyMuPDF fallback decision

PyMuPDF is optional and no longer a required dependency. PDF validation uses PyMuPDF when already installed. Otherwise it locates Poppler `pdftoppm`, renders every page, verifies rendered page count, checks meaningful-content bounds and blank-page ink coverage, and returns clear `PDF_RENDERER_UNAVAILABLE`, `PDF_RENDER_FAILED`, or `PDF_RENDER_INCOMPLETE` diagnostics.

## Bounded image requests

- Fresh OpenAI client for every API attempt
- `httpx.Timeout(connect=30, write=60, read=360, pool=30)`
- SDK `max_retries=0`
- One application-controlled retry for timeouts/transient connection or server errors
- One candidate generated at a time; later candidates occur only after QA failure
- Maximum two repair rounds
- Clear `COLORING_API_TIMEOUT` / `COLORING_API_ERROR` failure
- Poster supplied as image 1; optional line-art reference supplied only when present
- Configured `gpt-image-1` is explicitly overridden to `gpt-image-2`; the override is printed and recorded in each manifest

## Isolated image smoke test

Command: `python scripts/test_coloring_generation.py --chapter 001`

- Result: PASS
- Elapsed: 74.4 seconds
- Poster reference: used
- Style reference: not present
- Identity score: 96
- Overall score: 95
- Peacock-feather violation: none
- Final output and Drive: untouched by smoke test

## Final validation

| Story | Activity | Pages | Activity QA | Coloring identity | Coloring QA | Drive |
|---|---|---:|---:|---:|---:|---|
| 001 | Prayer Petal Wheel | 1 | 93 | 96 | 94 | UPLOADED |
| 002 | Build the Wedding Chariot | 2 | 88 | 98 | 96 | UPLOADED |

Manual image QA rejected the first story 001 generated coloring despite its automated score because Vishnu had a feather-like crown ornament. The final candidate removed it. Story 002 manual QA confirmed adult Devaki and Vasudeva, Kamsa driving with a concerned expression, Vasudeva calm/protective, dignified Devaki, no peacock feathers, and no Krishna-like ornaments.

Both local folders contain exactly seven final files.

## Drive replacement

Only `activity_sheet.pdf`, `coloring_page.png`, and `manifest.json` were replaced.

- Story 001 existing folder: `1_7R1uj_WtW0CfuhfMAz_d3FSF1zsHbo-`
  - Activity modified: `2026-06-21T15:29:20.488Z`
  - Coloring modified: `2026-06-21T15:29:22.404Z`
  - Manifest modified: `2026-06-21T15:29:24.476Z`
  - Final file count: 7
- Story 002 existing folder: `1pr9ZMwnzE8bx7mgreAguduQFDzc8XC0V`
  - Activity modified: `2026-06-21T15:29:49.908Z`
  - Coloring modified: `2026-06-21T15:29:51.899Z`
  - Manifest modified: `2026-06-21T15:29:54.271Z`
  - Final file count: 7

Story 001's old manifest pointed to the parent Drive folder. Replacement was refused before mutation, the existing story child folder was verified to contain exactly seven files, and the local manifest was corrected to that existing child ID. No folder was created.

## Tests

- Full suite: 55 passed
- Includes timeout/retry, fresh-client behavior, sequential candidate generation, Poppler fallback, locked-file preservation, authorized Drive scope, and seven-file contract coverage
- `git diff --check`: clean

## Known limitations

- Activity QA and image QA remain model-based and can miss visible defects; manual comparison remains required. This release caught and corrected one such story 001 identity defect.
- The local `.env` still names prohibited `gpt-image-1`; runtime explicitly logs and records the override to `gpt-image-2`. Updating the private environment value later would remove the override message.

## Required release output

```text
ACTIVITY + LINE ART RELEASE - FINAL

Tests: PASS (55)
Image Smoke Test: PASS - 74.4s, identity 96, overall 95
Story 001 Activity: Prayer Petal Wheel (1 page)
Story 001 Activity Score: 93
Story 001 Coloring Identity: 96
Story 001 Coloring Score: 94
Story 001 Drive: UPLOADED - 7 files
Story 002 Activity: Build the Wedding Chariot (2 pages)
Story 002 Activity Score: 88
Story 002 Coloring Identity: 98
Story 002 Coloring Score: 96
Story 002 Drive: UPLOADED - 7 files
Locked Files: PASS - hashes unchanged
Queue: PASS - unchanged
Git Commit: this release commit
Overall: PASS
```
