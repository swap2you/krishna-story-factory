# Implementation Plan — P01C (authorized only after G3)

**Do not execute in P01B.** Branch only after OD-15 + OD-14 + explicit build authorization.

## Proposed branch

- Name: `feature/kf-p01-visual-learning-pilot`  
- Base: `develop` @ re-verified SHA (currently `27c3f35…`)  
- Node: **24** mandatory (D12)

## Work sequence

1. Schema + TS/Python adapters + validation fixtures (no real scripture yet if still blocked — stop if D03 incomplete).  
2. Studio pagination (348) + private preview shell with Blocked state.  
3. Auth hardening (loopback + session; deprecate forgeable header).  
4. Stanza/lens/focus components + URL state.  
5. Unicode font load after OD-13.  
6. PDF spike (reportlab) → DOCX after OD-02 install approval.  
7. Golden page with approved dossier text only.  
8. Independent validation + one remediation pack.  
9. Freeze Page Template V1 → four confirmation pages (D04 titles).  
10. PR/evidence — still no staging/production/scheduler.

## Commit plan (logical)

1. `feat(knowledge): canonical package schema + adapters`  
2. `feat(studio): roadmap pagination + preview shell`  
3. `feat(knowledge): private-preview auth boundary`  
4. `feat(knowledge): stanza/lens/focus UI`  
5. `feat(knowledge): export PDF/DOCX + manifests`  
6. `test(knowledge): a11y/unicode/privacy/export matrix`  
7. `docs: as-built + evidence`

## Path ownership / allowlist

See `PATH_OWNERSHIP_ALLOWLIST.md`.

## Rollback

See `MIGRATION_AND_ROLLBACK.md`.

## Cost / provider

Paid off. No dependency install until OD-02 (DOCX) / OD-13 (fonts) approved.
