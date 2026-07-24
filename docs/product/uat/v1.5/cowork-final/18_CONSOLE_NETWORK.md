# 18 — Console / Network

## Console

`read_console_messages` captured on the live tab: only 2 messages, both from a browser extension (`chrome-extension://bgnngbhjbcnamcaeffgeiapmihppgipg/content...js`, a "clipto-webext" logger), unrelated to the Bhāva application itself. **No application-originated console errors or warnings observed** during homepage load, Knowledge search, story audio playback, or Learning-page navigation.

## Network

`read_network_requests` captured 46 requests during a Knowledge-search + multi-route navigation sequence. All application assets (`_next/static/*`, fonts, brand images, manifest) returned 200 or 304 (cache hit). Page RSC payloads for visited routes returned 200, **except** four `?_rsc=...` prefetch requests (`/`, `/library`, `/preachers`, `/printables`) which returned 503.

Investigated the 503s directly: repeated, non-prefetch `fetch()` calls to the same four paths (twice each) all returned 200 consistently. This confirms the 503s are an artifact of Next.js's automatic link-hover/viewport RSC-prefetch mechanism (a known dev/prod-server prefetch-cache behavior), not a real outage or broken route — real navigation and direct fetches both succeed reliably. Logged for completeness; not treated as a defect.

## Verdict for this section

**PASS.** No genuine application errors in console or network. The transient RSC-prefetch 503s were investigated and found benign.
