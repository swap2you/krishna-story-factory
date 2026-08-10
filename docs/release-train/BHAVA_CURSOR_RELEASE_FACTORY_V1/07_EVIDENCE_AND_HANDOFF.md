# Evidence and Handoff Contract

## Per-release local folder

`artifacts/release-train/<release-id>/<run-id>/`

Required contents:

- `FINAL_HANDOFF.md`
- `RELEASE_STATE.yaml`
- `REQUIREMENTS.md`
- `REQUIREMENTS_TRACEABILITY.csv`
- `BASELINE.md`
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
- `BLOCKER_REPORT.md` only if blocked
- `CHECKSUMS.sha256`
- sanitized logs and representative screenshots

Keep large generated media, private source PDFs, databases, credentials, tokens, and duplicate build outputs out of the ZIP and Git. Manifests point to them by canonical path/URL, size, hash, and validation result.

## Review ZIP

Create:

`MyPilotDropbox\BHAVA\release-handoffs\<release-id>_<run-id>_REVIEW.zip`

The ZIP is local-only unless repository policy explicitly permits small evidence files. Validate it by listing entries, rejecting traversal/symlinks, verifying checksums, and extracting it to a fresh temporary directory.

## Cursor final response

Return only:

1. release ID and outcome (`CLOSED`, `BLOCKED`, or `ROLLED_BACK`);
2. start/develop/main/deployed SHAs and tags;
3. implemented outcome in five bullets maximum;
4. requirement totals;
5. local test totals and failures/skips;
6. independent review totals and fixes;
7. CI, staging, promotion PR, production URLs/results;
8. browser/UX/accessibility/export/source/security verdicts;
9. public/private boundary result;
10. evidence ZIP path and SHA-256;
11. remaining blocker or next release ID;
12. exact files to send ChatGPT and CoWork.

Do not paste long logs into the response. Put them in the evidence ZIP.

