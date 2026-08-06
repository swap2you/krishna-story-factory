# Bhāva Cursor Prompt Library

Run prompts in numeric order. Each prompt inherits the charter, locks, phase manifest, and approved phase artifacts. Later prompts do not grant authority missing from earlier approvals.

| Prompt | Purpose |
|---|---|
| `00_CURSOR_STARTER.md` | Starts Phase 1A safely |
| `01_MASTER_ORCHESTRATOR.md` | Persistent orchestration/authority contract |
| `02_SAFE_INTAKE_AND_BASELINE.md` | Package and repo validation |
| `03_DISCOVERY_AND_REUSE_AUDIT.md` | Current-state evidence |
| `04_REQUIREMENTS_UX_AND_CONTENT_SPEC.md` | Full owner-reviewable specification |
| `05_ARCHITECTURE_TEST_AND_IMPLEMENTATION_PLAN.md` | Design before code |
| `06_IMPLEMENTATION_ORCHESTRATOR.md` | Approved Phase 1 implementation |
| `07_INDEPENDENT_VALIDATION.md` | QA/content/security/export evidence |
| `08_CONSOLIDATED_REMEDIATION.md` | One complete fix pack |
| `09_PR_CI_AND_HANDOFF.md` | PR/evidence/as-built package |
| `10_OWNER_MERGE_RELEASE_GATES.md` | Explicit protected actions |
| `11_MAINTENANCE_AND_LOCK.md` | Safe closure and hygiene |
| `12_CONTENT_BATCH_FACTORY.md` | Future 25/50-item private batches |
| `13_SCHEDULER_DESIGN_DISABLED.md` | Future scheduler design, off by default |

Every run must update `phase-state`, the evidence index, and requirements traceability. Chat statements are not substitutes for files.

