# Bhāva Stories Production Launch — Final Closeout UAT

**Branch:** `feature/bhava-portal-v1`
**Branch tip (live-resolved):** `0b08e3e5f83d8083ade11078ba743b777a7bc133` — **local HEAD == origin confirmed** (`git rev-parse HEAD origin/feature/bhava-portal-v1` identical)
**Tested product SHA:** `91a6be16d8e5c1cc6069775646494334c48cf08f` ("Fix Unicode fonts and per-page PDF copyright footers for Stories 001-009") — exactly one docs-only commit (`0b08e3e`) after it; `git diff --name-only 91a6be1..HEAD` returns `docs/` paths only.
**Runtime:** `.bhava/instances/bhava-final/runtime.json` — web `127.0.0.1:3000` (PID 6228), API `127.0.0.1:8000` (PID 6656), mode production. Live port probe this session: **3000 and 8000 ALIVE; all historical ports (3001–3005, 8001–8003) dead.**
**Reviewer:** Independent CoWork closeout auditor. No product code, story packages, queue, scheduler, providers, Drive, or MyPilotDropbox modified. Story 010 not generated. No PR/merge. This report and its evidence are the only files added by this review.
**Evidence:** `docs/product/launch/closeout/` (this session) + the product team's own SHA-bound run `docs/product/launch/runs/final-release-20260728-190107-91a6be1/`

---

## Verdict: **BLOCKED**

