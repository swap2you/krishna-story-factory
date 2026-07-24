# V1.4 Audio Evidence — DEF-06 reproduced on all 7 released stories (4th consecutive release)

## Verdict-relevant summary

Live, rendered-browser Play was tested on **all 7 released stories** (Chromium, genuine pointer click on the visible Play button, not simulated). On **every story**, the shared `<audio>` element never left `readyState 0` (`HAVE_NOTHING`), `currentTime` never advanced past `0`, `duration` stayed `null`, and **no `narration.mp3` network request was ever issued** by the audio element — despite the exact same URL succeeding instantly via manual `fetch()` (200/206, correct `content-length`, `content-type: audio/mpeg`, `accept-ranges: bytes`). This is the identical DEF-06 signature independently reproduced in the V1.2 and V1.3 CoWork UAT rounds. The release's own claim ("Live audio: Stories 001/006/007 — narration requests + readyState 4 + advancing currentTime", `BHAVA_V1_4_RELEASE_CANDIDATE.md`) and `docs/product/uat/v1.4/04_AUDIO_EVIDENCE.json` (`readyState: 4` for 001/006/007) are **contradicted by this session's independent live testing**.

## Per-story results (Play clicked, 3–6s settle time, JS state read directly from the DOM `<audio>` element)

| Story | src set correctly | readyState after Play | networkState | paused | currentTime | duration | narration.mp3 request seen? |
|---|---|---:|---:|---|---:|---|---|
| 001 The Earth Prays for Krishna to Come | yes | 0 | 2 | false | 0 | null | **No** |
| 002 The Wedding and the Heavenly Voice | yes | 0 | — | true | 0 | — | **No** |
| 003 Vasudeva Keeps His Word | yes | 0 | — | true | 0 | — | **No** |
| 004 Narada Warns Kamsa | yes | 0 | — | true | 0 | — | **No** |
| 005 Prayers by the Demigods | yes | 0 | — | true | 0 | — | **No** |
| 006 The Birth of Lord Krishna | yes | 0 | 2 | true | 0 | null | **No** |
| 007 Kamsa Begins His Persecutions | yes | 0 | 2 | true | 0 | null | **No** |

Deep-tested per the mission's requirement (001/006/007): full JS state capture before/after Play, `read_network_requests` filtered on `narration`, console check.

## Control test — confirms the backend and the network path are healthy

Manual `fetch('/api/v1/stories/001/assets/narration.mp3', {method:'HEAD'})` from the same page, same origin, same session:
```json
{"status":200,"ok":true,"headers":{"accept-ranges":"bytes","content-length":"3885356","content-type":"audio/mpeg","server":"uvicorn"}}
```
This proves the file is reachable, correctly typed, and range-capable. The defect is specifically that the `<audio>` element's own internal fetch is never issued when `.play()` is invoked — the failure is in media-element request issuance, not in the server.

One anomaly noted (not the root cause): the CDP network-request monitor independently logged this exact HEAD request completing with **503**, even though the page's own `fetch()` call reported `200 OK` with correct headers. The same 503-on-HEAD-only-in-the-monitor anomaly was noted in the V1.3 UAT round and is consistent with a transient proxy/monitor artifact, not a real server failure — it does not explain DEF-06, since DEF-06 itself is characterized by **zero** requests, not error-status requests.

## Root-cause isolation via `/dev/audio-lab`

`/dev/audio-lab` exists, is marked "LOCAL DIAGNOSTIC · NOT IN NAV", and is absent from the rendered public nav, `sitemap.xml`, and `robots.txt` disallow rules do not need to reference it since it isn't linked anywhere crawlable.

Running the lab's own "Run probes" action for story 001 produced this log (via manual `fetch()`/`Blob`, not the native element):
```
Probing story 001
HEAD next 200 ct=audio/mpeg cl=3885356
Range next 206 cr=bytes 0-1023/3885356
Blob bytes=3885356
```
All three manual probe paths (HEAD, Range GET, full Blob fetch through the Next.js media proxy) succeed cleanly.

Then the lab's own bare, isolated native `<audio>` control (labeled "C · Native controls", the exact same `src`) was played directly. Result:
```json
{"src":"http://127.0.0.1:3000/api/v1/stories/001/assets/narration.mp3","readyState":0,"networkState":2,"paused":false,"currentTime":0,"duration":null}
```
**Identical failure**, in complete isolation from the app's StoryPlayer React component. This localizes the defect: it is not a bug in the app's custom player logic (the same failure occurs on a bare, minimal `<audio>` tag). Native `<audio>`-element-driven HTTP request issuance is failing for this origin/URL in this render environment, while `fetch()`-driven retrieval of the identical byte stream succeeds every time.

**Implication for the "native + Blob fallback" claim** (`d6867e3 fix(audio): replace broken media lifecycle with verified native and blob playback`): whatever Blob-fallback logic exists in the shared `StoryPlayer` component, it did **not** rescue playback on any of the 7 live-tested stories in this session — all 7 exhibited the native-path failure with no fallback taking over (no Blob URL ever appeared on `currentSrc`, no loading state indicating a fallback attempt was observed).

## Section 5C (keyboard isolation) and 5D (Story 007 end state) — tested opportunistically

- Story 007 page: no link, card, or route reference to Story 008 found (`document.querySelectorAll('a')` filtered for `008` → empty array). Direct `GET /api/v1/stories/008` → `404 {"detail":"Story not found"}`. Direct navigation to `/stories/008` renders an honest "A story in preparation… Story 008 remains pending in the factory queue" placeholder (HTTP 200 shell, but every backing API call — `/sync`, `/source-links`, `/reflections`, `/shlokas` — returns 404 and no fabricated narration/text/Sanskrit is shown). This is an honest unpublished state, not a leak, though it is a softer signal than a hard 404 and worth product attention.
- Keyboard isolation (Coloring dialog Arrow/Space/Escape behavior while audio "plays") was **not independently exercised this session** — since audio never genuinely started playing on any story, there was no real playback to isolate against. This sub-check is untested, not passed.

## Conclusion

DEF-06 (audio playback) is confirmed **still broken on all 7 released stories**, for the fourth consecutive independently-tested release (V1.2, V1.3, and now V1.4). Per the mission's Section 18 verdict rule ("Return FAIL when: live audio fails on any released story"), this alone is release-blocking.
