# Bhāva V1.5 — Implementation Plan

**Branch:** `feature/bhava-portal-v1`  
**Contract:** `MyPilotDropbox/bhava-v1.5-release/BHAVA_V1_5_CURSOR_MASTER_PROMPT.md`  
**Starting SHA:** `b1bc133c927067bd33d3e1cc191c5345926a7169`

## Priority order (locked)

1. Production reliability and Story 008 recovery  
2. Audio (DEF-06)  
3. Homepage / platform positioning  
4. Knowledge Library  
5. Library  
6. Learning destinations  
7. Printables  
8. About / Contact / FAQ  
9. Prabhupāda Vāṇī  
10. Secondary polish  

## Phase map

| Phase | Commit message (target) | Status |
|------|-------------------------|--------|
| 0 | `test: establish Bhava v1.5 safety and defect baseline` | in progress |
| 1 | `fix(factory): make scheduled story production atomic resumable and idempotent` | pending |
| 2 | Story 008 recovery release docs + package | pending (after Phase 1 + explicit recovery flag) |
| 3 | `fix(catalog): publish only atomic story packages and refresh all portal indexes` | pending |
| 4 | `fix(audio): guarantee story playback with observable native and blob modes` | pending |
| 5 | `test: make Bhava release evidence immutable and SHA attributable` | pending |
| 6 | `feat(design): establish Bhava youth learning design system` | pending |
| 7 | `feat(navigation): improve Bhava brand lockup and platform wayfinding` | pending |
| 8 | `feat(home): reposition Bhava as a complete devotional learning platform` | pending |
| 9 | `feat(library): organize Bhava scriptures stories and devotee-life collections` | pending |
| 10 | `feat(knowledge): redesign public Knowledge pathways for readable youth learning` | pending |
| 11 | `feat(learning): clarify youth Sunday School teacher and preacher pathways` | pending |
| 12 | `feat(trust): strengthen Bhava mission contact FAQ and source transparency` | pending |
| 13–14 | Route visual QA + a11y/performance | pending |
| 15 | `test: complete Bhava v1.5 full release validation` | pending |
| 16–18 | Native UAT, reviews, safety cleanup | pending |

## Hard gates

- Stories 001–007 SHA-256 frozen in `BHAVA_V1_5_SAFETY_BASELINE.json`
- No Story 008 public exposure until exact-eight + atomic publish
- No unofficial Samarkan download; Tillana / Yatra One fallback
- No PR / merge / main / master / tag mutation
- READY only when scheduler, 008, audio, redesign, responsive, a11y, and SHA-bound matrix all pass

## Brand / Knowledge inputs

- Brand: `MyPilotDropbox/bhava-brand-assets-v1`
- Knowledge: `MyPilotDropbox/bhava-knowledge-library-v1.0`

## Product copy (locked)

- Name: Bhāva  
- Tagline: Timeless devotion for growing hearts and minds.  
- Supporting: Stories, scripture, practice, and learning paths for children, youth, families, and teachers.
