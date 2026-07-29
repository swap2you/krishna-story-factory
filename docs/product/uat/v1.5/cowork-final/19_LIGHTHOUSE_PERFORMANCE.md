# 19 — Lighthouse / Performance

## Lighthouse — infeasible from this sandbox (disclosed, not substituted silently)

The live application runs on the user's own Windows machine (`127.0.0.1:3005`/`8003`), reachable only through the Claude-in-Chrome browser connection, not through this review's Linux bash sandbox network. Lighthouse's CLI/Node tooling in the sandbox has no network path to `127.0.0.1:3005` on the user's machine, so a genuine Lighthouse run could not be executed this session. This matches the mission's own non-blocking allowance: *"Lighthouse could not run for a documented tooling reason while no performance blocker was otherwise found."* The release notes (`BHAVA_V1_5_RELEASE_CANDIDATE.md`) independently disclose the same limitation: "Lighthouse not in CI; axe critical/serious covered via Playwright."

## Substitute proxy metrics (Performance/Navigation Timing API)

As a lightweight substitute, the browser's native `performance` API was queried live on `/library`:

| Metric | Value |
|---|---|
| `domContentLoadedEventEnd` | 101 ms |
| `loadEventEnd` | 577 ms |
| `transferSize` | 8,776 bytes (this navigation entry only) |

These numbers are fast and show no obvious performance red flag, but they are **not a substitute for a real Lighthouse audit** (no Core Web Vitals, no Largest Contentful Paint, no accessibility/SEO/best-practices scoring). Treat as a directional sanity check only.

## Verdict for this section

**PASS WITH NON-BLOCKING NOTES**, per the mission's own explicit allowance for a documented Lighthouse-tooling-reachability gap with no otherwise-observed performance blocker.
