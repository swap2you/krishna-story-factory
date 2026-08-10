# Execution Contract

## One release at a time

Cursor must not mix active release implementation paths. Finish, evidence, stage, promote, verify, tag, and close one release before beginning the next.

## Standard state machine

`BASELINE -> REQUIREMENTS_LOCKED -> IMPLEMENTING -> LOCAL_VALIDATION -> INDEPENDENT_REVIEW -> REMEDIATION -> DEVELOP_PUSHED -> CI_GREEN -> STAGING_VERIFIED -> PROMOTION_PR -> PRODUCTION_VERIFIED -> TAGGED -> CLOSED`

`BLOCKED` is reachable from any state.

## Before implementation

For each release Cursor must:

1. fetch remotes and confirm exact `develop`/`main` SHAs;
2. confirm a clean working tree or isolate unrelated user changes without stashing/resetting them;
3. read current requirements, ADRs, templates, tests, release manifests, runbooks, design tokens, and relevant prior evidence;
4. create atomic requirements and objective acceptance criteria;
5. map each criterion to implementation paths, test method, and required evidence;
6. freeze scope and exclusions in `RELEASE_STATE.yaml`;
7. record starting SHA and rollback pointer.

Do not ask the owner to repeat decisions already proven in current documents. When two current documents conflict materially, use implementation/runtime truth for current state and the most recent accepted requirement for intent. Record the resolution.

## Implementation rules

- Work on local `develop` only.
- Use existing architecture, components, tokens, templates, content contracts, export tooling, and test infrastructure.
- Prefer the smallest cohesive change that fully satisfies the release.
- No broad cleanup, speculative abstraction, framework migration, or dependency churn.
- Do not weaken, skip, delete, or rewrite a valid failing test to manufacture green status.
- A test must be hermetic in CI; it must not depend on ignored workstation media unless explicitly classified as an operational test.
- Keep private originals, ZIPs, databases, generated media, credentials, and workstation paths out of Git.
- Do not copy distinctive third-party wording, art, or layout into public work. Create original expression from verified facts and permitted source use.
- Never invent Sanskrit, translation, quotation, locator, reviewer, approval, permission, or runtime evidence.

## Bounded repair loop

When a gate fails:

1. capture the exact failure and reproduce it once;
2. compare it with the original requirement and expected evidence;
3. identify the root cause, not just the symptom;
4. apply the smallest complete fix;
5. rerun the affected test, then the required regression set;
6. update traceability and evidence;
7. repeat for at most three root-cause remediation cycles per release.

Do not count multiple edits addressing one diagnosed root cause as multiple speculative retries. If the same root failure survives three complete cycles, stop with `BLOCKER_REPORT.md` rather than looping forever.

## Independent review

After the implementation passes locally, use two read-only independent review contexts if Cursor supports them:

- Code reviewer: architecture, correctness, security, privacy, maintainability, duplication, test quality, unnecessary complexity.
- Experience reviewer: browser UX, visual fidelity, responsive behavior, accessibility, Unicode, export/render quality, source presentation.

Reviewers do not edit application paths. Cursor consolidates findings by root cause, fixes them in one remediation set, and reruns the full affected matrix. If independent contexts are unavailable, run clean-context review passes and record the limitation honestly.

## Commit and push

- Logical local commits are allowed on `develop` during a release.
- Push remote `develop` only after local validation and independent-review remediation pass.
- Never force-push, rewrite shared history, or delete commits.
- If CI fails after push, fix directly on `develop`, push the corrective commit, and keep the release open until green.
- Do not open a PR to `develop`.

## Staging and production

- A green `develop` SHA deploys to staging through the existing workflow.
- Verify the exact deployed SHA/content tag and complete smoke/browser/security checks.
- Create one `develop -> main` promotion PR for the completed major release.
- The promotion PR contains the release summary, evidence paths, rollback pointer, exact CI/staging evidence, and production plan.
- Merge only when required checks pass and the PR diff equals the staged release.
- Deploy the exact merged `main` SHA and immutable content tag.
- Verify production independently; do not infer success from workflow completion.
- Create the annotated major-release tag only after production passes.

## Hard stop conditions

Stop only for:

- missing or contradictory authoritative source for required scripture/translation/quote;
- missing credential, permission, paid-service approval, or environment access that cannot be safely substituted;
- overlapping uncommitted user changes on required paths;
- destructive history/data action outside this authorization;
- critical privacy/security leak;
- acceptance criteria that materially conflict and cannot be resolved from current authoritative documents;
- corrupt/mismatched immutable artifacts;
- the same root failure after three complete repair cycles;
- unavailable production dependency with no rollback-safe path.

Cosmetic choices, lint, type, unit/e2e failures, browser defects, console errors, layout problems, docs drift, stale screenshots, and ordinary CI failures are not hard stops.

