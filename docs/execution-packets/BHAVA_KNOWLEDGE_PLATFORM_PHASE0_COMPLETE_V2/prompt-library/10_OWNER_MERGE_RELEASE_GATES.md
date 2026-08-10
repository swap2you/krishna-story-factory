---
id: PL-10
version: 1.0.0
purpose: Enforce explicit protected-action approvals
---

# Owner, merge, staging, and production gates

Never infer approval from “looks good,” CI success, PR approval, or prior permission.

- Merge to `develop`: require owner approval for exact PR/head SHA after green CI and accepted evidence.
- Post-merge: validate from clean checkout at merged SHA and produce report.
- Staging: requires a separate explicit instruction naming target and exact build/SHA. Phase 1 default is no staging.
- Production/main/publication: requires separate explicit instruction after accepted staging evidence and release plan.
- Scheduler enablement: requires separate explicit instruction after scheduler phase dry/shadow gates.
- Remote branch deletion: requires explicit maintenance approval after reachability and post-merge proof.

If approval is absent, stop safely with a ready-to-act package and state the exact requested decision.

