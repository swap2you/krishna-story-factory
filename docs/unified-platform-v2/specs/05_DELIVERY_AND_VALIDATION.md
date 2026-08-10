# Delivery, Quality, and Evidence Contract

## Continuous fix loop

For every failed gate: reproduce once, compare to the stated criterion, find the root cause, apply the smallest complete fix, rerun focused checks and relevant regression, update traceability/evidence. Three complete attempts at the same root cause is the limit; then issue one consolidated blocker rather than endless mutation.

## Required quality gates

| Area | Required proof |
|---|---|
| Code | configured formatter/lint/type checks, focused and full Python/web tests, existing security/audit gates, existing Sonar gate if configured |
| Browser | production/standalone build; desktop/tablet/mobile; all major happy/error/privacy paths; no unexpected console/network errors |
| UX | Board B consistency; 320px, 200%, 400% reflow; keyboard/focus; semantic headings/landmarks; reduced motion; 44px primary targets |
| Text/exports | NFC/NFD and IAST/Devanāgarī fixtures; selectable text; PDF/DOCX open/render/extract; accurate capability claims only |
| Content | dossier/rights/claim/review evidence; canonical/asset/export hashes; no invented text or fake approval |
| Security/privacy | external checks prove Studio/local/mutation/source paths are denied; no private data in sitemap/API/metadata/logs |
| Release | exact SHA/tag/digest in CI, staging, production; rollback pointer; public/private boundary smoke; current documents agree |

## Hard stops

Stop only for: missing/contradictory authoritative source for required text; permission/credential/environment access that cannot be safely substituted; overlapping user edits on required paths; destructive action outside authorization; P0 privacy/security leak; corrupt immutable artifacts; materially conflicting criteria; or the same root failure after three full remediation cycles.

An ordinary test, browser, build, layout, documentation, CI, deployment, or visual failure is not a stop condition.

## Cumulative promotion gate

One final promotion PR is permitted only when:

1. all implementable program milestones pass;
2. each blocked source-dependent item is honestly withheld from public routes and recorded;
3. staging verifies exact intended public records and denies all private/draft records;
4. production diff matches staging SHA/content artifacts;
5. final evidence ZIP, rollback pointer, and release manifest are complete.

If a non-core source record remains blocked but the platform itself is complete, it may remain private only if no public feature claims it is available and the final evidence names it exactly.

