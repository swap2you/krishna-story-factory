# 05 — Security, Runtime & Safety

## Security (Section H) — PASS

- **`npm audit --omit=dev` re-run live this session: 0 vulnerabilities (0 info / 0 low / 0 moderate / 0 high / 0 critical)** — matches the evidence `npm-audit-prod-summary.json`. Production audit ZERO requirement met.
- Versions (lockfile): **next 15.5.22** (patched — out of the advisory range that flagged 15.3.5 at V1.7.3), **react 19.1.9**, **react-dom 19.1.9**. The previously-flagged nested `postcss`/`sharp` prod entries are no longer flagged after the Next upgrade — no vulnerable nested runtime package remains.
- Full audit (dev included): 9 high, ALL in the eslint/brace-expansion/minimatch lint-toolchain cluster (devDependencies only; classified in the V1.7.3 evidence and unchanged in character). Zero critical.
- Boundary: `/.env` 404, path traversal 404, factory mutation API 404, `/studio` read-only, no source PDFs served, no MyPilotDropbox or local paths exposed on any page sampled; no `.pem/.key/.pfx/.env` files tracked in git; `docs/SETUP_AND_CREDENTIALS.md` contains policy text only, no actual secrets (pattern scan clean).

## Runtime & cleanup (Section I) — PASS

- **Live port probe (from the host browser): exactly one web instance (127.0.0.1:3000 ALIVE) and one API instance (127.0.0.1:8000 ALIVE); all historical ports (3001–3005, 8001–8003) dead.**
- `runtime-cleanup-note.json` records the 12 old instances (cursor, cursor-launch, cursor-uat, v11–v173) as stopped with `bhava-final` active, strict ports, no collision — consistent with the live probe.
- No tunnel active: `public-url.txt` absent/empty → zero UAT tunnels (≤1 requirement met). No new instance or tunnel was started by this review.
- Runtime files untracked: `git ls-files .bhava/ MyPilotDropbox/` returns nothing; `.gitignore` covers `.bhava/` and `/MyPilotDropbox/`.
- Old instances' stale `runtime.json` files remain on disk (untracked, processes dead) — cosmetic only; P4 tidy-up candidate.
- No arbitrary user files were deleted by this review (review-only).

## Safety (Section J) — PASS

- Queue live: `009 … done` / `010,baby-krishna-breaks-the-cart,pending` — unchanged.
- No `output/010_*` (direct listing).
- Scheduler not triggered; zero provider calls; Drive untouched this pass (no Drive access from this environment); MyPilotDropbox unmodified.
- No sensitive file committed: the only files this review adds are the report and this evidence folder.

## Git/evidence (Section A) — PASS

- Live-resolved: HEAD == origin/feature/bhava-portal-v1 == `f8caa61...` after a real `git fetch` this session.
- Tested product SHA `77640c3...` (from `metadata.json`); `git diff --name-only 77640c3..HEAD` → **docs/ only** (single evidence commit `f8caa61 "Record final copyright launch evidence and screenshot index."`).
- No PR/merge; `main` remains `3bae978...` (untouched); tags unchanged (same 3 historical tags).
- Raw final matrix present at `docs/product/launch/runs/final-copyright-20260728-153637-77640c3/`: playwright-full.txt (607 passed / 3 skipped per metadata note, exit reflected in summaries), pytest-full.txt, lint/typecheck/unit/build logs, npm evidence, story-version-migration and old-and-new hashes, sitemap/queue/runtime verification JSONs — all git-tracked and cross-consistent with this review's independent findings.
- Second run folder `20260728-113630-122f230` is an earlier same-day iteration retained for provenance; the final folder is authoritative.
