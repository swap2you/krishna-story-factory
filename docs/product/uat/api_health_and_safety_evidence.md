# Live API Evidence — Bhāva Portal V1

Captured by starting `bhava_api` with `uvicorn` directly against the real `output/` catalog
(`BHAVA_REPOSITORY_ROOT` pointed at the repository, `data/catalog/bhava.sqlite` redirected to
local disk only to avoid a network-mount SQLite locking artifact in the review sandbox — see
`00_METHODOLOGY_AND_LIMITATIONS.md`). No env vars beyond the defaults were changed;
`BHAVA_FACTORY_ACTIONS_ENABLED` was never set.

## Health

```
GET /api/v1/health
200 {"status":"ok","service":"bhava-api"}
```

## Stories catalog (all 7, correct order)

```
GET /api/v1/stories -> 200, 7 items, story_no 001..007 in order, quality_status "PASS" on all.
```
Titles confirmed: 001 The Earth Prays for Krishna to Come · 002 The Wedding and the Heavenly
Voice · 003 Vasudeva Keeps His Word · 004 Narada's Warning and Kamsa's Decision · 005 Prayers by
the Demigods for Lord Krishna in the Womb · 006 The Birth of Lord Krishna · 007 Kamsa Begins His
Persecutions. Each entry carries `poster_url`, `narration_url`, `story_md_url`.

## Factory Studio safety — live negative tests

```
GET /api/v1/local/status (default localhost host)
200 {"loopback_only":true,"factory_actions_enabled":false,"csrf_token":"<random, non-empty>"}

GET /api/v1/local/status  -H "Host: evil.example.com"
403 Forbidden   <-- loopback host enforcement confirmed live

POST /api/v1/local/generate-next   (no CSRF header)
403 Forbidden   <-- CSRF enforcement confirmed live

GET /api/v1/local/queue -> 200, read-only JSON (no mutation endpoint exists)
```

`tests/portal/test_api_read_only.py::test_public_catalog_endpoints_and_disabled_factory` also
confirms that even a **valid** CSRF-authenticated call to `POST /api/v1/local/generate-next`
returns `{"status": "disabled"}` while `BHAVA_FACTORY_ACTIONS_ENABLED` is unset — Story 008
cannot be produced through this API under any request observed in this session.

## Media/content-type

```
GET /api/v1/stories/007/assets/manifest.json -> 200, content-type application/json
GET /api/v1/stories/007/assets/story.md      -> 200, content-type present
GET /api/v1/stories/007/assets/%2e%2e%2f.env -> 404   <-- path traversal rejected
```

## CORS

`apps/api/bhava_api/main.py` registers `CORSMiddleware` with an explicit allow-list
(`http://localhost:3000`, `http://127.0.0.1:3000`, `:3002` variants) — not a wildcard.

## Story package completeness on disk (all 7 packages)

`output/00{1..7}_*/` each contain exactly 8 files with non-trivial sizes: `activity_sheet.pdf`,
`coloring_page.png`, `manifest.json`, `narration.mp3`, `simple_coloring_page.png`, `story.md`,
`story_poster.png`, `whatsapp_caption.txt`. Example (`003_vasudeva-keeps-his-word/`):
narration.mp3 ≈ 3.4 MB, story_poster.png ≈ 1.6 MB, activity_sheet.pdf ≈ 76 KB — all non-empty.
