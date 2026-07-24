# V1.3 Link and Redirect Matrix

## Configured redirects (`apps/web/next.config.ts`)

| Source | Destination | Type | Verified live? |
|---|---|---|---|
| `/vanani` | `/prabhupada-vani` | permanent (308) | Not tested this session |
| `/vani` | `/prabhupada-vani` | permanent (308) | Not tested this session |
| `/blog` | `/knowledge` | permanent (308) | **Yes** — confirmed via `fetch('/blog',{redirect:'manual'})` → `type:"opaqueredirect"`, and `fetch('/blog',{redirect:'follow'})` → resolves to `http://127.0.0.1:3007/knowledge`, status 200 |
| `/blog/:path*` | `/knowledge/:path*` | permanent (308) | Not tested this session |

This is a genuine Next.js `redirects()` config entry, not a client-side relabel. The old
`apps/web/app/blog/page.tsx` file still exists on disk with the stale "Bhakti Blog" copy but is
unreachable via normal navigation because the redirect fires first at the routing layer — confirmed
dead code, not a live inconsistency a user could encounter.

## Rewrite (API proxy)

`/api/:path*` → `${BHAVA_API_ORIGIN or BHAVA_API_URL}/api/:path*`. This is why story asset URLs
(e.g. `/api/v1/stories/001/assets/narration.mp3`) appear same-origin (port 3007) in the browser even
though they are actually served by the FastAPI backend (port 8003) — confirmed via the `server: uvicorn`
response header on a direct fetch to that same-origin path.

## Internal navigation clicked this session

Header nav (Home/Library/For Teachers/Prabhupāda Vāṇī/Knowledge/About/Contact), footer links
(Sunday School/For Preachers/FAQ/Printables/Privacy/Accessibility/Source & permissions), Library
collection cards (Krishna Book/Śrīmad-Bhāgavatam/Bhagavad-gītā/Rāmāyaṇa visible), Śrīmad-Bhāgavatam
canto cards (canto 10 opened), Knowledge pathway cards, Knowledge canonical-question links,
Printables "Open story" pattern (not clicked through), Preachers story-selector cards (not clicked
through to see outline generation).

## Not tested this session

- Exhaustive click-through of every link on every page (this was a representative navigation pass,
  not a full crawler).
- External links (e.g., "Open in Vedabase" on story Source tabs) were not clicked to confirm they
  resolve to a real external page.
- Breadcrumb navigation (e.g., `Home / Printables` seen on the Printables page) was not clicked.
- Previous/Next story navigation buttons (seen on story pages, e.g. "Story 002 →") were not clicked.
- Download links and print controls were not exercised this session (carried forward from prior UAT
  rounds, which did test these and found them working).

No broken images, dead-end pages, or console-visible failed requests were observed among the
navigation that was performed.
