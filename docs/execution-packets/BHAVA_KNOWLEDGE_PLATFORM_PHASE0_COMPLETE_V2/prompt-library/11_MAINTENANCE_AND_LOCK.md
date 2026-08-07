---
id: PL-11
version: 1.0.0
purpose: Close and protect an accepted phase
---

# Maintenance and phase lock

Reconcile as-built docs with the accepted SHA. Archive phase inputs, approvals, source/asset manifests, traceability, evidence, checksums, PR/CI and post-merge results. Remove only known temporary phase artifacts. Verify no private source, secret, absolute local path, accidental binary, or scratch file remains.

Lock schema/template/ADR with version and regression tests. Record ownership and change-entry conditions. Move enhancements to the next phase backlog. Do not silently improve locked files.

Evaluate local/remote feature branch cleanup only after commit reachability and explicit approvals. Never delete `main`, `develop`, unmerged work, user changes, evidence, manifests, source vault objects, or audit history.

Produce `MAINTENANCE_RECORD.md` and `PHASE_CLOSURE.md`; state all branches/SHAs and staging/production/scheduler/publication status.

