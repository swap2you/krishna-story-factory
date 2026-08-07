# UX Specification — Phase 1 Golden Prayer Page (Private Preview)

**Run:** `P01B-2026-08-07`  
**Surface:** Loopback Studio private preview (D06) — not public Knowledge publication  
**Scripture status:** `SOURCE_BLOCKED` until OD-14 / D03 edition  

## User and task

- **Primary task:** Read one multi-stanza prayer with authentic Devanāgarī, IAST, and verified English; optionally deepen via self-selected lens; optionally focus one stanza; consult source/review; download validated PDF/DOCX when ready.
- **Lenses:** Little Learner (5–7), Explorer (8–12), Teen (13–17), Study (18–22+). Numeric `min_age`/`max_age` + `presentation_profile` in data model.
- **Default (recommended OD-05):** Explorer.
- **No-account path:** Full read + lens + focus + source + downloads with zero signup; optional `sessionStorage` after explicit lens choice (OD-07).

## Information hierarchy

1. Hero — title, restrained art placeholder, review status  
2. Lens control  
3. Purpose (one sentence)  
4. Stanza sequence (canonical text always real text, never image-only)  
5. Focus mode toggle  
6. Context/story (only if source-grounded)  
7. Practice and remember (non-gamified)  
8. Source/review/correction  
9. Related (approved only)  
10. Downloads  

## States

| State | Behavior |
|---|---|
| Loading | Skeleton; `aria-busy`; no shimmer if reduced-motion |
| Ready | Full anatomy for current lens |
| Empty | Honest empty (public stubs today) |
| Blocked | Status + reason; **no** scripture body if SOURCE_BLOCKED/RIGHTS_BLOCKED |
| Error | Retry + correction/contact |
| Export unavailable | Disabled downloads + reason |
| Reduced motion | Instant show; no auto-advance |
| Focus on | One stanza; prev/next ≥44px; exit restores focus |
| Offline | Clear message |

## Interactions

- **Keyboard:** Tab through lens radiogroup → stanzas → focus controls → source → downloads; visible gold focus ring.  
- **Lens switch:** Preserve stanza position + restore focus (P1-F05).  
- **URL (OD-06 recommend):** `?lens=explorer|little_learner|teen|study` + optional `?focus=1` + `?stanza=<id>`.  
- **Download:** Only when export validation PASS; else disabled.  
- **D05:** Spec civil-name removal from footer — **do not implement in P01B**.

## Typography (evaluate; do not lock)

| Role | Current / candidate |
|---|---|
| Brand / headings / body | Tillana / Fraunces / Source Sans 3 (**VERIFIED** loaded) |
| Devanāgarī | Noto Serif Devanagari (named, **not loaded**) + license-check alternates |
| IAST | Prefer body font if glyph-complete; fixture `āīūṛṝṅñṇṭḍśṣṃḥ` |

**NFC** normalization policy for storage + export hash (P1-E02).

### Lens type density (recommended)

| | Little Learner | Explorer | Teen | Study |
|---|---|---|---|---|
| Devanāgarī | 1.5–1.75rem | 1.35rem | 1.25rem | 1.15rem |
| Measure | ≤40ch | ≤48ch | ≤60ch | ≤72ch |

## Artwork / motion

- Boards A/B/C in `VISUAL_DIRECTIONS.md` (placeholders only).  
- Motion: short semantic reveal only; honor `prefers-reduced-motion`.  
- No photoreal deities, meme/neon/AI-gloss, inconsistent tilaka, particles, cursor-follow.

## Identity (D05 specify-only)

Public footer must not include civil name `Swapnil Patil`. Exact replacement string → OD-08. Implementation deferred.

## Acceptance evidence

Map P1-U01–U07 and P1-F01–F06 to `REQUIREMENTS_TRACEABILITY.csv` and `TEST_AND_SECURITY_PLAN.md`.
