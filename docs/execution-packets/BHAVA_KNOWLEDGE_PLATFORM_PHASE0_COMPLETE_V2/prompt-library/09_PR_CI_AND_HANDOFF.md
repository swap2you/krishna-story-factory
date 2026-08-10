---
id: PL-09
version: 1.0.0
phase: P01 delivery
approval_required: push/PR according to repository and owner policy; merge always separate
---

# PR, CI, and owner handoff

Reverify minimal diff, no secrets/private paths/binaries/unrelated churn, manifests, docs, tests, and clean status. Create logical final commits and record hashes. Push/open a PR to `develop` only when authorized and supported by repository workflow.

PR body must include scope/exclusions, requirements summary, architecture/ADRs, source/rights/privacy, UX/accessibility/export evidence, tests/commands/results, screenshots/renders, migration/rollback, protected Story Factory/release invariants, known risks, and explicit statement that staging/production/scheduler/publication remain unchanged.

Reconcile CI failures to root cause; do not weaken gates. Produce `PR_HANDOFF.md`, `OWNER_REVIEW.md`, `AS_BUILT.md`, `EVIDENCE_INDEX.md`, checksums, traceability totals, exact branch/base/head SHAs, and all requested deliverable links/paths.

Stop at merge approval.

