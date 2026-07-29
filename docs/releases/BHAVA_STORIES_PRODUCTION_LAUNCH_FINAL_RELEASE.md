# BHĀVA STORIES PRODUCTION LAUNCH — FINAL RELEASE

**Status:** RELEASE FROZEN  
**Branch:** `feature/bhava-portal-v1`  
**Product SHA (tested):** `023ebc10effe9719e2b5f5a64e3ed8edd77c3b3f`  
**Evidence run:** `docs/product/launch/runs/final-poster-20260729-120419-023ebc1/`  
**Package artifact version:** `2.1.2-copyright` (Stories 007 and 009 only)  
**Not a new numbered product release.** This is an artifact correction inside the existing production launch.

## Verdict

CLOSEOUT-B1 is closed. Story 009 and Story 007 poster title/caption bands render Sanskrit diacritics with the validated Unicode font. The archive-version sequencing issue is corrected. Story 010 was not generated. The MWF scheduled task is disabled for freeze.

## What was fixed

| Item | Result |
| --- | --- |
| CLOSEOUT-B1 Story 009 poster diacritics | Fixed — title and caption render without missing-glyph boxes |
| Story 007 caption diacritics (same defect class) | Fixed in the same controlled pass |
| Archive backup version labeling (CLOSEOUT-N1) | Fixed — `_PREVIOUS_VERSION.json` sidecar records true prior version |
| Devotional narrative / narration | Unchanged |
| Providers / Drive / Story 010 | Not invoked during the product fix; noon backup failed closed |

## Product SHA and fonts

- **Product commit:** `023ebc1` — `fix(poster): render poster title and caption with the Unicode font resolver`
- **Unicode font regular:** `C:\Windows\Fonts\arial.ttf`
- **Unicode font bold:** `C:\Windows\Fonts\arialbd.ttf`
- **Poster rebuild source:** clean `2.0` artwork masters under `output/_archive/pre-copyright/{007,009}/2.0/`

## Package state

| Story | Version | Exact-eight | Poster |
| --- | --- | --- | --- |
| 007 | `2.1.2-copyright` | yes | Caption `Yoga-māyā` / `Kaṁsa` clean |
| 009 | `2.1.2-copyright` | yes | Title `Pūtanā — Kṛṣṇa’s Astonishing Mercy` clean |

Superseded `2.1.1-copyright` packages are archived and still fail the tofu detector (regression guard).

## Final matrix

Evidence directory: `docs/product/launch/runs/final-poster-20260729-120419-023ebc1/`

| Gate | Result |
| --- | --- |
| Python `pytest -m "not slow"` | 540 passed, 0 failed, 5 deselected |
| Poster glyph suite | 61 passed |
| `npm ci` | ok |
| `npm audit --omit=dev` | 0 vulnerabilities |
| lint | 0 errors (3 warnings) |
| typecheck | ok |
| unit | 2 passed |
| production build | ok |
| Playwright | 608 passed, 0 failed, 3 skipped (WebKit-mobile autoplay only) |

## Visual evidence

- Automated crops: `docs/product/launch/final-poster-closeout/`
- CoWork READY FOR RELEASE zooms: `docs/product/launch/final-poster-closeout/cowork-final/`
- Independent CoWork note: `docs/reviews/BHAVA_STORY_009_POSTER_FIX_REVIEW.md`

## Scheduler and Story 010 safety

| Event | Result |
| --- | --- |
| 10:00 AM MWF run | FAILED — `[Errno 22] Invalid argument`; partial worktree only; no `output/010_*` |
| 12:00 PM backup | FAILED — production recovery gate; exit 1; no provider generation; no Drive upload |
| Task state at freeze | **Disabled** (`Krishna Story Factory MWF`) |
| Queue | `009 done` / `010 pending` (attempts=2) |
| `output/010_*` | absent |

Details: `scheduler-final-state.json`, `queue-safety.json`.

## Freeze rules

- No product code changes after `023ebc1`.
- No Story 010 generation.
- No provider or Drive mutation during closeout.
- No new release number, PR, or merge.
- Re-enable the MWF task only by explicit operator decision after freeze acceptance.
