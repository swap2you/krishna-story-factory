# V1.4 Git and Runtime Authority

## Repository state

| Check | Result |
|---|---|
| Branch | `feature/bhava-portal-v1` (confirmed via `git switch`, already on it) |
| `git fetch origin` / `git pull --ff-only` | Succeeded, already up to date |
| `git rev-parse HEAD` | `19afe6fd7548ff938dd9375c268acccc093947cf` |
| `git rev-parse origin/feature/bhava-portal-v1` | `19afe6fd7548ff938dd9375c268acccc093947cf` — matches HEAD and matches the mission's expected release SHA exactly |
| `git cat-file -t 19afe6f...` | `commit` — reachable and valid |
| `git diff --check` | Clean except benign CRLF-normalization notices on two JSON files |
| `main` / `master` | `origin/main` = `3bae97850ef8b934bbec3a48f42f92fbe6de169f`, unchanged; no `master` branch |
| Tags | `backup/pr8-pre-squash-7a26e80`, `v1.0.0-pilot-stories-001-006`, `v1.1.0-stories-001-007-operational` — unchanged, none created/modified this session |
| Secrets tracked | `git grep` for `sk-`, `AIza`, `ghp_`, `AKIA` patterns → no matches. `KrishnaBook.pdf` and `MyPilotDropbox/` both untracked and gitignored |

## Working tree cleanliness (exception, investigated and explained)

`git status --short` showed the tree **not byte-for-byte clean**:
```
M docs/product/uat/live/runtime.json
M docs/product/uat/live/uat-summary.json
```
Root cause, confirmed via `git diff` and `git show HEAD:...`: these two files are live-telemetry files that the running `cursor-v14` instance overwrites with fresh PIDs/timestamps on every restart. The **committed** (HEAD) values — not the locally-drifted values — are what this review treats as the frozen release evidence. Per the mission's instruction not to reset/rebase/discard legitimate work, these two files were left untouched. No application code, story asset, or safety-relevant file was modified.

Diff details:
- `runtime.json`: `web_pid` 83096→11880, `api_pid` 18136→1320, `started_at` `03:42:57Z`→`13:02:43Z` (instance restarted later same day — expected).
- `uat-summary.json`: **`playwright_exit_code: 1 → 0`** — this single-field drift is the seed of a much larger discrepancy documented in `15_AUTOMATED_MATRIX_AUDIT.md`. The committed value (`1`, i.e. FAIL) is what this review relies on, since it is the only value that is part of the reviewable, git-authenticated release.

## Commit history reviewed (`git log -30 --oneline`)

Starting SHA `018740b` (V1.3 CoWork commit, preserved) through HEAD `19afe6f`, the V1.4 feature sequence ran: safety baseline → defect/brand/knowledge matrices → **`d6867e3` fix(audio): replace broken media lifecycle with verified native and blob playback** → `8639868` fix(a11y) → `e3d11f5`/`05b21c0` brand/logo → `19fe7c5` **feat(knowledge): import the complete governed resource roadmap** → `491c4e2`/`fee1f20`/`6b2ceb9` Knowledge UX/search/editorial → **`6f968e8` test: complete Bhava v1.4 post-fix release gates** → **`22ff772` docs: add Bhava v1.4 final CoWork UAT prompt and live evidence** → five docs-only SHA-freezing commits to `19afe6f`.

**No commit between `22ff772` (which checked in a failing `uat-summary.json`, `playwright_exit_code: 1`) and `19afe6f` (HEAD) touches application code or re-runs the test suite.** The release was frozen at a SHA whose own committed automated-evidence file records a failing run. See `15_AUTOMATED_MATRIX_AUDIT.md`.

## Runtime instance

- Expected instance: `cursor-v14`. `.bhava/instances/cursor-v14/runtime.json` (live, on-disk): `web_pid 11880`, `api_pid 1320`, `mode: production`, `started_at 2026-07-24T13:02:43Z`. This is the instance actually reached and tested (`http://127.0.0.1:3000` / `http://127.0.0.1:8000`).
- `docs/product/uat/v1.4/runtime.json` (tracked copy) is stale (older PIDs/timestamp) — a copy-paste snapshot from an earlier boot, not evidence of a different/wrong instance.
- Existing healthy instance was reused; no new `cowork-v14` instance was started, so nothing needed to be stopped at the end of this session.
- Live `GET /api/v1/stories` confirmed 7 released stories, correct ordering (001–007), `mode: production`.
