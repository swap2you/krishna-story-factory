# V1.3 Console and Network Summary

## Console

Checked on: homepage, `/knowledge`, several story pages (001, 006, 007), `/knowledge/search`.

No application-level console errors or React hydration warnings were observed on any page visited.
The only console output captured all session came from an unrelated third-party browser extension
(`chrome-extension://bgnngbhjbcnamcaeffgeiapmihppgipg/content.06af5f40.js`, identifying itself as
"clipto-webext") logging its own initialization — not part of the Bhāva application and not evidence
of an app-level issue.

Not checked: every route in the full 39-route inventory (console was sampled on ~10 pages, not all).

## Network

Checked incidentally, primarily during audio testing (see `04_AUDIO_EVIDENCE.md`).

- All deliberate page navigations, RSC prefetch requests, and story asset requests (poster images,
  waveform JSON, reader text, source-links, reflections, shlokas) returned clean `200` status codes.
- Static asset requests (`_next/static/...`, fonts, brand logo) all returned `200` (or `304` on a
  cache-hit revalidation for the header logo when navigating between pages).
- One notable anomaly: during rapid back-to-back navigation between story pages, a stray, already
  in-flight `HEAD` request to a *previous* story's narration file
  (`/api/v1/stories/001/assets/narration.mp3`) was observed completing with status **503** after the
  page had already navigated away from it. A follow-up direct probe (6 consecutive `HEAD` requests to
  a different story's identical endpoint pattern, all issued deliberately and sequentially) all
  returned clean `200`. This reads as a transient contention/timing artifact under concurrent
  Next.js route prefetching rather than a systemic server fault, but it is reported as observed rather
  than dismissed, since it touches the exact same endpoint family implicated in DEF-06.
- Two `503` responses were also observed on RSC-prefetch requests (`/library/krishna-book?_rsc=...`,
  `/stories/002?_rsc=...`) during the same rapid-navigation window — suggesting the dev/production
  server under this instance may have a low concurrency ceiling that these UAT sessions' fast
  successive `browser_batch` navigations occasionally exceed. This is worth the team's attention as a
  possible contributing factor to intermittent behavior generally, though it was not the explanation
  for DEF-06 itself (DEF-06 reproduced with zero network requests at all, not with 503 responses).

## Performance

Not measured this session. No Lighthouse score, Core Web Vitals figure, or load-time number is
reported anywhere in this evidence set or the main report.