One confirmed, reproducible defect directly fails an explicitly enumerated acceptance check (#9) and is visible in a customer-facing, printable/shareable asset. Per this mission's two-option contract, that is sufficient to withhold READY FOR RELEASE regardless of how clean the other 19 checks are.

**All other 19 checks PASS** on independent, this-session verification, including the two P3 defects from the immediately preceding UAT cycle (stale-footer-on-final-page-only, and diacritic tofu-boxes) — both are now genuinely fixed **inside the PDF pipeline**. The regression below was not caught by the product team's own evidence because their automated glyph check validates a different, narrower code path than the one that broke.

---

## Defect register

### CLOSEOUT-B1 — Blocking — Poster title/caption text renders Sanskrit diacritics as black-box glyphs (Story 009 only)

- **What I found:** `output/009_putana-krishnas-astonishing-mercy/story_poster.png` — the title bar reads **"P▢tan▢ ▢ K▢▢▢a's Astonishing Mercy"** (should be "Pūtanā — Kṛṣṇa's Astonishing Mercy") and the bottom caption reads **"K▢▢▢a's mercy is greater than anyone's faults."** (should be "Kṛṣṇa's mercy is greater..."). Every diacritic character (ū, ā, the em dash, ṛ, ṣ, ṇ) renders as a missing-glyph box. Directly fails mission check #9 ("Kṛṣṇa," "Pūtanā" ... render correctly with no black boxes) and #11 (poster credit strips have no missing glyphs, read in spirit as "poster overlay text").
- **Visual proof (this session, independently rendered/zoomed):** `docs/product/launch/closeout/visual-evidence/009_poster_title_zoom.png`, `009_poster_caption_zoom.png`, and the full poster `009-story_poster-DEFECT.png`.
- **What is NOT affected (all independently confirmed clean this session):**
  - The **PDF pipeline** — every one of the 33 pages across all 9 activity-sheet PDFs, independently rendered by this reviewer at 150–200 DPI and visually inspected (not just text-extracted): footer line "© Svarna Gauranga Das · Dauji Publication · A Bhāva Project publication" renders with a correct "Bhāva" glyph on every page; Story 007's body text renders "Yoga-māyā," "Durgā," "Kaṁsa," "Devakī," "Vaiṣṇavas and brāhmaṇas" perfectly; Story 009's own PDF pages render "Pūtanā — Kṛṣṇa's Astonishing Mercy" and "Kaṁsa" correctly in the title bar and body. See `footers_grid_A.png`, `footers_grid_B.png`, `007-pdf-page1-diacritics.png`, `007-pdf-page2-vaisnava-brahmana.png`.
  - The poster's own **bottom credit line** — "Bhāva design and publication © Svarna Gauranga Das · Dauji Publication" renders cleanly on both Story 001's and Story 009's posters (`001-story_poster-control.png`, visible in `009-story_poster-DEFECT.png`).
  - The **coloring-page credit strip** — Story 009's coloring page credit line "© Svarna Gauranga Das · Dauji Publication · Bhāva" renders cleanly (`009-coloring_page-control.png`).
  - The **live website** — `/stories/009` browser tab title renders "Pūtanā — Kṛṣṇa's Astonishing Mercy | Bhāva" correctly (real web font), fresh axe scan 0 violations.
- **Root cause (inferred from scope):** the `91a6be1` fail-closed Unicode font resolver (`krishna_story_factory/publication/fonts.py`) was wired into the PDF generator (`pdf/activity_sheet.py`) and into the poster's bottom credit-strip renderer, but not into the separate title-bar/caption text-compositing step used when building `story_poster.png`. That step still uses whatever font it used before the fix.
- **Why only Story 009 shows it:** of the 9 released titles, Story 009 is the *only* one whose canonical title/caption contains Sanskrit diacritics (`Pūtanā — Kṛṣṇa's Astonishing Mercy`, checked against all 9 manifests). Stories 001–008 have plain-English titles/captions, so this code path's bug is invisible on their posters — it is not that they are "fixed," it is that they never exercise the broken font.
- **Evidence-hygiene note:** the product team's own `docs/product/launch/runs/final-release-20260728-190107-91a6be1/image-credit-glyph-validation.json` samples `Bhāva`/`Kṛṣṇa`/`Pūtanā` and reports success — but by its own field name (`image-credit-glyph-validation`) and content (`strips_rebuilt_from_2_0_masters`) it validates the credit-strip renderer only, not the title/caption overlay. It is not a false claim, but its scope is narrow enough that it created a false sense of completeness. This is exactly the gap the mission's instruction to visually inspect rendered pages "rather than relying only on text extraction" was designed to catch — text extraction and the automated glyph-sample check both passed while the actual customer-facing image was broken.
- **Recommendation:** apply `fonts.py`'s resolver to the poster title-bar/caption compositing step, regenerate `story_poster.png` for Story 009, and extend the retrofit script's own validation to render and pixel/OCR-check the title and caption bands specifically (not just the bottom credit strip) for any title containing non-ASCII characters — this will also auto-cover any future story whose title contains diacritics.

### CLOSEOUT-N1 — P4, non-blocking — Archive version-label ahead of its own content

For all 9 stories, `manifest.json.rights.prior_version_sha256` correctly and completely matches the archived `*_pre_swap_20260728_185858` (or `_185859`) backup byte-for-byte (7/7 hashable files, all 9 stories) — the supersession chain is real and hash-verified, satisfying checks #4 and #5. However, that "immediately preceding" backup is itself already labeled `version: "2.1.1-copyright"` in its own manifest, identical to live, rather than `"2.1.0-copyright"`. This is because the retrofit script bumped the version stamp in `story.md`'s footer before the final PDF-only rebuild step, then took the safety backup. The true `2.1.0-copyright` content is separately and correctly archived one step further back (`*_pre_swap_20260728_185617/8`, confirmed `version: "2.1.0-copyright"` for all 9). Net effect: nothing is lost or misrepresented at the hash level, but a future auditor reading version labels alone (without hash-chasing, as this review did) could be confused about which backup is the "real" 2.1.0 predecessor. Recommend the retrofit script bump the version stamp only at the moment a swap-backup is taken, not before.

---

## Independent verification detail (all 20 checks)

| # | Check | Result | How verified this session |
|---|---|---|---|
| 1 | Local HEAD == origin | **PASS** | `git rev-parse HEAD origin/feature/bhava-portal-v1` → both `0b08e3e...` |
| 2 | Commits after tested SHA are evidence/docs only | **PASS** | `git diff --name-only 91a6be1..HEAD` → `docs/` only; one commit (`0b08e3e`) |
| 3 | Stories 001–009 exact-eight | **PASS** | Live Python re-hash: 9/9 packages complete, 63/63 file hashes self-consistent with manifests |
| 4 | Prior 2.1.0 copyright versions archived | **PASS** | `*_pre_swap_20260728_185617/8` present for all 9, each manifest confirms `version: "2.1.0-copyright"` |
| 5 | Corrected package versions have complete supersession histories | **PASS** (see CLOSEOUT-N1) | `prior_version_sha256` in live manifest matches archived immediate-predecessor backup 7/7 files, all 9 stories |
| 6 | Story narrative before Rights and Credits unchanged | **PASS** | Byte diff of `story.md`, 2.1.0-archive vs. live, all 9 stories: **only the version-stamp line differs**; `narration.mp3` byte-identical live vs. 2.1.0 archive (no TTS regen) for all 9 |
| 7 | Every activity PDF page has the compact footer | **PASS** | Independently rendered all 33 pages (9 PDFs) at 150 DPI, cropped footer bands, visually inspected in grid form — footer present and legible on every page |
| 8 | Every PDF retains a final detailed Rights and Credits page | **PASS** | All 9 final pages rendered and visually reviewed (`rights_grid.png`); identity/claim/not-claimed language consistent |
| 9 | Bhāva/Kṛṣṇa/Pūtanā/Rādhā/Vaiṣṇava render with no black boxes | **FAIL** (CLOSEOUT-B1) | PDF pipeline clean on all tested terms across all 9 stories; poster title/caption broken on Story 009 (the only story containing these terms in poster text). "Rādhā" does not appear anywhere in Stories 001–009's content (chronologically pre-Vraja pastimes) — untestable directly, but composed only of already-confirmed-clean glyphs (ā) plus plain ASCII |
| 10 | PDF footers stay within safe margins, no overlap | **PASS** | Visual inspection of all 33 rendered pages — footer sits in clear whitespace, no collision with body content on any page |
| 11 | Poster/coloring credit strips have no missing glyphs | **FAIL for poster title/caption** (CLOSEOUT-B1); credit-strip lines themselves PASS | Bottom credit lines clean on posters (001, 009) and coloring page (009); poster title/caption text broken on 009 |
| 12 | No credit strip covers sacred subjects | **PASS** | Posters (001, 009) and coloring page (009) visually reviewed — credit strips are separate bars above/below artwork, artwork fully unobstructed |
| 13 | Story 010 remains pending and absent | **PASS** | `tracking/queue_state.csv` live: `010,...,pending`; no `output/010_*` directory; live `/stories/010` renders only "A story in preparation" placeholder, no title/narrative leak |
| 14 | Raw successful WebKit notes rerun exists | **PASS** | `playwright-notes-webkit-rerun.txt`: `1 passed (17.2s)` |
| 15 | Complete final Playwright matrix has zero failures | **PASS** | `full-playwright-log.txt` raw grep: 608 passed, 0 failed, 3 skipped |
| 16 | Production npm audit remains zero | **PASS** | `npm audit --omit=dev --json` re-run live this session: 0/0/0/0/0 |
| 17 | Accessibility remains zero critical/serious | **PASS** | Fresh axe-core 4.9.1 (wcag2a+wcag2aa) run live this session on `/stories/009` and `/rights`: 0 violations each; `apps/web/` proven byte-identical to the prior fully-14-route-scanned cycle via `git diff` |
| 18 | Only one bhava-final runtime is active | **PASS** | Live port probe: only 3000 and 8000 alive; 3001–3005/8001–8003 dead; only one non-suffixed instance directory under `.bhava/instances/` |
| 19 | Queue, scheduler, providers, Drive unchanged | **PASS** | Live `queue_state.csv`: 009 done, 010–098 pending, unchanged; no scheduler trigger; no provider calls made by this review; Drive not reachable from this sandbox (disclosed limitation, consistent with all prior cycles); `MyPilotDropbox/` and `.bhava/` untracked in git |
| 20 | Final evidence is SHA-bound and complete | **PASS with the scope caveat above** | `docs/product/launch/runs/final-release-20260728-190107-91a6be1/metadata.json` binds `product_sha: 91a6be1`; folder contains matrix/audit/font/footer JSONs and partial renders; this review's own visual inspection went beyond that folder's scope to catch CLOSEOUT-B1 |

---

## Environment disclosures (carried forward, unchanged)

- This sandbox has no network path to the app host for OS-level process checks; runtime liveness is verified via the host browser's port probe, not Windows process inspection.
- Google Drive is not reachable from this environment; "Drive unchanged" is asserted from the absence of any provider/Drive code path being invoked by this review, not from a live Drive read.

## Files delivered by this review

- `docs/reviews/BHAVA_STORIES_PRODUCTION_LAUNCH_FINAL_CLOSEOUT_UAT.md` (this report)
- `docs/product/launch/closeout/visual-evidence/` — 11 PNGs: independently rendered PDF footer grids (33 pages), rights-page grid (9 stories), the defect poster and its zoomed title/caption crops, a control poster, a control coloring page, and two high-DPI PDF pages proving clean Kaṁsa/Devakī/Yoga-māyā/Durgā/Vaiṣṇava/brāhmaṇa rendering
- `docs/product/launch/closeout/fresh-axe-and-runtime-probe.json` — raw live axe + port-probe results
