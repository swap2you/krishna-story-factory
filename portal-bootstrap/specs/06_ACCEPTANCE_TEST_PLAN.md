# Acceptance and Test Plan

## Factory preservation
- Existing full Python suite stays green.
- Story generation behavior is unchanged.
- Scheduler, queue and Drive behavior are unchanged.
- Stories 001–007 and release tags are unchanged.
- Portal reads packages through adapters.

## Public UX
- Home, library, collection, story, teacher, about and contact pages work.
- Mobile, tablet and desktop layouts pass.
- Every story asset is visible only when present.
- Audio player supports play/pause, seek, ±15 seconds and 0.75–2× speed.
- PDF displays with fallback, downloads and prints.
- Images open and download.
- Markdown is sanitized and beautifully rendered.
- Local notes persist without server storage.
- Bookmarks and playlists persist on-device.

## Local studio
- Public routes cannot invoke factory operations.
- Local gateway binds only to loopback.
- One production run at a time.
- Run actions use existing approved commands.
- Queue advances only through the existing pipeline.
- Logs are streamed without exposing secrets.

## Automated gates
- Python unit/integration tests
- TypeScript checks
- ESLint
- Next.js production build
- Vitest
- Playwright Chromium/Firefox/WebKit
- axe accessibility scans
- visual screenshot baseline
- secret scan
- dependency audit
- API schema validation
- package contract tests

## Browser validation
Cursor must open the local app in a real browser and verify:
- all primary routes
- navigation
- story player
- PDF fallback
- download links
- notes
- responsive modes
- keyboard navigation
- no console errors
