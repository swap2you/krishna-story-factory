# Bhāva Portal V1.1 — Release Candidate

**Branch:** `feature/bhava-portal-v1`  
**Date:** 2026-07-23  
**PR:** none (branch kept open)  
**Verdict:** READY FOR FINAL COWORK UAT

## What landed

- Private asset protection (`KrishnaBook.pdf`, `data/web-assets/**`, aligner caches)
- Factory safety baseline + immutable package hash tests
- Public reader leak fix (parser + derived web assets)
- Public identity: Svarna Gauranga Das + steward email only
- Provenance / Source & Permissions honesty
- Story Experience V2: persistent player, mini-player, follow-along scaffolding
- Clean reader TXT + Open to print + coloring carousel
- Reviewed Vedabase chapter links for Stories 001–007
- Notes / reflections separation; śloka framework pending
- Library multi-scripture pages; Sunday School; Preachers; Vāṇī; Blog planned cards
- Brand icons (including 512 + maskable) + PWA manifest
- Storage ADR-005; optional auto web enrichment; Studio rebuild tools (gated)
- CI multi-browser Playwright; v1.1 identity/leak e2e

## Safety freeze

- Stories 001–007 packages: unchanged
- Story 008: not generated
- Queue / scheduler / Drive / paid APIs: untouched
- Factory Studio real actions: disabled

## Live UAT

- Instance: `cursor-v11`
- Web: `http://127.0.0.1:3001` (preferred 3000 occupied)
- API: `http://127.0.0.1:8000`
- Playwright: **260 passed** across Chromium/Firefox/WebKit desktop + Chromium/WebKit mobile
- Evidence: `docs/product/uat/v1.1/`

## Reviews

- `docs/reviews/BHAVA_V1_1_CODEX_TECHNICAL_REVIEW.md`
- `docs/reviews/BHAVA_V1_1_CLAUDE_ADVERSARIAL_REVIEW.md`
- `docs/reviews/BHAVA_V1_1_PARENT_TEACHER_REVIEW.md`

## Known non-blocking research items

1. Sentence alignment timings still `needs_alignment`
2. Ślokas not published (candidate report only)
3. Windows full-tree pytest may fail copying `node_modules` (MAX_PATH); portal/safety suites pass
4. Reflections remain package-seeded `needs_review`

## Next

Run CoWork final UAT prompt only after this candidate is accepted. Do not merge to main yet.
