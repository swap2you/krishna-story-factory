# 07 — Library UAT

## Collection cards — correct implementation

`/library`'s own collection cards (Krishna Book, Śrīmad-Bhāgavatam, Bhagavad-gītā, etc.) use a dark-navy solid text panel rendered over real photographic/artwork backgrounds (scrim/overlay-gradient technique). Manually inspected via `getComputedStyle` and visually — text is clearly legible against its backdrop.

## Accessibility scan

axe-core `color-contrast` returned `incomplete` (80 nodes) on this page too, but every sampled node's `failureSummary` cites `"background gradient"` (axe's known limitation: it cannot algorithmically resolve contrast behind CSS gradients) rather than the homepage's `"background color could not be determined ... obscured"` / fully-transparent pattern. This is the expected, benign axe limitation for a correctly-implemented gradient-scrim design, not a real defect. See file 04 for the full comparison against the homepage's genuine defect.

## Verdict for this section

**PASS.** `/library` demonstrates the design system's correct card pattern and is the reference implementation that the homepage's "CORE AREAS" cards should be brought in line with.
