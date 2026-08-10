# Evidence, Validation, and Handoff Contract

## Definition of done

“Implemented,” “looks good,” an agent summary, or green unit tests alone are not completion. Every acceptance criterion must map to reproducible evidence.

## Required phase deliverables

- `PHASE_CHARTER.md`
- `BASELINE_REPORT.md`
- `SOURCE_AND_REUSE_INVENTORY.md`
- `REQUIREMENTS.md`
- `UX_SPEC.md`
- `ARCHITECTURE.md` and ADRs
- `IMPLEMENTATION_PLAN.md`
- `TEST_AND_SECURITY_PLAN.md`
- `SOURCE_LEDGER.csv`
- `ASSET_MANIFEST.csv`
- `REQUIREMENTS_TRACEABILITY.csv`
- `IMPLEMENTATION_REPORT.md`
- `TEST_RESULTS.md`
- `ACCESSIBILITY_AND_EXPORT_REPORT.md`
- `SECURITY_PRIVACY_RIGHTS_REPORT.md`
- `EVIDENCE_INDEX.md`
- `CONSOLIDATED_REMEDIATION.md` when needed
- `PR_HANDOFF.md`
- `OWNER_REVIEW.md`
- `AS_BUILT.md`
- `POST_MERGE_REPORT.md` after authorized merge
- `MAINTENANCE_RECORD.md`
- `PHASE_CLOSURE.md`
- machine-readable phase state, approvals, evidence records, hashes

## Evidence classes

| Class | Examples |
|---|---|
| Repository | status, branch, SHA, diff, file inventory |
| Automated | exact commands, exit codes, test/lint/type/build/security results |
| Runtime | route/API responses, browser console/network, private/public boundary |
| Visual | desktop/mobile/zoom/reduced-motion/print screenshots and render comparisons |
| Accessibility | automated report plus keyboard/screen-reader/manual findings |
| Content | dossier, claim map, text/translation comparison, reviewer decisions |
| Rights/provenance | source/asset ledger, licenses/conditions, checksums |
| Export | PDF/DOCX render, Unicode extraction, structure/accessibility checks, hashes |
| Delivery | CI URL/result, PR diff, owner decisions, merge/post-merge SHA |

## Traceability row

Each requirement row records:

`requirement_id, description, source, implementation_paths, validation_method, evidence_paths, status, finding_ids, reviewer, decision_date, deferral`

Status is one of `NOT_STARTED`, `IMPLEMENTED_UNVERIFIED`, `PASS`, `FAIL`, `BLOCKED`, `OWNER_DEFERRED`. Only `PASS` or an explicit `OWNER_DEFERRED` with accepted risk can close a row.

## Independent validation

- Implementer runs local checks but does not serve as independent QA.
- QA/accessibility, content/source, security/privacy/rights, and UX reviewers submit findings before remediation.
- The orchestrator deduplicates/root-causes findings and creates one remediation release (`Pxx.R1`).
- All changed/affected tests and the full required regression suite rerun after remediation.

## Cursor final response requirements

Cursor must return:

1. outcome and exact phase state;
2. implemented scope and explicit exclusions;
3. files created/changed and why;
4. branch, starting/current SHA, commits, PR/CI status;
5. requirements pass/fail/deferred totals;
6. commands/tests and results;
7. browser/visual/accessibility/export/content/security evidence;
8. consolidated fixes applied;
9. known risks/blockers and owner decisions needed;
10. deployment/scheduler/publication state (normally unchanged);
11. links/paths to every required deliverable;
12. repository/branch hygiene result.

Cursor must create the deliverable files, not merely describe them in chat.

