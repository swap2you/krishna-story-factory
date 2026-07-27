# V1.7.3 CoWork UAT — Sequence Correction & Evidence Verification

## Git state (resolved live, not hard-coded)

- `git fetch origin feature/bhava-portal-v1` executed successfully this session.
- Local HEAD: `6e7c585dfbf7f1360a299da8913eb25d3401a78e`
- `origin/feature/bhava-portal-v1` (post-fetch): `6e7c585dfbf7f1360a299da8913eb25d3401a78e` → **local == origin CONFIRMED**
- Tested product SHA `aeb5104b8780b5a7a267db609060bfd870228a62` exists and resolves. Commits after it:
  - `919841d` docs: add Bhava v1.7.3 sequence-correction evidence and CoWork UAT prompt
  - `6e7c585` docs: set Bhava v1.7.3 evidence SHA in release candidate
  - `git diff --name-only aeb5104..HEAD` touches **only `docs/**`** → docs/evidence-only CONFIRMED.

## Sequence correction — every mission item independently verified

1. **Story 009 remains full Pūtanā**: `output/009_putana-krishnas-astonishing-mercy/` present; manifest `publishable: true`, `quality.status: PASS`, 8 outputs; title "Pūtanā — Kṛṣṇa's Astonishing Mercy". The published `story.md` passes the live coverage gate (`evaluate_package_text('009', …)` → ok, zero errors), independently re-run in this session's sandbox.
2. **Stories 001–009 unchanged**: recomputed SHA-256 for all **72 files** (9 stories × 8) against `docs/releases/BHAVA_V1_7_3_SAFETY_BASELINE.json` → **checked 72, missing 0, mismatched 0**.
3. **No `output/010_*`**: confirmed by directory listing (`_archive`, `_staging`, `_quarantine` etc. present; no 010 package).
4. **Next pending = Baby Kṛṣṇa Breaks the Cart**: live `tracking/queue_state.csv` row `010,baby-krishna-breaks-the-cart,pending,0` (Tṛṇāvarta correctly moved to `011`). Also verified programmatically: `read_next_pending()` → 010/cart (see test run below).
5. **Chapter 7 ledger majors, separately**: `kb7-utthana-cart` → [010], `kb7-trinavarta` → [011], `kb7-yawn-universal-mouth` → [012] (loaded via `load_coverage_ledger()` live).
6. **Chapter 8 ledger majors, separately**: `kb8-garga-name-giving` → [013], `kb8-crawling-adventures` → [014], `kb8-butter-complaints` → [015], `kb8-dirt-universal-form` → [016].
7. **Two universal-form manifestations separately mapped**: 012 (Ch7 yawn) vs 016 (Ch8 dirt-eating) — distinct events, distinct stories.
8. **Non-skipping guard rejects incomplete mappings**: `python3 -m pytest tests/test_coverage_non_skipping.py` executed **independently in this review's sandbox** (not just read from evidence): **17 passed in 0.74s**, including the rejection tests (incomplete Ch7, missing cart, missing yawn, collapsed Ch8, 010-as-Tṛṇāvarta-while-cart-uncovered, one-story-covering-both-universal-forms — all correctly rejected by `evaluate_ledger_integrity`).

## SHA-bound raw evidence audit (`docs/product/uat/v1.7.3/runs/20260727-163324-aeb5104/`)

- `metadata.json.product_sha` == mission product SHA — match.
- Folder is git-tracked (all 14 files listed by `git ls-files`).
- **Self-hash integrity**: recomputed SHA-256 of all 13 evidence files against `metadata.json.evidence_file_sha256` → **13/13 match**.
- Raw `pytest-full.txt` tail: `434 passed, 5 deselected, 1 warning in 49.43s` — matches `pytest-summary.json` and metadata counts.
- Raw `playwright-full.txt`: **415 literal `ok` lines counted** + tail `10 skipped / 415 passed (7.2m)` — matches summary/metadata. Skips = webkit-mobile autoplay-policy (documented in `skipped-tests.json`).
- `lint.txt`: 0 errors, 3 warnings. `typecheck.txt`: clean tsc. `unit.txt`: 2 passed. `build.txt`: successful production build. All exit codes 0 per metadata.
- `safety-hashes.json`: `stories_001_009_unchanged: true`, `story_010_present: false` — independently corroborated by this review's own 72-file hash check.

## Coverage gap found in the evidence (recorded as DEF-V173-05)

`apps/web/e2e/v14-audio-all-stories.spec.ts` `STORIES = ["001" … "008"]` — **Story 009 has no "play advances currentTime" automated test** in the official run (confirmed by grep: no `story 009 play advances` line in `playwright-full.txt`; 009 coverage there is navigation-linkage only). Combined with this session's environment being unable to exercise media playback at all (see SCREENSHOT_INDEX.md Listen row), **Story 009's audio playback has not been directly demonstrated by either the automated evidence or this live review** — its asset integrity (bytes/servability/manifest agreement) and the player's identical code path across stories are the supporting evidence. Recommended: add "009" to the STORIES array (one-line change) and re-run before release.
