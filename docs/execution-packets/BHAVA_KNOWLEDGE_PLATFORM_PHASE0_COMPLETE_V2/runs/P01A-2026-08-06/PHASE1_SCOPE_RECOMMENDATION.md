# Phase 1 Scope Recommendation — P01A

## Exact proposed Phase 1B scope (specification only)

Produce owner-reviewable:

1. `REQUIREMENTS.md` mapped from P1-F/U/E IDs + discovery evidence  
2. `UX_SPEC.md` + three visual direction boards + golden wireframe (no production assets)  
3. `ARCHITECTURE.md` + ADRs: record package schema, private-preview auth, export approach selection criteria  
4. `TEST_AND_SECURITY_PLAN.md` (a11y, Unicode, privacy, export, regression)  
5. `IMPLEMENTATION_PLAN.md` with allowlisted paths and path owners  
6. Source ledger + draft dossiers for owner-chosen candidates (still no fabricated text)  
7. Requirements traceability CSV seeded (`NOT_STARTED`)

**Still forbidden in 1B:** feature branch (until spec approval + build auth), app code, dependency installs, paid calls, content publication.

## Exact proposed Phase 1C scope (after build authorization)

1. Create `feature/kf-p01-visual-learning-pilot` from `develop` @ approved SHA only after owner build approval  
2. Implement **one golden page** (private preview) with four lenses + focus mode + source panel  
3. PDF + DOCX export from same record version (chosen spike)  
4. Studio completeness for 348 roadmap visibility (pagination) + private-preview listing  
5. Hardened private-preview controls (noindex, auth stronger than forgeable header alone)  
6. Independent validation + one consolidated remediation  
7. Four confirmation pages only after Page Template V1 freeze  

**Excluded from Phase 1 (locked):** staging/production promotion, scheduler enablement, audio/podcast/3D, framework migration, public publication of pilot pages, Story Factory changes, bulk 348 promotion, Etiquette vertical until PDFs restored.

## Recommended golden-page candidate(s)

| Rank | Candidate | Why | Blocker |
|---|---|---|---|
| 1 | `TOP-0147` Sri Nrsimha Pranama and Prayers | Matches multi-stanza golden requirement | **SOURCE_BLOCKED** — no verified text/rights package |
| 2 | `TOP-0148` Nrsimha Arati | Alternate Nṛsiṁha multi-part form | same |

**Owner must supply or designate** the authorized edition before any title is frozen.

## Success definition for Phase 1 (unchanged from packet)

Private preview proves content→page→export with five dossiers and zero unresolved P0/P1 defects; no staging/production/scheduler change.
