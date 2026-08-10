# Evidence and Handoff

## Milestone evidence folder

Create one local folder per milestone:

`artifacts/unified-platform-v2/<milestone>/<timestamp>/`

Required files:

- `FINAL_HANDOFF.md`
- `PROGRAM_STATE.yaml` (copy/update `specs/02_PROGRAM_LEDGER.yaml`)
- `BASELINE.md`
- `REQUIREMENTS_TRACEABILITY.csv`
- `IMPLEMENTATION_SUMMARY.md`
- `CHANGED_FILES.csv`
- `TEST_RESULTS.md`
- `BROWSER_UX_ACCESSIBILITY.md`
- `SOURCE_CONTENT_EXPORT_REVIEW.md`
- `SECURITY_PRIVACY_REVIEW.md`
- `CI_STAGING_PRODUCTION.md`
- `RELEASE_MANIFEST.json`
- `EVIDENCE_MANIFEST.csv`
- `BACKLOG.md`
- `BLOCKER_REPORT.md` only when needed
- `CHECKSUMS.sha256`
- sanitized logs and representative standalone-build screenshots

## ZIP rules

- Create a compact review ZIP per milestone and one final program ZIP.
- Verify entries have no traversal/symlink hazards, verify checksums, and extract to a clean directory.
- Exclude original PDFs, databases, secrets, provider data, private media, caches, and duplicate build output.
- Evidence must separately name: implementation SHA, `develop` tip, ledger-close SHA, staged SHA, main merge SHA, deployed SHA, tag, and content digest. Do not call different SHAs the same thing.
- Where Drive equality is claimed, compare a common digest or explicitly state the limitation; matching file name/size alone is not byte equality.

## Current evidence to keep

- R00 Story 001–025 evidence ZIP: closed release, production verification, `025=200`, `026=404`.
- R01 evidence ZIP: genuine source blocker for TOP-0147. Do not erase or misrepresent it; supersede it only with an adequate dossier decision.

