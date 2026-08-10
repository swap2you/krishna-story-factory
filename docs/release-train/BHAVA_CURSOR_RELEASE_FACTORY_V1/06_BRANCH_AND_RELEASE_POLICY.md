# Lean Branch and Release Policy

## Develop

- `develop` is the sole integration/release branch.
- Owner-authorized direct pushes are allowed.
- No feature/fix/docs/sync/release branch and no PR to `develop`.
- Cursor pushes only release-scoped commits that already pass local gates.
- CI remains evidence, not a branch-creation trigger.

## One-time GitHub configuration check

Cursor must inspect classic branch protection and repository/org rulesets affecting `develop` and `main`.

If `develop` requires PRs or blocks owner direct pushes:

1. capture the current configuration in sanitized evidence;
2. ensure equivalent `main` protection exists independently;
3. remove or narrow only the rule coverage for `develop` so owner direct pushes work;
4. leave `main` PR/check protections unchanged;
5. read back both effective configurations;
6. record the exact change and rollback method.

Do not delete a repository-wide ruleset that protects `main` until a `main`-only equivalent is active. Do not enable force pushes or deletion. If Cursor lacks admin authority, report this single configuration blocker; continue local preparation but do not fabricate a successful direct push.

## Main

- `main` stays protected and production-aligned.
- Exactly one promotion PR per completed major release.
- PR head is `develop`; base is `main`.
- No additional release branch.
- Required checks and staging evidence must pass.
- Production deployment uses the exact merged `main` SHA.

## Tags

- Use repository-established naming when present.
- Otherwise use annotated code tag `bhava-rNN-<slug>-v1` and immutable content tag where applicable.
- Never move or overwrite a published tag.
- Tag only after production verification.

## Rollback

- Record pre-release production SHA/content tag before deployment.
- Use the existing rollback workflow.
- Never use `git reset --hard` against shared branches, force-push, or retag history as rollback.
- A failed release remains evidenced and is repaired forward unless the runbook calls for redeploying the prior immutable version.

