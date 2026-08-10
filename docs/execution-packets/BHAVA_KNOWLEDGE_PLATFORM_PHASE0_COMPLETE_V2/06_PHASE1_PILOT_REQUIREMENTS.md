# Phase 1 — Governed Visual Learning Page Pilot

## Goal

Prove the complete content-to-page-to-export system with one golden prayer/mantra page, then validate reuse with four additional pages. Everything remains private preview until later owner authorization.

## Recommended pilot composition

Final titles and exact texts must come from source discovery. Select:

1. one multi-stanza Nṛsiṁha prayer page as the golden implementation;
2. one short praṇāma-mantra collection/page;
3. one prasāda prayer page;
4. one single-verse/śloka page with word meanings;
5. one context-rich prayer page that exercises story/context and related content.

Do not invent text or choose a record whose source/rights are inadequate merely to fill a slot.

## Functional requirements

| ID | Requirement |
|---|---|
| P1-F01 | Render one canonical structured record through four self-selected depth lenses without duplicating the core text. |
| P1-F02 | Always show approved Devanāgarī, IAST, English translation, source/translator, revision, and review status. |
| P1-F03 | Support stanza-aligned artwork where it adds meaning; artwork per stanza is optional, not mechanical. |
| P1-F04 | Provide linear reading and optional one-stanza focus mode. |
| P1-F05 | Preserve reading position and accessible focus when switching lens/mode. |
| P1-F06 | Expose source/review/correction information without overwhelming younger views. |
| P1-F07 | Generate/download a validated PDF and DOCX from the same record version. |
| P1-F08 | Show all 348 roadmap records and lifecycle counts privately in Studio; do not expose them publicly. |
| P1-F09 | Prevent research/draft/restricted records and private source paths/files from public routes/search/API/sitemap/metadata. |
| P1-F10 | Support related approved content only; no dead or planned link presented as available. |

## UX and accessibility requirements

| ID | Requirement |
|---|---|
| P1-U01 | WCAG 2.2 AA target with keyboard, focus, contrast, reflow, headings, landmarks, labels, and alt-text rules. |
| P1-U02 | Primary child-facing targets use a 44×44 CSS-pixel design token; no target below applicable WCAG minimum. |
| P1-U03 | 320px/mobile, tablet, desktop, 200% and 400% zoom have no overlap, clipped diacritics, or lost content. |
| P1-U04 | Reduced-motion mode removes all nonessential movement; content never depends on animation. |
| P1-U05 | Informative art has reviewed alt/description; decorative art is programmatically ignored. |
| P1-U06 | Mature shared brand; younger lenses alter density/scaffolding, not the whole identity. |
| P1-U07 | No mandatory age/DOB, account, child profile, tracking, comment, upload, or personalization. |

## Text/export requirements

| ID | Requirement |
|---|---|
| P1-E01 | Canonical scripture/translation hash is identical across lenses and exports. |
| P1-E02 | Unicode normalization policy and glyph regression fixture cover used Devanāgarī conjuncts and IAST marks. |
| P1-E03 | Copy/search/print/export preserve approved characters and stanza boundaries. |
| P1-E04 | PDF has selectable Unicode text, embedded fonts, logical reading order/bookmarks/links/alt/language to the proven tool capability. |
| P1-E05 | DOCX uses real styles, headings, paragraphs, native images/alt text, language metadata, headers/footers, and opens without repair. |
| P1-E06 | US Letter and A4 have no split mantra/translation unit, clipped artwork, orphan heading, or blank overflow page. |
| P1-E07 | Export manifest records record/template/asset versions and hashes. |

## Technical constraints

- Reuse the existing stack and components after discovery. No framework migration.
- Prefer server-rendered content and small client islands for lens/focus/motion controls.
- No live Canva/Figma embed or external authoring tool as runtime/source of truth.
- No broad dependency upgrades, opportunistic refactor, or unrelated formatting.
- Accessibility of generated PDF is an early spike; do not claim PDF/UA conformance until the chosen pipeline proves it.

## Phase 1 sequence

1. Build source dossier and requirements for the golden page.
2. Produce three visual direction boards and one page wireframe; owner selects one.
3. Implement the golden page, four lenses, and both exports.
4. Run full source, devotional, Unicode, visual, accessibility, export, privacy, and regression validation.
5. Apply one consolidated remediation pack.
6. Freeze Page Template V1 only after owner acceptance.
7. Implement the four confirmation pages using the frozen template.
8. Rerun complete acceptance; prepare PR/evidence/as-built docs.

## Exit criteria

- 100% of requirements map to passing evidence or explicit owner-approved deferral.
- All five records have adequate dossiers, rights states, and required human reviews.
- Zero unresolved P0/P1 source, doctrinal, privacy, security, accessibility, Unicode, export, or public-boundary defect.
- Web/PDF/DOCX revision hashes agree.
- Private Studio clearly explains why each of the 348 records is not public.
- Clean local validation, logical commits, green CI, independent review packet.
- No staging/production/scheduler change.

