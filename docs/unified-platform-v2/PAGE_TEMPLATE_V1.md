# Knowledge Page Template V1 (frozen)

**Status:** FROZEN for Bhāva Unified Platform Build V2 / M2  
**Canonical anatomy:** `specs/01_VISIBLE_PRODUCT_SPEC.md` → “Canonical record page anatomy”  
**Web contract:** `apps/web/components/knowledge/`

This freeze locks the public/studio record-page anatomy. It does **not** authorize publication of scripture text. Devanāgarī / IAST / English bodies appear only when a package has cleared source/rights gates (or when rendering the private P01C structural fixture, clearly labelled).

## Anatomy (required order)

| # | Region | Contract | Component hooks |
|---|---|---|---|
| 1 | Hero | Title, one-sentence purpose, restrained art slot, status | `LearningPageShell` / `ArticleRecordShell` hero |
| 2 | Lens selector | Little Learner / Explorer / Teen / Study — one canonical text | `LensSelector` |
| 3 | Canonical text | Verified Devanāgarī → IAST → English (+ optional meanings) | Scripture packages only; **omitted** on Bhāva-original guides |
| 4 | Focus mode | Optional, keyboard-safe, preserves context | `FocusModeBar` |
| 5 | Context & practice | Source-grounded explanation + age-adaptive practice | Content blocks / article body |
| 6 | Trust panel | Sources, edition/locator, rights/use, version, review, correction route | `TrustPanel` |
| 7 | Related | Approved material only | Caller-supplied; no roadmap leakage |
| 8 | Downloads | PDF/DOCX only after export validation | Studio package exports only |

## Lens rules

- Default lens: **Explorer** (`DEFAULT_LENS`).
- Preference may persist in `sessionStorage` after explicit user selection only.
- URL sync: `?lens=&focus=&stanza=` (packages). Articles may omit stanza/focus params.
- Lens never invents a second canonical text.

## Focus mode rules

- Keyboard-safe stanza stepping on multi-stanza packages.
- Honors `prefers-reduced-motion`.
- Articles may offer a soft “reading focus” that dims chrome only — never synthesizes stanzas.

## Trust panel (always)

Every public Knowledge record and every studio preview must expose:

- source / review state
- edition or editorial provenance (honest gaps allowed)
- record/version identifiers when present
- correction route (`/knowledge/corrections`)

## Public Bhāva-original guides (current)

These use Template V1 **adapted** (hero + body + trust panel; no scripture sequence):

- `what-is-bhava`
- `source-and-permissions`
- `printing-and-classroom-use`

They are **not** scripture golden pages. No Devanāgarī/IAST/English verse bodies are fabricated for them.

## Frozen non-goals

- No dashboard chrome, neon gradients, or photoreal deity art in the template.
- No automatic publication from Studio or the draft factory.
- No public PDF serving of owner intake originals.
