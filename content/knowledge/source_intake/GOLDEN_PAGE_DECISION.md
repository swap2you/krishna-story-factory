# Golden page decision (M2)

**Program:** Bhāva Unified Platform Build V2  
**Date:** 2026-08-10  
**Decision:** **NO new scripture golden package is published.**

## Candidates evaluated

| Candidate | Result | Notes |
|---|---|---|
| TOP-0147 Sri Nrsimha Pranama and Prayers | **SOURCE_BLOCKED** | Roadmap metadata only; no authorized edition, locator, Devanāgarī, IAST, English, or rights clearance |
| TOP-0148 Nrsimha Arati (alternate) | **SOURCE_BLOCKED** | Same gap class; not dossier-ready |
| Owner PDF intake (12 files) | **SOURCE_INCOMPLETE** | All `dossier_ready=false`; stubs under `dossiers/`; no PDF text copied into git |

## Consolidated source blocker (exact missing fields)

Until the following are evidenced for a chosen scripture candidate, no golden/confirmation scripture page may become public:

1. **exact edition/locator**
2. **Devanāgarī** (verified Unicode, NFC)
3. **IAST** (verified)
4. **English** (authorized translation/adaptation attribution)
5. **rights clearance**

Additional operational gaps for image-only intake PDFs (sequences 10–11): `ocr_state=OCR_PENDING` under a supported OCR workflow — OCR alone does not clear rights or edition gates.

## What remains public on Knowledge

Existing **Bhāva-original** editorial guides only (not scripture packages):

- `what-is-bhava`
- `source-and-permissions`
- `printing-and-classroom-use`

Plus published FAQ question records already in the public Knowledge catalog. These are **not** a substitute golden scripture page.

## Private artifacts retained

- P01C structural fixture `KF-P01C-FIXTURE-001` (studio private; `SOURCE_BLOCKED`)
- Intake inventory + dossier stubs (private; `public_allowed=false`)
- Batch-25 manifest and draft factory queue (private; zero publication authority)

## Authority

This decision does not authorize fabricate-to-publish. Revisit only when a dossier reaches `DOSSIER_READY` with real evidence for every field above.
