# Baseline Report — P01A

**Run:** `P01A-2026-08-06`  
**Repository:** `C:/Development/Workspace/DevotionalRepo/krishna-story-factory`  
**Observed:** 2026-08-06

## Git baseline

| Item | Value | Label |
|---|---|---|
| Current branch | `develop` | **VERIFIED** |
| HEAD SHA | `d6159e9af6b7033d1876141eae31944ec93fffc0` | **VERIFIED** |
| Upstream | `origin/develop` @ same SHA; ahead/behind `0 0` | **VERIFIED** |
| `origin/main` | `257692f2d927d2215cf7a07efa22411f4cf46db9` | **VERIFIED** |
| Local `main` | `72eb171…` (**behind** `origin/main` by 21) | **VERIFIED** |
| Open PRs | none (`gh pr list` → `[]`) | **VERIFIED** |
| Remote branches | `main`, `develop` only | **VERIFIED** |
| Worktrees | main checkout + `krishna-story-factory-deployment` @ `fix/pr15-review-gate` | **VERIFIED** |
| Working tree (tracked) | clean | **VERIFIED** |
| Untracked (this intake) | `docs/execution-packets/` (package + this run) | **VERIFIED** |

Phase 0 baseline SHAs for `develop`/`origin/main` match current remotes. Local `main` lag is operator hygiene only; Phase 1 work must base on `develop`.

## Runtimes

| Runtime | Pin / observed | Label |
|---|---|---|
| Node pin (`.nvmrc` / `.node-version`) | `24` | **VERIFIED** |
| Node observed | `v22.23.1` | **VERIFIED** mismatch vs pin |
| npm | `10.9.8` | **VERIFIED** |
| Python pin (`.python-version`) | `3.14` | **VERIFIED** |
| Python observed | `3.14.6` | **VERIFIED** |
| Lockfiles | root `package-lock.json`, `requirements.txt` | **VERIFIED** |
| `pnpm`/`yarn`/`uv`/`poetry` locks | absent | **VERIFIED** |

## Stack layout (summary)

| Area | Path | Role |
|---|---|---|
| Web | `apps/web` | Next.js App Router public site + Studio |
| API | `apps/api` | FastAPI catalog/knowledge/local factory |
| Factory | `krishna_story_factory/`, `run_daily_story.py` | Story pipeline |
| UI kit | `packages/ui` | design tokens/primitives |
| Contracts | `packages/contracts/schemas` | JSON schemas |
| Content | `content/knowledge/` | Knowledge articles/questions/pathways/roadmap |
| Deploy | `deploy/ionos/`, `deploy/content/RELEASE_CONTENT.json` | Caddy/compose + content pin |
| CI | `.github/workflows/ci.yml` (+ deploy/rollback/ops) | lint/type/test/e2e/security |

## Release / public story boundary

| Control | Value | Label |
|---|---|---|
| `RELEASE_CONTENT.json` | tag `bhava-content-001-022-v1`, `public_story_max: 22` | **VERIFIED** |
| Web default `PUBLIC_STORY_MAX` | 20 (`apps/web/lib/public-boundary.ts`) unless env override | **VERIFIED** |
| API default | 20 unless `BHAVA_PUBLIC_STORY_MAX` | **VERIFIED** |
| AGENTS.md note | 001–020 public / next 021 | **REPORTED** stale vs release pin 22 |
| Local private package present | `output/023_…` (gitignored) | **VERIFIED** |

## Knowledge foundation (spot-check)

| Item | Value | Label |
|---|---|---|
| Roadmap path | `content/knowledge/roadmap/records.json` | **VERIFIED** |
| Count | **348** | **VERIFIED** |
| Lifecycle | all `source_research` | **VERIFIED** |
| Package status | all `research_backlog` | **VERIFIED** |
| Published articles/questions | 3 + 3 | **VERIFIED** |
| Pathways | 4 published / 12 proposed | **VERIFIED** |

## Sibling repositories (local disk)

| Repo | Present | HEAD (observed) | Label |
|---|---|---|---|
| `bhava-library` | yes | `fix/curation-quality-v1.1` @ `5e5c648…` | **VERIFIED** |
| `bhava-publishing-studio` | yes | not fully re-audited this run | **PARTIAL** |

## Existing user / local changes

| Change | Overlap risk with Phase 1 |
|---|---|
| Untracked `docs/execution-packets/` | None for app code; keep uncommitted until owner decides doc commit policy |
| Local `MyPilotDropbox/`, `.env`, `output/`, `credentials/` | Must remain uncommitted; do not stash/clean |
| Deployment worktree | Non-overlapping if Phase 1 stays on `develop` feature branch later |

No stash/reset/checkout/clean performed.

## Commands / evidence

```text
git rev-parse --show-toplevel
git status --porcelain=v1
git branch -vv
git remote -v
git log -8 --oneline --decorate
git rev-list --left-right --count origin/develop...HEAD
git worktree list
gh pr list --state open
python -c "...roadmap Counter..."
```

## Gate

**G1 Baseline: PASS for discovery**  
Build/spec authorization remains **false**. Node 22 vs pin 24 recorded as operator risk before any future build.

## Baseline unsafe?

No `BLOCKER_REPORT.md` for discovery. Soft risks → `RISK_REGISTER.md`.
