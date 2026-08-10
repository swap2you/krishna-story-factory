# What Is Already Implemented (Excluding the Story Content Itself)

## Production and delivery foundation

- Public release boundary is now 001–025. Story 026+ is denied on page and reader routes.
- Immutable content bundle and staging/production deployment path are proven, with rollback pointers and smoke tests.
- `main` carries production release `0fb429c6…`; the exact content bundle digest is `2dda0485a085f93d222a0ebd1d27b620df408990e7673a11b9603de68ff230a9`.
- Direct-to-`develop` release-train policy, evidence templates, CI/staging checks, and final promotion workflow exist.

## Knowledge foundation already in the codebase

- Canonical Knowledge record-package structure: record, ordered content blocks, source dossier, claims, rights, assets, reviews, and manifest.
- Four age-depth lenses: Little Learner, Explorer, Teen, and Study, sharing one canonical text rather than four contradictory copies.
- Private Studio/Knowledge preview, package queue/pagination, lifecycle states, and private API boundaries.
- Controlled focus mode, source/review surfaces, deterministic Noto font setup, PDF/DOCX export paths, and Unicode fixtures.
- Board B editorial-gouache visual direction and Bhāva tokens are the locked design direction.

## What is deliberately not done yet

- No real, approved Knowledge record has become a public page.
- TOP-0147 Nṛsiṁha was correctly left blocked because its verified Devanāgarī, IAST, English source, locator, and rights dossier were not established.
- No genuine Learning pathways, teacher packs, Prabhupāda Vāṇī collection, publication packages, podcast pilot, scheduler, or 3D product has been completed.

## Important correction

The site did not visibly change from P01C because P01C was an internal/private foundation. The next program must create approved public-facing product surfaces and real approved content records; otherwise the work is technically sound but visually invisible.

## M1 source intake (2026-08-10)

Stale “12 PDFs missing” notes from Phase-0 evidence are superseded for current work: the twelve owner PDFs are inventoried as private metadata (`STAGED_SOURCE_CANDIDATE` / `OCR_PENDING`) under `content/knowledge/source_intake/` and `docs/unified-platform-v2/source_inventory/`. Originals are not in git; no public PDF bodies; `dossier_ready` remains false until real review.

## M2 Knowledge system + factory (2026-08-10)

- Page Template V1 frozen (`docs/unified-platform-v2/PAGE_TEMPLATE_V1.md`) with component contract under `apps/web/components/knowledge/`.
- Public guides use adapted Template V1 shell (no fabricated scripture).
- Twelve private `SOURCE_INCOMPLETE` dossier stubs; golden scripture page **not** published (`GOLDEN_PAGE_DECISION.md`).
- Private `batch_25_manifest_v1.json` and 50-item dry-run draft factory with Studio read-only progress; zero publication authority.

