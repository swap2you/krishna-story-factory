# V1.3 CoWork Final UAT — Evidence Index

Companion evidence for `docs/reviews/BHAVA_V1_3_COWORK_FINAL_UAT.md`. All live testing was performed
against the already-running `cursor-v13` instance (`http://127.0.0.1:3007` web, `http://127.0.0.1:8003`
API) via the Claude-in-Chrome browser extension, driving the user's real Chrome browser on Windows.
One browser only — no second engine available this session.

## Session identity

- SHA tested: `cbe9bf7bfe026fa9f29ce2deee4a130241b5e997` (== local `HEAD` == `origin/feature/bhava-portal-v1`)
- Branch: `feature/bhava-portal-v1`
- `.bhava/instances/cursor-v13/runtime.json`: web `http://127.0.0.1:3007`, api `http://127.0.0.1:8003`,
  mode `production`, `collision: true` (preferred port 3005 was occupied — instance not restarted or
  reconfigured by this review)
- Repository working tree confirmed clean (via scratch-index `git status --porcelain`) both immediately
  before testing began and immediately before this report was written.

## Files in this evidence set

- `01_ROUTE_MATRIX.md` — full 39-route inventory from source, with live-visit status per route.
- `02_STORY_TAB_MATRIX.md` — per-story, per-tab coverage for Stories 001–007.
- `03_LINK_AND_REDIRECT_MATRIX.md` — `/blog → /knowledge` redirect proof and other redirect rules found in `next.config.ts`.
- `04_AUDIO_EVIDENCE.md` — full raw state captures for every DEF-06 trial this session (7 stories).
- `05_BRAND_ASSET_RENDER_MATRIX.md` — category-by-category brand asset wiring status, code references, screenshot IDs.
- `06_KNOWLEDGE_REQUIREMENT_TRACEABILITY.md` — requirement-by-requirement classification against the MyPilotDropbox blueprint.
- `07_KNOWLEDGE_RESOURCE_STATUS_COUNTS.md` — exact published/proposed counts, and the 348-vs-20 roadmap-import finding.
- `08_ACCESSIBILITY_RESPONSIVE_MATRIX.md` — what was and wasn't independently verified this session.
- `09_CONSOLE_NETWORK_SUMMARY.md` — console/network observations, including the transient audio-endpoint 503.
- `10_FACTORY_SAFETY.md` — queue/hash/scheduler/Drive/secrets verification.

## Key live checks and their direct evidence (summary)

**DEF-06 (audio playback) — NOT fixed, reproduced 8 times across all 7 stories this session.**
Full raw JSON in `04_AUDIO_EVIDENCE.md`. Every trial: `readyState` stuck at `0`, no `narration.mp3`
request ever appears in the network log after Play is clicked, despite the identical URL succeeding
immediately via manual `fetch()` (`200` HEAD, `206` ranged GET, correct headers). This directly
contradicts `docs/releases/BHAVA_V1_3_RELEASE_CANDIDATE.md`, `docs/reviews/BHAVA_V1_3_CODEX_TECHNICAL_REVIEW.md`,
`docs/reviews/BHAVA_V1_3_CLAUDE_ADVERSARIAL_REVIEW.md`, and `docs/product/uat/v1.3/uat-summary.json`,
all of which claim this defect is resolved.

**Brand assets — real improvement over V1.2, verified via code + live screenshots.** Library collection
covers and all Śrīmad-Bhāgavatam canto covers now render (`apps/web/components/collection-card.tsx`,
`apps/web/lib/brand-assets.ts`, `cantoCoverPath()`). Contact and FAQ hero images now render
(`brandSrc("hero-contact-page")` / `brandSrc("hero-faq-page")`). Section banners, learning icons,
empty-state illustrations, and social/OG images remain unwired — confirmed via `grep -rn` for each
asset-folder path across `apps/web/app` and `apps/web/components`, all returning zero matches; this
matches the "Deferred" section of the project's own `docs/brand/BHAVA_V1_3_ASSET_USAGE_AUDIT.md`.

**Knowledge Library — real, honestly-labeled thin-slice implementation; 348-item backlog not actually imported.**
File-first content at `content/knowledge/{articles,pathways,questions,roadmap}`, gated server-side by
`apps/web/lib/knowledge/loader.ts`'s `isPublic()` check (`visibility: "public"` AND `review_state` in an
allow-list). Direct route-guessing of a `proposed`-status pathway (`/knowledge/daily-practice`) correctly
404s. `/blog` genuinely 308-redirects to `/knowledge` (confirmed via `fetch(..., {redirect:'manual'})`
→ `type: "opaqueredirect"`). The real 348-record `topic_backlog.csv` from the research package was
**not** imported — `content/knowledge/roadmap/index.json` contains only 20 synthetic placeholder
records ("Backlog topic 1"–"Backlog topic 20"), though the file does honestly self-annotate as
"metadata only; not published content."

**Identity/privacy.** `og:description` on `/about`: "Devotional learning for children, parents, and
teachers — stewarded by Svarna Gauranga Das." No "Swapnil" or "swap2you" substring found anywhere in
the rendered HTML of `/about`. Contact page correctly shows only `svarnagaurangdas@gmail.com` /
Harrisburg, Pennsylvania.

**Factory safety.** `data/catalog/locked_queue_state.csv`: 7 `done`, 86 `pending`, chapter 008 =
`pending`. Live API `GET /api/v1/stories/008` → `404`. `git status --porcelain` empty throughout.

## Screens captured (screenshot IDs from this session)

| Screen / state | Screenshot ID |
|---|---|
| Homepage (`/`) | ss_6440ukdlq |
| `/library` (collection covers rendered) | ss_59990t1le |
| `/library/srimad-bhagavatam` (canto covers rendered) | ss_7410r2h2p |
| `/library/srimad-bhagavatam/canto/10` | ss_8554g7x5v |
| `/contact` (hero rendered) | ss_99547b5mt |
| `/faq` (hero rendered) | ss_1086d7aue |
| `/knowledge` home | ss_2284fmolc, ss_6313zoe7y, ss_775277ouo, ss_9182ogv3f |
| Story 001 Listen tab, before Play | ss_5212jvj17 |
| Story 001 Listen tab, after Play (button flipped to "Pause," audio still stuck) | ss_1588hvos3 |
| `/studio/knowledge` (honesty disclosure) | ss_1307ka50q |
| `/teachers`, `/sunday-school`, `/preachers`, `/prabhupada-vani`, `/printables` | ss_7121ghnsd, ss_8523x8quz, ss_9740gd780, ss_10358wrbe, ss_2303yha99 |
| `/privacy`, `/accessibility`, `/source-permissions` | ss_9260assfh, ss_0467rrlo0, ss_1852g1l2m |

## Repository changes made by this review

Only the following paths were added by this UAT session:

- `docs/reviews/BHAVA_V1_3_COWORK_FINAL_UAT.md` (the report)
- `docs/product/uat/v1.3/cowork-final/**` (this evidence set)

No application code, story package, queue file, scheduler file, or brand/knowledge content file was
touched. No cowork-local instance was started this session (the already-running `cursor-v13` was
healthy and used as-is), so no instance stop was required at the end of this review.
