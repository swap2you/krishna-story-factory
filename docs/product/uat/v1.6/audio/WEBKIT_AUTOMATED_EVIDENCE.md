# WebKit automated audio evidence — V1.6

## Findings

Playwright WebKit on Windows rejects `blob:audio/mpeg` (`MEDIA_ERR_SRC_NOT_SUPPORTED`). Product path: mark blob unsupported → native allowlisted `narration.mp3` in-gesture.

## Automated coverage

- `e2e/v14-audio-all-stories.spec.ts` — stories 001–008 on webkit-desktop
- `e2e/v12-audio-routes.spec.ts` — blob or native `currentSrc` accepted
- Narrow skip remains for **webkit-mobile** autoplay policy only

## Claim boundary

Automated WebKit desktop native playback is evidenced. Real Safari/iOS is **not** claimed verified — see manual checklist.
