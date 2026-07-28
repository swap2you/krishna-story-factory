# Bhāva Stories Production Launch — Final CoWork UAT

**Release name:** BHĀVA STORIES PRODUCTION LAUNCH  
**Branch:** `feature/bhava-portal-v1` only (no PR, no merge, no main/tag edits)  
**Product SHA:** `664030a9c933727ffafb2749041dc505ebb0b903`  
**Evidence run:** `docs/product/launch/runs/20260728-113630-122f230/`  
**Runtime:** local portal `http://127.0.0.1:3000` (API `http://127.0.0.1:8000`) — do **not** rely on LocalTunnel for this cycle

## Mission

Perform **one** independent final CoWork UAT of the story-first public launch. Confirm every known CoWork defect is closed, Stories 001–009 remain byte-identical, Story 010 stays unpublished, screenshots are real PNGs, accessibility and security gates hold, and no launch-blocking P0/P1/P2 remains.

Do **not** generate Story 010, mutate the queue, call paid providers, touch Drive, or deploy bhava.me.

## Must verify

1. **Git / SHA** — `git fetch`; local HEAD == origin; product SHA matches `664030a…`; evidence folder present and hashes intact.
2. **Stories 001–009** — recompute 72 package SHA-256 values vs `docs/releases/BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json`; all match.
3. **Story 010** — no `output/010_*`; `/stories/010` is unpublished placeholder with clear language; not in catalog/printables/latest.
4. **Closed CoWork defects**
   - Player Speed/Sleep select contrast ≥ 4.5:1
   - `/preachers` list semantics valid
   - Krishna Book timeline title reflects published range (001–009), not hard-coded 001–007
   - Story 009 Read “Next Story Preview” = Story 010 cart-breaking (not Tṛṇāvarta)
   - Story 009 audio advances in automated evidence (catalog-driven suite includes 009)
5. **Story-first UX** — Home CTAs: Start the Stories / Listen to Latest / Browse Activities / Print Coloring & Worksheets; planned Knowledge/Teachers/Sunday School/Preachers/Vāṇī remain honestly planned.
6. **Printables** — every published story offers poster, simple coloring, detailed coloring, activity PDF.
7. **Screenshots** — `docs/product/launch/screenshots/<viewport>/*.png` exist (138 files); review `SCREENSHOT_INDEX.md`.
8. **Accessibility** — axe critical/serious = 0 on major routes including `/preachers` and `/stories/009`.
9. **Security** — Next `15.5.22`, React `19.1.9`; `npm audit --omit=dev` = 0; see `DEPENDENCY_SECURITY_CLASSIFICATION.md`.
10. **Private boundary** — Studio/Factory not publicly mutable; no source PDFs/keys/`.env`/MyPilotDropbox in public surface.
11. **Raw evidence** — pytest, lint, typecheck, unit, build, playwright (+ reruns), audits, story-hashes, queue-safety, lighthouse-summary present under the evidence run path.

## Verdict options

- `READY FOR RELEASE` only if all gates above pass with no launch-blocking findings.
- Otherwise `PASS WITH NON-BLOCKING NOTES` or `BLOCKED` with a precise defect register.

## Out of scope

- Deploying bhava.me
- Generating Story 010+
- Populating full Knowledge / curriculum libraries
- Creating another micro-release number
