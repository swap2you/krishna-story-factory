# Age-Adaptive UX and Design System

## Core recommendation

Do not build one childish page for everyone, and do not maintain four copies of each prayer. Store one verified canonical text and expose four self-selected presentation lenses.

| Lens | Typical age | Presentation | Content depth |
|---|---:|---|---|
| Little Learner | 5–7 | largest type, one stanza/idea at a time, direct illustration, short prompts | one-sentence meaning and one action |
| Explorer | 8–12 | illustrated vertical narrative, word meanings, memory cues | simple context and practical lesson |
| Teen | 13–17 | calmer visual density, philosophy/context, reflection | deeper explanation and application |
| Study | 18–22+ | compact scholarly layout, citations, variants, glossary | full notes and source/review detail |

Use numeric `min_age`/`max_age` plus a configurable `presentation_profile`; do not hard-code a universal age enum. The immutable mantra/verse and verified translation remain the same across lenses. Adaptations alter explanation, scaffolding, examples, and density—not doctrine.

## Canonical prayer/mantra page anatomy

1. **Hero:** title, restrained devotional artwork, record/review status.
2. **Purpose:** one sentence explaining when/why the prayer is used.
3. **Stanza sequence:** each stanza is a content unit with:
   - Devanāgarī Sanskrit;
   - IAST Roman transliteration;
   - verified English translation;
   - optional word meanings;
   - governed illustration;
   - age-lens explanation.
4. **Focus mode:** one stanza at a time for memorization; never the only access path.
5. **Context/story:** only when source-grounded and relevant.
6. **Practice and remember:** age-appropriate, non-gamified devotional prompt.
7. **Source/review panel:** edition, exact locator, translator/rights, reviewers, date/version, correction link.
8. **Related learning:** approved records only.
9. **Download:** print/PDF and DOCX when artifact validation passes.

### Important text rule

Never put Sanskrit or translation only inside an image. W3C guidance favors genuine text because it scales and adapts; artwork must not become the authoritative text source.

## Visual system

- Deep navy, muted gold, ivory/cream, restrained saffron/lotus/sage.
- Use generous whitespace and editorial rhythm; avoid cartoon-dashboard density.
- Typography must support Devanāgarī shaping and full IAST diacritics. Candidate fonts are discovered and license-checked in Phase 1; do not lock a font before render tests.
- Illustration direction options for the owner review:
  1. refined hand-painted devotional storybook;
  2. clean gouache/editorial illustration;
  3. restrained cut-paper/relief with subtle texture.
- Avoid photoreal deity depictions, meme aesthetics, neon gradients, generic AI-gloss, inconsistent tilaka/tulasī, excessive particles, and cursor-following effects.

## Motion contract

Allowed motion is short, calm, and semantic: gentle stanza reveal, tab/focus transition, progress indication, and subtle illustration depth. No infinite floating elements, auto-advancing scripture, scroll hijacking, or animation required to obtain content.

All nonessential motion must respect `prefers-reduced-motion`; the reduced path must preserve meaning and functionality.

## Artwork governance

Every asset requires:

- stable asset ID and linked record/stanza;
- source prompt/brief and model/tool/version if generated;
- reference-image provenance and permission status;
- theological/iconographic checklist;
- age suitability and cultural review;
- alt text or explicit decorative classification;
- width/height/aspect/crop variants;
- checksum, license/rights, reviewer, status, and supersession.

Generate only after the exact stanza/context is approved. Asset agents may propose briefs/concepts; they do not invent events or iconography.

## Responsive behavior

- Mobile is the primary reading test; stanza text never becomes horizontally scrollable.
- Desktop may pair text and image; mobile stacks them in reading order.
- Touch targets meet WCAG 2.2 minimum guidance; keyboard focus is visible.
- 200% zoom must retain content and controls without overlap.
- All toggles use explicit labels and preserve a sensible no-JavaScript reading path where practical.

## Accessibility target

Target WCAG 2.2 AA. Include semantic headings, language attributes where applicable, keyboard operation, contrast, focus visibility, text reflow, reduced motion, alt-text decision rules, and automated plus manual testing.

## Child privacy posture

Phase 1 requires no child account, profile, behavioral tracking, comments, uploads, voice input, or personalized recommendations. Default to minimal data collection. Introducing any such feature requires separate privacy/legal review; this is not merely a UX enhancement.

## Web/PDF/DOCX single-source strategy

- Canonical structured blocks are the source of truth.
- Web renders the blocks directly.
- PDF uses a governed print layout with `@media print`, `@page`, and modern break properties plus rendered visual QA.
- DOCX is generated from the same blocks with a simpler editable template. Exact pixel parity with the website is not a valid requirement; semantic fidelity, readable styles, Unicode accuracy, images, citations, headers/footers, and page breaks are.
- Export manifests record record version, template version, asset hashes, generated date, and validation results.

## UX acceptance criteria

- Same canonical verse/translation hash across all age lenses and exports.
- User can switch depth without losing reading position.
- Devanāgarī and IAST render correctly on tested platforms and exports.
- Each informative image has useful alt text; decorative images are ignored by assistive technology.
- Full content remains usable with reduced motion.
- No layout overlap at mobile widths or 200% zoom.
- PDF and DOCX pass text extraction/Unicode checks and human visual review.
- Source/reviewer/version status is visible and understandable.

