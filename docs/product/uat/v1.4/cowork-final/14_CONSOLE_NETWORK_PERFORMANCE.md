# V1.4 Console, Network, and Performance

## Console

Checked on: homepage, stories 001–007, `/knowledge`, `/knowledge/search`, `/dev/audio-lab`, `/dev/logo-sheet`, `/studio/knowledge`, `/contact`. No application-level console errors were captured (`read_console_messages` with `onlyErrors: true` returned "No console errors or exceptions found" after the Studio sign-in flow). The only console output seen at any point was an unrelated third-party browser extension (`clipto-webext`) logging its own initialization — not part of the Bhāva application.

## Network

- Static assets (`_next/static/*`, fonts, brand images) all returned 200 (or expected caching behavior).
- Story supporting-data endpoints (poster, waveform, reader, sync, source-links, reflections, shlokas) all returned 200 across every story visited.
- narration.mp3 correctly never requested on page load (lazy-load architecture is correct) but never requested on Play either (see `05_AUDIO_EVIDENCE.md` — this is the core defect).
- RSC-prefetch 503s observed during rapid navigation (see `02_ROUTE_MATRIX.md`) — a known, previously-documented transient artifact, not a page-load failure.
- One HEAD request to `narration.mp3` was independently logged as 503 by the network monitor while the identical `fetch()` call reported 200 with correct headers in the same call — an unexplained monitor/proxy discrepancy noted for completeness, not treated as the root cause of DEF-06.

## Performance

**Not measured this session.** No Lighthouse score, Core Web Vitals figure, or load-time number is reported anywhere in this evidence set. The mission requires recording "actual Lighthouse or equivalent scores" and explicitly forbids inventing or estimating them — none are provided, rather than fabricating placeholder numbers.
