# Story 009 Poster Correction — Verification Note

**Branch tip / origin:** `6bd9508c6dc4958e0d32d9ca57b873a03d187bc6` (local HEAD == origin, confirmed via fetch + `git rev-parse`)
**Tested product SHA:** `023ebc10effe9719e2b5f5a64e3ed8edd77c3b3f` — bound in `docs/product/launch/runs/final-poster-20260729-120419-023ebc1/metadata.json`; the one commit after it (`6bd9508`) is evidence-only (`git diff --name-only 023ebc1..HEAD` → 2 files, both under `docs/product/launch/runs/...`).

## Verdict: READY FOR RELEASE

## Verification (independent, this session)

1. **HEAD == origin** — confirmed.
2. **Tested SHA evidence-bound** — confirmed.
3. **Title exact text** — pixel-zoomed render of `output/009_.../story_poster.png` reads **"Pūtanā — Kṛṣṇa's Astonishing Mercy"**, correct curly apostrophe, no missing glyphs. (`poster-fix-review/009_LIVE_title_zoom.png`)
4. **Caption exact text** — renders **"Kṛṣṇa's mercy is greater than anyone's faults."** One micro-observation, not a defect: the apostrophe after "Kṛṣṇa" is curly (’) but the apostrophe in "anyone's" is a plain ASCII tick — a punctuation-style inconsistency baked into the source caption string itself (confirmed in `manifest.json.publication.artifact_notes...caption_text`), not a rendering failure. No missing glyph either way. (`poster-fix-review/009_LIVE_caption_zoom.png`)
5. **No missing-glyph boxes** — confirmed in both bands by direct pixel inspection; manifest's own `poster_text_glyph_validation` records `missing_glyphs: []` for both.
6. **Bottom copyright strip** — "Bhāva design and publication © Svarna Gauranga Das · Dauji Publication" renders cleanly. (`poster-fix-review/009_LIVE_credit_zoom.png`)
7. **No duplicate strip** — exactly one credit strip present; compositor trace confirms "append exactly one credit strip."
8. **Sacred subjects unobstructed** — confirmed visually; evidence JSON records `sacred_subject_overlay: false`.
9. **Exact-eight + manifest hashes** — all 7 hashable files in `output/009_.../manifest.json` self-consistent (7/7 match).
10. **Previous version archived correctly** — `_pre_swap_20260729_112730` backup + new `..._PREVIOUS_VERSION.json` sidecar correctly record `backed_up_version: "2.1.1-copyright"`; the archived manifest itself also reads `2.1.1-copyright` (the CLOSEOUT-N1 labeling-sequence issue from the prior review is fixed).
11. **Narrative/narration unchanged** — `story.md` diff vs. the 2.1.1 backup is the version-stamp line only; `narration.mp3` byte-identical. Only `story_poster.png` actually changed in this swap (confirmed via `rights.sha256` vs `rights.prior_version_sha256` diff across all 7 files).
12. **Tests green** — committed `pytest-full.txt`: 540 passed, 0 failed, 5 deselected; live spot re-run of `test_poster_text_glyphs.py` progressing clean (30/30, no failures, environment too slow to finish in-session); lint/typecheck/prod npm audit (0 vulnerabilities) all clean in the same evidence run. `apps/web/` untouched by this fix (Python/image-generation only), so the previously-audited Playwright/axe matrix still applies unchanged.
13. **Story 010 pending/absent** — `output/010_*` absent; `tracking/queue_state.csv` still `status: pending`, `completed_at` empty. (Note: `attempts` ticked 0→2 with no error and no completed_at — outside this commit's diff, `tracking/` is git-untracked; not a generation, not investigated further as out of scope for this review.)

Story 007 (also corrected by the same commit) was spot-checked as a bonus: its caption "Yoga-māyā warns Kaṁsa; soft hearts need good association." now renders correctly too.

## Files delivered by this review

- `docs/reviews/BHAVA_STORY_009_POSTER_FIX_REVIEW.md` (this note)
- `docs/product/launch/closeout/poster-fix-review/` — 6 PNGs: title/caption/credit zooms, full corrected poster, coloring page, Story 007 caption zoom
