# Bhāva Portal V1 — CoWork UAT: Methodology & Environment Limitations

This UAT was executed by a Cowork agent from a **sandboxed Linux review environment** with
read/write access to the repository folder (mounted from the Windows workstation) and an
isolated Linux shell. It did **not** have access to PowerShell/`pwsh`, and each shell command
is capped at 45 seconds with no processes surviving between commands. These constraints shaped
what could be dynamically executed vs. statically reviewed. This note exists so every finding
in `docs/reviews/BHAVA_V1_COWORK_UAT.md` can be traced back to how it was actually verified.

## What was executed live (real, reproducible evidence)

- **Git state** — `git status`, `git rev-parse`, `git log`, `git diff --ignore-all-space`,
  `git ls-files` were run directly against the real repository.
- **Backend API** — The FastAPI service (`apps/api`) was started for real with `uvicorn` inside
  a Python 3.10 virtual environment built in this session, using `BHAVA_REPOSITORY_ROOT` pointed
  at the real `output/` folder so genuine story packages were served. `curl` was used to exercise
  `/api/v1/health`, `/api/v1/stories`, `/api/v1/local/status`, `/api/v1/local/generate-next`, and
  asset routes, including negative tests (bad `Host` header, missing CSRF token). See
  `api_health_and_safety_evidence.md`.
- **Python test suites** — `pytest` was run directly against `tests/portal` (all 8 tests) and
  against the legacy factory suite in `tests/` (173 of 218 collected tests completed; see
  `pytest_results.md` for the itemized breakdown and the tests that could not finish inside the
  45-second execution windows).
- **Repository/secret hygiene** — `git ls-files`, `.gitignore` review, and a pattern-based secret
  scan (`git grep`) were run against tracked files only.

## What could **not** be executed live, and why

The Next.js frontend (`apps/web`) **could not be started** in this sandbox:

- `package.json` pins `@next/swc-win32-x64-msvc` and `@rollup/rollup-win32-x64-msvc` directly as
  regular `dependencies` (Windows-only native binaries). Running `npm install` exactly as
  instructed, in the real repository, fails immediately with `EBADPLATFORM` on this Linux
  sandbox — this is itself recorded as a defect (see report).
- A workaround copy with the Windows-only packages stripped was attempted so a Linux-compatible
  `node_modules` could be built for testing purposes only (never committed, never written back
  into the real repository). Even the trimmed install could not complete: this sandbox's npm
  dependency-resolution step for the Next 15 / React 19 / ESLint 9 / Playwright toolchain did not
  finish within the available execution windows.
- No Playwright browsers (Chromium/Firefox/WebKit) could therefore be launched against a live
  `next dev`/`next start` server, so **no live screenshots, no live axe-core DOM scan, no live
  console/network capture, and no live responsive/cross-browser passes were possible** in this
  session.
- Separately and independently: `apps/web/playwright.config.ts` only defines a `chromium`
  project, and `apps/web/e2e/` does not exist in the repository at all — so even on a machine
  where `npm install` succeeds, there are currently **zero** Playwright end-to-end specs to run,
  and no Firefox/WebKit projects configured. This is a real repository finding, independent of
  the sandbox limitation, and is recorded as a defect.

## How the frontend was reviewed instead

Every route, component, and piece of client-side behavior referenced in the persona, functional,
UX, and accessibility findings below was verified by **reading the actual shipped source** under
`apps/web/app/**`, `apps/web/components/**`, and `apps/web/lib/**` — the exact code that ships to
the browser — and cross-checking it against the live backend responses. Findings are cited with
file paths (and line numbers where useful) so they can be independently re-checked. Claims that
would require rendered pixels (exact visual layout at each breakpoint, real screen-reader output,
true cross-browser rendering differences) are explicitly flagged as **not verified** rather than
asserted.

## Recommendation

To close this gap, re-run Phases 3–15 and 18 of this UAT **natively on the Windows workstation**
using `scripts\test_bhava.ps1` and `scripts\start_bhava_local.ps1` (or from a Linux/macOS CI
runner once the `EBADPLATFORM` issue is fixed), with real Playwright specs added under
`apps/web/e2e/` covering Chromium, Firefox, and WebKit, plus an `@axe-core/playwright` pass per
route. That run can supply the visual evidence (screenshots, axe report, cross-browser diffs)
this session could not produce.
