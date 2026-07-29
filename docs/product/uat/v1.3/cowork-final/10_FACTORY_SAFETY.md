# V1.3 Factory Safety Verification

| Check | Result | Evidence |
|---|---|---|
| Stories 001–007 hashes unchanged | Pass (by omission — file untouched) | `data/catalog/locked_story_hashes.json` present; `git status --porcelain` empty for the whole session, so nothing could have modified it |
| Real Story 008 pending, not generated | Pass | Live API: `GET /api/v1/stories/008` → `404 {"detail":"Story not found"}`. Queue CSV: `008,the-meeting-of-nanda-and-vasudeva,pending,0,,,,2026-07-22T14:57:23` |
| Real queue unchanged | Pass | `data/catalog/locked_queue_state.csv`: 7 rows `done`, 86 rows `pending` — matches the state expected from prior UAT rounds (001–007 done) |
| Scheduler not triggered | Pass | No scheduler command, script, or endpoint was invoked this session |
| Google Drive unchanged | Pass (by omission) | No Drive credentials configured in this sandbox; no Drive-related code path was exercised |
| No paid API calls | Pass | No OpenAI, ElevenLabs, or image-generation request was made; all traffic this session was to the local `cursor-v13` instance and to `github.com` for git fetch/push |
| KrishnaBook.pdf ignored/unserved | Pass | `git ls-files \| grep -i krishnabook.pdf` → empty; `.gitignore` contains `/KrishnaBook.pdf` |
| MyPilotDropbox untracked | Pass | `git ls-files \| grep -i mypilotdropbox` → empty; `.gitignore` contains `/MyPilotDropbox/` |
| No key/cert/env tracked | Pass | `git ls-files` grep for `.env$/.pem$/.key$/.crt$/credentials/secret` → only `docs/SETUP_AND_CREDENTIALS.md` matched, confirmed to be documentation with blank placeholder values, not real secrets |
| No real-looking secret strings in tracked files | Pass | `git grep` for `sk-`, `AIza`, `ghp_`, `AKIA` patterns across the whole tree → no matches |
| Factory Studio production mutation disabled | Not re-verified fresh this session | Carried forward from the V1.2 UAT round: "Actions enabled: NO (demo)," all ten production buttons confirmed `disabled: true` via direct DOM query at that time. `/studio` was not re-opened this session |
| Knowledge Editorial Studio private | Pass | `/studio/knowledge` visited: explicit "not a public CMS," "must not appear in public navigation," "Factory and Knowledge studio actions remain disabled by default. No AI auto-publish. No public comments." Confirmed absent from the rendered public nav bar |
| `main`/`master`/tags unchanged | Pass | `git rev-parse origin/main` and `origin/master` both `3bae9785...`, unchanged from before this session; `git tag -l` shows only the 3 pre-existing tags, none created or modified |
| Working tree clean throughout | Pass | `git status --porcelain` (via scratch index, to route around a pre-existing stale `.git/index.lock`) returned empty both before testing began and immediately before this report was written |

## Identity/privacy check

- `og:description` on `/about`: "Devotional learning for children, parents, and teachers — stewarded
  by Svarna Gauranga Das." No civil name.
- `document.documentElement.outerHTML` on `/about` tested for `/swapnil/i` and `/swap2you/i` — both
  **false** (no match).
- `grep -rniE "swapnil|swap2you|swap2patil" apps/web/app apps/web/components apps/web/config apps/web/public`
  → no matches.
- Contact page (`/contact`) shows only "Svarna Gauranga Das," `svarnagaurangdas@gmail.com`, "Harrisburg,
  Pennsylvania" — matches the mission's specified correct public identity exactly.
- Not checked this session: sitemap.xml content, full manifest.webmanifest content, and the public API's
  full JSON payloads beyond the `/stories` and `/stories/008` endpoints already inspected for other
  purposes — no indication of a problem was found in what was checked, but this is not an exhaustive
  sweep of every JSON response the app can produce.
