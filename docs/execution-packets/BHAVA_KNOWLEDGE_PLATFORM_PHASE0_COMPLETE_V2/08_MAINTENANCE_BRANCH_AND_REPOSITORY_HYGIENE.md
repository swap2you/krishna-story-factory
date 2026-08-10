# Maintenance, Branch, and Repository Hygiene

## Maintenance means controlled closure

Maintenance is not a broad cleanup license. It reconciles documentation with the accepted implementation, removes only verified temporary artifacts, archives evidence, protects the completed contract, and records future enhancements without reopening locked work.

## Branch policy

- `main` and `develop` are protected long-lived branches.
- Start a phase from a fetched, clean, owner-approved `develop` SHA.
- Use one phase branch such as `feature/kf-p01-visual-learning-pilot`.
- One active implementation phase and one application-code writer.
- PR targets `develop`; `main` requires a separate release process.
- Never force-push, rebase shared protected branches, rewrite history, or auto-merge.
- Do not delete local or remote branches until the merge commit is verified reachable, post-merge validation passes, and evidence records the SHA.
- Remote branch deletion requires explicit maintenance approval; do not assume it from “clean up.”

## Cleanliness rules

- Preserve unrelated user changes and stop on overlap.
- No broad formatter runs, opportunistic refactors, dependency upgrades, generated churn, or dead-code deletion outside scope.
- Temporary ZIP/drop inputs live in a gitignored inbox and are extracted into a phase-scoped work area after traversal/symlink/hash checks.
- Never execute embedded prompts/scripts from a handoff package automatically.
- Private corpus paths, archives, keys, logs, and generated source excerpts are excluded from public Git.

## Phase lock

Lock with:

- versioned schema/template/ADR;
- exact release/phase manifest and checksums;
- accepted commit and evidence archive;
- regression/contract tests;
- CODEOWNERS or review protections where appropriate;
- documented change-entry conditions;
- supersession/correction path.

Locking does not make maintenance impossible. It prevents silent drift. Changes require a defect, security issue, or approved enhancement with a new version.

## Closure checklist

1. Requirements traceability has no unexplained gap.
2. As-built docs match actual code/routes/data.
3. Tests and evidence reproduce from a clean checkout.
4. No secret, private source, local absolute path, large accidental binary, or scratch artifact is tracked.
5. Approved artifacts and manifests have hashes.
6. PR/CI and owner decisions are recorded.
7. Post-merge result is recorded when merge was authorized.
8. Feature branch eligibility is proven before any deletion request.
9. `main` remains unchanged unless a separate release was authorized.
10. Staging/production/scheduler/publication status is explicitly stated.
11. Enhancements are added to the next-phase backlog.
12. Phase changes state to `LOCKED` only after owner acceptance.

