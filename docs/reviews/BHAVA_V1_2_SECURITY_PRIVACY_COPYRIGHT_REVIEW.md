# Bhāva V1.2 — Security, Privacy, and Copyright Review

**Branch:** `feature/bhava-portal-v1`  
**Date:** 2026-07-23

## Checks

| Check | Result |
| --- | --- |
| Private keys/certs tracked | No |
| `.env` tracked | No |
| `KrishnaBook.pdf` tracked/served | No (gitignored) |
| MyPilotDropbox tracked | No |
| Civil identity / phone / LinkedIn / GitHub on public pages | Guarded by tests; steward-only public identity |
| Child-data collection | No accounts; notes localStorage-only; contact uses mailto |
| Analytics by default | None added |
| Public Studio production actions | Disabled; loopback + CSRF |
| Path traversal on assets | Allowlisted filenames |
| Blanket BBT ownership / undocumented “used with permission” | Avoided; excerpt-needs-review language |
| Fabricated ślokas/quotations | Not published |

## Residual

- 8 Phase-5 canto cover assets missing from approved recreated package extract (documented blockers).
- Sentence alignment still `needs_alignment`.

## Verdict

Pass for release-candidate review with documented brand blockers.
