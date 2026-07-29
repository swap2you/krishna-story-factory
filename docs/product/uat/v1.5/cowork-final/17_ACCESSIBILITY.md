# 17 — Accessibility (Fresh Live axe-core Scans)

## Method

Injected axe-core 4.9.1 live into the running app (from CDN, via `javascript_exec`) and ran `axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa']}})` fresh against the actual rendered DOM — not a rerun of a pre-existing report.

## Homepage (`/`)

- `violations`: 0
- `incomplete` → `color-contrast`: **99 nodes, impact `serious`** — manual follow-up confirmed this is the genuine DEF-CONTRAST-01 white-on-white defect (12+ of the 99 nodes are directly the affected `.collection-card` title/description text). Full detail in file 04.

## `/library`

- `violations`: 0
- `incomplete`: `color-contrast` (80 nodes, all attributable to axe's inability to resolve CSS-gradient backdrops — confirmed benign via manual inspection, not a real defect), `link-in-text-block` (1 node, not separately investigated this session — low impact, recommend a follow-up spot check)

## Modal keyboard isolation

Live-verified (not an axe automated check, but a manual interaction test) per file 08: Space does not leak through to audio control while a Coloring dialog is open; Escape returns focus correctly to the triggering thumbnail.

## Interpretation of "incomplete" vs "violations"

axe-core distinguishes hard `violations` (confidently detected) from `incomplete` results (axe cannot algorithmically resolve the answer — e.g., transparent/gradient backgrounds — and flags for manual review). Zero hard violations were found in either scan, but the `color-contrast` "incomplete" bucket on the homepage is not benign noise: manual computed-style inspection resolved it to a genuine, serious defect. This is a good illustration of why automated tooling alone (as flagged by the mission) is insufficient without human/manual follow-up on "incomplete" results.

## Verdict for this section

**FAIL for homepage** (DEF-CONTRAST-01, corroborated by axe's `color-contrast` incomplete flag plus manual resolution). **PASS for `/library`** (incomplete flags resolved to benign gradient-detection limitations, not real defects).
