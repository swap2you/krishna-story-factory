# Validation Matrix

Apply only relevant rows, but a skipped row requires a reason. `NOT RUN` is never `PASS`.

| Gate | Minimum evidence |
|---|---|
| Requirements | Atomic IDs, objective acceptance, exact implementation/evidence mapping |
| Repository | start/end SHA, clean status, diff/stat, no unrelated or generated churn |
| Python | configured lint/format/type checks; focused and full pytest suites |
| Web | configured lint, typecheck, unit/component tests, production build |
| Browser | real production/standalone build; desktop/tablet/mobile; happy/error paths |
| Console/network | zero unexpected browser console errors; no failed unexpected requests |
| Responsive | 320px, representative tablet/desktop, 200% and 400% zoom where applicable |
| Accessibility | automated scan plus keyboard/focus/landmarks/labels/reduced-motion/manual review |
| Visual | Board B/tokens, hierarchy, spacing, art consistency, no dev toolbar/badges/placeholders |
| Unicode | Devanagari and IAST NFC/NFD/copy/search/extraction/glyph fixtures |
| PDF | opens/renders, selectable text, font facts accurate, sizes/page breaks, no clipping/blank overflow |
| DOCX | opens without repair, real styles, Unicode, images, supported metadata; no false embedding claim |
| Source/content | dossier/locator/claim map, canonical hashes, no invented text, lifecycle/review state |
| Privacy/security | private routes/original paths/secrets denied; public routes do not leak draft/restricted data |
| Dependencies | existing audit/scanners; no new critical/high issue; no unjustified dependency |
| Sonar | run existing Sonar/SonarCloud gate if configured; do not add a new Sonar service solely for this train |
| Release | immutable tag, manifest/hash agreement, exact staging/prod SHA, rollback pointer |
| Public boundary | intended records return expected status; next/private record remains denied |
| Documentation | requirements, traceability, as-built, tests, risks, runbook, release ledger all agree |

## Browser evidence

For UX changes Cursor must save representative screenshots from the production build, not `next dev`. Include viewport, route, commit SHA, browser, timestamp, console result, and expected requirement IDs. Use browser automation plus human-quality visual inspection; screenshots alone are insufficient.

## Completion threshold

- Zero unresolved P0/P1 correctness, source, privacy, security, accessibility, Unicode, export, release-boundary, or data-integrity findings.
- P2/P3 findings may move to a later release only when they do not invalidate a stated acceptance criterion; record them in the backlog.
- Every requirement is `PASS`, `NOT_APPLICABLE` with reason, or `OWNER_DEFERRED` with explicit risk. No `IMPLEMENTED_UNVERIFIED` row may close a release.

