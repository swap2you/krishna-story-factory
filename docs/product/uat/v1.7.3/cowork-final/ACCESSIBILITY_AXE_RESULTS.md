# V1.7.3 CoWork UAT — Fresh axe-core Scans (all primary families)

Method: axe-core 4.9.1 injected live, `wcag2a`+`wcag2aa` tags, each route rendered in a real 1440×900 same-origin iframe. These are fresh scans run by this reviewer, not a replay of the repo's Playwright axe evidence.

| Route | Hard violations | Incomplete color-contrast nodes* |
|---|---|---|
| `/` | 0 | 95 |
| `/library` | 0 | 80 |
| `/library/krishna-book` | 0 | 40 |
| `/library/srimad-bhagavatam` | 0 | 48 |
| `/knowledge` | 0 | 109 |
| `/knowledge/search` | 0 | 53 |
| `/learning/children-youth` | 0 | 64 |
| `/sunday-school` | 0 | 91 |
| `/teachers` | 0 | 78 |
| `/preachers` | **1 — `aria-required-children`, impact critical** | 79 |
| `/prabhupada-vani` | 0 | 81 |
| `/printables` | 0 | 131 |
| `/about` | 0 | 48 |
| `/contact` | 0 | 59 |
| `/faq` | 0 | 74 |
| `/stories/001` | **1 — `color-contrast`, impact serious (2 nodes)** | 99 |
| `/stories/009` | **1 — `color-contrast`, impact serious (2 nodes)** | 100 |

\* "Incomplete" = axe could not algorithmically resolve the backdrop (gradients/imagery). The homepage's card region was manually verified visually this cycle — cards now use artwork + solid dark-navy text panels (V1.5's DEF-CONTRAST-01 confirmed fixed). The incomplete counts are the expected benign consequence of the gradient/photo design language.

## Defect detail

### DEF-V173-01 — Story player Speed/Sleep selects fail contrast (serious)

- Nodes: `select[aria-label="Playback speed"]`, `select[aria-label="Sleep timer"]`
- Measured: foreground `#d5e0ec` on background `#ffffff` = **1.33:1** (requirement 4.5:1, 16px normal weight)
- Scope: audio player component → all 9 story pages
- Severity: P2. Controls remain operable and screen-reader-labeled; but their visible text (current speed / sleep state) is effectively illegible against white
- Recommended fix: darken the select text color (e.g., use the player's existing dark-navy text token)

### DEF-V173-02 — `/preachers` list semantics (critical impact, 1 node)

- Node: `.scope-grid[role="list"]` — children are `button[tabindex]`, not `role="listitem"`
- Impact: assistive tech list semantics broken for the "Reviewed stories" selector
- Severity: P2/P3. Recommended fix: wrap buttons in `role="listitem"` containers or drop `role="list"`

### Reconciliation with repo automated evidence

`apps/web/e2e/accessibility.spec.ts` samples only `/`, `/library/krishna-book`, `/teachers`, `/contact`, `/prabhupada-vani`, `/studio`, `/about` — story pages and `/preachers` are NOT in the sampled set. The official "axe critical/serious clean on sampled routes" claim is therefore accurate as stated; this review's findings extend coverage beyond the sampled set rather than contradicting it. Recommended: add `/stories/009` (or a story route) and `/preachers` to the sampled list.
