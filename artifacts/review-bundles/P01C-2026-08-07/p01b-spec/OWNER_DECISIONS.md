# Owner Decisions — P01B-2026-08-07

**Recorded:** 2026-08-07  
**Basis:** Owner instructions authorizing P01B after PR #69 merge  
**Immutable prior evidence:** Phase 0 package + `runs/P01A-2026-08-06/` (do not rewrite)

| ID | Decision | Status |
|---|---|---|
| **D01** | P01A discovery accepted as the baseline. | **DECIDED** |
| **D02** | P01B requirements/UX/architecture/test specification is authorized. | **DECIDED** |
| **D03** | During P01B, locate candidate source editions **read-only** using priority: (1) immutable private `bhava-library` corpus; (2) official BBT, Vedabase, ISKCON, or Ministry source with exact locator; (3) owner-provided upload. Do not download or copy arbitrary third-party editions. Record edition, locator, checksum/private ID, translator, rights, and adequacy. If no adequate authorized edition is found, keep the golden page `SOURCE_BLOCKED`. | **DECIDED** (process). **Outcome this run:** golden page remains `SOURCE_BLOCKED` — see `SOURCE_AVAILABILITY.md`. |
| **D04** | Confirmation-page titles remain deferred until their dossiers are source-adequate. | **DECIDED** |
| **D05** | Preserve the existing devotional public-identity policy. Specify removal of the civil name from the devotional public footer and use the approved Bhāva/Dauji brand identity. **Do not implement during P01B.** | **DECIDED** |
| **D06** | Phase 1 preview is **loopback-only**. Shared preview requires real authentication and separate owner authorization. | **DECIDED** |
| **D07** | Produce three visual-direction boards for owner selection. | **DECIDED** (boards delivered). **Selection of A/B/C still open** → `OWNER_OPEN_DECISIONS.md` OD-01. |
| **D08** | Compare DOCX approaches through a documented technical spike and recommend one; **do not install dependencies**. | **DECIDED** (spike + recommendation delivered). **Install approval still open** → OD-02. |
| **D09** | Carry the Story 20/22 documentation/default mismatch as a bounded maintenance item. Do not change Story Factory behavior during P01B. | **DECIDED** |
| **D10** | Do not waive the missing Etiquette/Deity Worship source requirement. Keep that vertical blocked until exact files or authorized equivalents are restored. | **DECIDED** |
| **D11** | Execution packet and P01A evidence are accepted in Git through PR #69. | **DECIDED** (merged `27c3f35`) |
| **D12** | Node 24 is mandatory before any P01C web build. | **DECIDED** |

## Merge evidence (D11)

| Item | Value |
|---|---|
| PR | https://github.com/swap2you/krishna-story-factory/pull/69 |
| Verified head | `e1a7b1862ddea2796fc48ea17bea02d99a7ea0c6` |
| Merge commit | `27c3f35a72a0ffbea864361bab597cc627eaeb0f` |
| Base | `develop` |
| Local post-merge | `develop` @ `27c3f35`, clean, FF-only; feature head is ancestor of `develop` |

## Effect on gates

- **G2 Specification:** in progress → this run completes the package for owner review.  
- **G3 Build:** **not** authorized. P01C remains blocked until specification acceptance **and** an authorized golden-page edition/dossier (D03 outcome).  
- Source discovery ≠ content approval.
