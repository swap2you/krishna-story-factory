# Bhāva V1.2 UAT Evidence Index

**Date:** 2026-07-23  
**Instance:** `cursor-v12`  
**Web:** http://127.0.0.1:3004  
**API:** http://127.0.0.1:8002  
**Playwright:** 313 passed (`playwright_exit_code`: 0)  
**Branch tip at UAT:** `eec11b79868aa646593be5bce4d855eb4b6d4f5e`

## Files

| File | Purpose |
| --- | --- |
| `runtime.json` | Exact ports/PIDs |
| `uat-summary.json` | Suite result |
| `axe-results.json` | Captured via Playwright suites |
| `console-errors.json` | Captured via Playwright suites |
| `network-errors.json` | Captured via Playwright suites |
| `responsive-results.json` | Captured via Playwright suites |

## Notes

- Genuine Play click covered by Playwright on Chromium/Firefox/WebKit desktop (`currentTime` advances).
- WebKit mobile audio autoplay cases intentionally skipped (iOS policy).
- Brand READY blocked by 8 missing Phase-5 canto covers.
