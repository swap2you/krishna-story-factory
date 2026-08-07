---
id: PL-08
version: 1.0.0
phase: P01.R1
preconditions: all independent findings collected
---

# Consolidated remediation

Deduplicate findings by root cause. Create one prioritized remediation plan containing numbered items `1.1`, `1.2`, etc., mapped to requirements, evidence, paths, owner, and retest.

Fix all blocking correctness, source, doctrinal, rights, privacy, security, accessibility, Unicode, export, public-boundary, and acceptance issues in the current phase. Put genuinely cosmetic/non-blocking enhancements into the next-phase backlog with rationale.

After fixes:

1. run each targeted retest;
2. rerun the full required regression/validation matrix;
3. update traceability, as-built docs, manifests/hashes, findings status, and evidence;
4. repeat at most one additional consolidated cycle if new blocking findings emerge;
5. hard-stop after two failed full cycles on the same root cause.

Do not call the phase complete with hidden skipped tests or unsupported waivers.

