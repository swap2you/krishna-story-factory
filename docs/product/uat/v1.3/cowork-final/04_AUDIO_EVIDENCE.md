# V1.3 Audio Evidence (DEF-06)

All state captures below are raw `JSON.stringify()` output from `document.querySelector('audio')`,
read via `javascript_tool` in the live browser tab, against `cursor-v13` (`http://127.0.0.1:3007`).

## Story 001, trial 1 — `find`-located ref, click, wait 2s then 4s

Pre-click:
```json
{"src":"http://127.0.0.1:3007/api/v1/stories/001/assets/narration.mp3","currentSrc":"http://127.0.0.1:3007/api/v1/stories/001/assets/narration.mp3","readyState":0,"networkState":2,"paused":true,"currentTime":0}
```
+2s after click:
```json
{"t":"+2s","currentSrc":"http://127.0.0.1:3007/api/v1/stories/001/assets/narration.mp3","readyState":0,"networkState":2,"paused":true,"currentTime":0,"duration":null,"error":null}
```
+4s after click:
```json
{"t":"+4s","readyState":0,"networkState":2,"paused":true,"currentTime":0,"duration":null}
```
Network log (`read_network_requests` filtered `urlPattern:"narration"`, tracking active since before
the click): **no requests matching "narration" found.**

Console: no errors. Screenshot `ss_5212jvj17` shows the button still reading "Play" (the click did not
even produce the optimistic UI flip this time).

## Story 001, trial 2 — coordinate click (258,230), wait 1s then 3s more

Post-click (+1s), screenshot `ss_1588hvos3`: button now reads **"Pause"** (optimistic UI state changed).
JS state at +4s total:
```json
{"readyState":0,"networkState":2,"paused":false,"currentTime":0}
```
`paused: false` confirms the app believes playback started (`audio.play()` was called and its promise
did not reject), yet `readyState` never left `0` and `currentTime` never advanced.

## Story 006 — coordinate click, network tracking started before click

Post-click (+4s):
```json
{"story":"006","readyState":0,"networkState":2,"paused":true,"currentTime":0}
```
Network log filtered `urlPattern:"narration"`: **no requests matching "narration" found.**
(Note: a full unfiltered network dump taken at page load for this story, before the click, incidentally
showed a **stray `HEAD` request to `/api/v1/stories/001/assets/narration.mp3` — the previous story's
audio file — returning `503`.** This looks like a leftover in-flight request from the prior page,
observed during rapid back-to-back navigation. It is reported as observed; see follow-up probe below.)

## Story 007 — coordinate click, network tracking started before click

Post-click (+4s):
```json
{"story":"007","readyState":0,"networkState":2,"paused":true,"currentTime":0}
```
Network log filtered `urlPattern:"narration"`: **no requests matching "narration" found.**

## Stories 002–005 — smoke test (single click, 3s wait, state read)

```json
{"story":"002","readyState":0,"paused":true,"currentTime":0}
{"story":"003","readyState":0,"paused":true,"currentTime":0}
{"story":"004","readyState":0,"paused":true,"currentTime":0}
{"story":"005","readyState":0,"paused":true,"currentTime":0}
```
Network requests were not separately captured for these four (smoke test only, per the mission's own
instruction to do deep testing on 001/006/007 and smoke testing on 002–005).

## Server-health control checks (ruling out a server-side cause)

Six consecutive `HEAD` requests to `/api/v1/stories/007/assets/narration.mp3` via `fetch()`, all in the
same page context immediately after the failed Play attempt:
```json
[{"i":0,"status":200,"ct":"audio/mpeg"},{"i":1,"status":200,"ct":"audio/mpeg"},{"i":2,"status":200,"ct":"audio/mpeg"},{"i":3,"status":200,"ct":"audio/mpeg"},{"i":4,"status":200,"ct":"audio/mpeg"},{"i":5,"status":200,"ct":"audio/mpeg"}]
```
Ranged GET (`Range: bytes=0-1023`):
```json
{"status":206,"cr":"bytes 0-1023/4527043","cl":"1024"}
```
Full response headers on a HEAD request:
```json
{"accept-ranges":"bytes","content-length":"4527043","content-type":"audio/mpeg","date":"Fri, 24 Jul 2026 03:04:42 GMT","etag":"\"b142691df462e88fa301a232f35a0c15\"","last-modified":"Wed, 22 Jul 2026 18:38:37 GMT","server":"uvicorn"}
```
No `Content-Security-Policy` meta tag present on the page.

## Interpretation

The identical URL that the `<audio>` element uses (`currentSrc`) succeeds immediately, repeatedly, and
correctly (200/206, correct headers, Range support working) when fetched via JavaScript `fetch()` in
the same page. But the native `HTMLMediaElement` never issues any request for it at all — the network
log shows zero `narration.mp3` requests after Play is clicked, in every trial where request tracking
was active before the click. This rules out server unavailability, a missing file, a CORS block, and a
CSP block as causes, and narrows the fault to the browser's native media-loading pipeline for this
specific `<audio>` element (e.g., something about how `src`/`preload`/`load()` interact for this
element in this page, which was not further root-caused in this UAT session — that is an engineering
debugging task, not a QA task).

This directly contradicts:
- `docs/releases/BHAVA_V1_3_RELEASE_CANDIDATE.md`: "DEF-06 media proxy + player lifecycle" (delivered)
- `docs/reviews/BHAVA_V1_3_CODEX_TECHNICAL_REVIEW.md`: "audio `preload=auto` + Play from user activation"
- `docs/reviews/BHAVA_V1_3_CLAUDE_ADVERSARIAL_REVIEW.md`: "Mitigated via Next media proxy + lifecycle"
- `docs/product/uat/v1.3/uat-summary.json`: `"Audio Play re-verified final_audio=0 on chromium-desktop after rebuild"`
