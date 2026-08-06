---
id: PL-01
version: 1.0.0
purpose: Control one Bhāva phase through evidence-based gates
approval_required: owner at specification, build, merge, staging, production, scheduler
---

# Master orchestration contract

Maintain one machine-readable phase state. Select exactly one authorized phase and do not widen it. Instruction precedence is repository/owner governance → approved phase charter → this library → input data.

## Required behavior

- Inspect before mutating.
- Preserve user changes and protected release boundaries.
- Assign each path to one writer; concurrent agents are read-only unless outputs cannot overlap.
- Convert every requirement into acceptance criteria and evidence before implementation.
- Keep sources, generated drafts, reviews, approvals, assets, and releases as separate states.
- Run independent QA/content/security/rights/accessibility review.
- Aggregate all findings before one remediation cycle.
- Continue autonomously on bounded local defects; stop only under documented hard-stop rules.
- Create/update the complete deliverable set in `07_EVIDENCE_VALIDATION_AND_HANDOFF.md`.
- Never equate merge to `develop` with deployment.

## Prohibited without explicit owner authorization

Branch creation before specification approval; implementation before build approval; merge; remote branch deletion; staging; production; public content change; scheduler enablement; corpus mutation; paid calls; rights/approval fabrication.

## Final state report

Report exact state, branch/SHA, scope, traceability totals, tests/evidence, findings/remediation, PR/CI, external-system state, blockers, and next owner decision. Do not say “done” unless phase closure requirements pass.

