# Repository State & Public-Repository Review — Bhāva Portal V1

## Phase 1 — repository state

- Branch: `feature/bhava-portal-v1` (confirmed via `git branch --show-current`).
- Local `HEAD` == `origin/feature/bhava-portal-v1` == `a4276033951c62687660f9f26375057fe78e01ac`
  (no pull was needed; already fast-forwarded).
- `main` local ref: `3bae97850ef8b934bbec3a48f42f92fbe6de169f` — not touched this session.
- `origin/master`: `3bae97850ef8b934bbec3a48f42f92fbe6de169f` — not touched this session.
- Tags unchanged: `backup/pr8-pre-squash-7a26e80`, `v1.0.0-pilot-stories-001-006`,
  `v1.1.0-stories-001-007-operational` — none created, moved, or deleted this session.
- `data/catalog/locked_queue_state.csv`: stories 001–007 = `done`, story 008 = `pending` — matches
  the required precondition, unchanged.

## Working tree was **not** clean — details

`git status --short` reported 121 modified files. Diffing with `--ignore-all-space` shows
**116 of those 121 are pure CRLF/LF churn** — this repository has no `.gitattributes` and the
review sandbox has no `core.autocrlf` configured, so every file originally committed with CRLF
shows as "modified" on this Linux checkout even though the content is byte-identical once
whitespace is ignored. This is a review-environment artifact, not real drift, and no action was
taken on those 116 files.

The remaining **5 files contain genuine, real uncommitted changes** that predate this UAT
session (this agent did not create them):

- `apps/api/bhava_api/catalog/filesystem.py` — adds `_chapter_sort_key` so packages sort
  numerically (1, 2, …, 10) instead of lexically by `chapter_no` string.
- `apps/api/bhava_api/routes/media.py` — eager-loads `Story.assets` and falls back to
  `asset_media_type(filename)` when an asset (e.g. `manifest.json`) isn't indexed, fixing a
  previously-`None` `Content-Type`.
- `tests/portal/test_api_read_only.py`, `tests/portal/test_catalog_discover_stories.py`,
  `tests/portal/test_package_hash_guard.py` — new/updated assertions covering the two fixes
  above.

These 5 files were **not committed or discarded** by this UAT (review-only mandate). They were
included as-is when this session ran the portal test suite (all 8 tests passed with them in
place — see `pytest_results.md`), so the numeric sort and content-type behavior described in the
report reflect this working-tree state, not only the recorded SHA. Recommend committing these
(they are real bug fixes with matching tests) or explicitly reverting before the branch is
considered final — leaving real code changes uncommitted on a shared branch is itself a release
hygiene risk.

## Phase 16 — public-repository safety scan

No `.env`, credentials, tokens, or Drive credential files are tracked by git:

```
git ls-files | grep -E '^\.env$'          -> (none; only .env.example, all placeholders)
git ls-files credentials                   -> (none tracked)
git ls-files | grep bhava_portal_cursor_bootstrap_v1.zip  -> (none; 21MB zip is untracked/local-only)
```

`.gitignore` already excludes: `.env`, `.venv/`, `__pycache__/`, `output/*` (except `.gitkeep`),
`tracking/*.csv` (except templates), `logs/`, `credentials/`, `node_modules/`, `.next/`,
`data/catalog/*.sqlite*`, `.bhava/`, and the 21 MB bootstrap zip by name.

**Public story media (`output/`) is intentionally excluded** from the repository
(`output/*` + `!output/.gitkeep`) — answers Known Item #10: this is deliberate, not an oversight.

### Large/temporary tracked content that should be reviewed before merging to `main`

- **`portal-bootstrap/`** — 25 tracked files, ~21 MB (`config/`, `cursor/`, `scripts/`, `specs/`,
  `ux-prototype/assets/`). This is one-time scaffolding used to originally bootstrap the portal
  via Cursor; it is not part of the shipped product and inflates clone size. Not deleted during
  this UAT — flagged for a deliberate cleanup decision (Known Item #9).
- `bhava_portal_cursor_bootstrap_v1.zip` (21 MB) sits in the working tree but is correctly
  git-ignored and untracked — no action needed, but worth deleting locally since it duplicates
  `portal-bootstrap/`.

## Secret scan result

See `pytest_results.md` → "Secret scan" section for the single (false-positive/test-fixture) hit.
No real API keys, tokens, or credentials were found in any git-tracked file.
