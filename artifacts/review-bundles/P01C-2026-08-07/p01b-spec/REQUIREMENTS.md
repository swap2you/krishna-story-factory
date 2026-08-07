# Requirements — Phase 1 Visual Learning Pilot (P01B)

**Run:** `P01B-2026-08-07`  
**Status:** Specification — not implemented  
**Inheritance:** `06_PHASE1_PILOT_REQUIREMENTS.md` + P01A evidence + `OWNER_DECISIONS.md`

## Priority legend

`P0` = blocks pilot exit · `P1` = required for Phase 1 · `P2` = important · `P3` = backlog

## Functional

| ID | Requirement | Rationale | Acceptance | Validation | Priority | Deps | Exclusions |
|---|---|---|---|---|---|---|---|
| P1-F01 | Render one canonical structured record through four self-selected depth lenses without duplicating core text | Age adaptation without doctrinal drift | Same `scripture_hash`+`translation_hash` across lenses; scaffolding differs | Hash unit + e2e lens switch | P0 | CONTENT_MODEL | Four content copies |
| P1-F02 | Always show approved Devanāgarī, IAST, English translation, source/translator, revision, review status | Fidelity / transparency | All fields visible in every lens (density may vary) | Visual + a11y | P0 | D03 text | Invented text |
| P1-F03 | Support stanza-aligned artwork where it adds meaning | Comprehension | Art optional per stanza; never sole text carrier | Asset policy + visual QA | P1 | OD-01 | Photoreal deities |
| P1-F04 | Linear reading and optional one-stanza focus mode | Memorization without trapping users | Focus never sole path; exit restores context | E2E keyboard | P0 | UX | Auto-advance scripture |
| P1-F05 | Preserve reading position and accessible focus when switching lens/mode | Continuity | Focus return + stanza in view after switch | E2E a11y | P0 | OD-06 | — |
| P1-F06 | Expose source/review/correction without overwhelming younger views | Progressive disclosure | Little Learner collapsed source; Study open | UX review | P1 | — | Private path strings |
| P1-F07 | Generate/download validated PDF and DOCX from same record version | Single-source export | Manifest hashes match web; Letter+A4; DOCX opens without repair | Export suite | P0 | OD-02, OD-03, OD-04 | Paid PDF APIs; PDF/UA claim |
| P1-F08 | Show all 348 roadmap records and lifecycle counts privately in Studio | Governance visibility | Counts + pagination covering all 348 | Studio e2e | P0 | — | Public exposure |
| P1-F09 | Prevent research/draft/restricted records and private source paths from public routes/search/API/sitemap/metadata | Privacy boundary | Public listRoadmap=0; preview noindex; no Dropbox paths in public responses | Security tests | P0 | D06 | Shared preview without real auth |
| P1-F10 | Related approved content only; no dead/planned as available | Honest IA | Related links resolve to approved/published only | Link audit | P1 | — | Fake availability |

## UX / accessibility

| ID | Requirement | Acceptance | Validation | Priority |
|---|---|---|---|---|
| P1-U01 | WCAG 2.2 AA target | Keyboard, focus, contrast, reflow, headings, landmarks, labels, alt rules | axe + manual SR | P0 |
| P1-U02 | Child-facing targets use 44×44 CSS-pixel token | `--bhava-target-min: 44px`; no target below WCAG min | Visual + e2e | P1 |
| P1-U03 | 320px / tablet / desktop / 200% / 400% zoom: no overlap, clipped diacritics, or lost content | Matrix PASS | Visual QA | P0 |
| P1-U04 | Reduced-motion removes nonessential movement; content never depends on animation | Full content usable | prefers-reduced-motion e2e | P0 |
| P1-U05 | Informative art has reviewed alt; decorative ignored | Manifest alt or decorative flag | Review + axe | P1 |
| P1-U06 | Mature shared brand; lenses alter density/scaffolding not identity | Same tokens/chrome | Design review | P1 |
| P1-U07 | No mandatory age/DOB, account, child profile, tracking, comment, upload, or personalization | Self-selected lens only | Privacy audit | P0 |

## Text / export

| ID | Requirement | Acceptance | Validation | Priority | Deps |
|---|---|---|---|---|---|
| P1-E01 | Canonical scripture/translation hash identical across lenses and exports | Byte-equal hashes | Unit + export | P0 | OD-04 |
| P1-E02 | Unicode NFC policy + glyph regression fixtures | Fixture PASS web+PDF+DOCX | Unicode suite | P0 | OD-13 |
| P1-E03 | Copy/search/print/export preserve approved characters and stanza boundaries | Round-trip extract | Export extract | P0 | — |
| P1-E04 | PDF selectable Unicode, embedded fonts, logical order/bookmarks/links/alt/lang **to proven tool capability** | Documented capability matrix; **no PDF/UA claim** | Spike evidence | P0 | OD-03 |
| P1-E05 | DOCX real styles, headings, paragraphs, native images/alt, language metadata, headers/footers; opens without repair | Checker + human open | DOCX suite | P0 | OD-02 |
| P1-E06 | US Letter and A4: no split mantra unit, clipped art, orphan heading, blank overflow | Visual QA both sizes | Export visual | P0 | — |
| P1-E07 | Export manifest records record/template/asset versions and hashes | Manifest schema complete | Integration | P0 | — |

## Privacy / identity (specification)

| ID | Requirement | Notes | Priority |
|---|---|---|---|
| P1-P01 | Loopback-only Phase 1 preview (D06) | Shared preview = separate owner auth | P0 |
| P1-P02 | Specify civil-name removal from public footer (D05); do not implement in P01B | OD-08 exact string | P2 |
| P1-P03 | No paid providers / no arbitrary third-party downloads for sources | D03 process | P0 |

## Studio / roadmap

| ID | Requirement | Notes | Priority |
|---|---|---|---|
| P1-S01 | Studio pagination for all 348 rows | Fix 200-row cap | P0 |
| P1-S02 | Honest explanation why research rows are not public | Copy in Studio | P1 |

## Explicit exclusions (Phase 1)

- Framework migration; Postgres cutover; audio/podcast/3D  
- Public publication of pilot pages; staging/production deploy; scheduler changes  
- Story Factory / `RELEASE_CONTENT` / public_story_max code changes (D09)  
- Etiquette/Deity Worship vertical until D10 sources restored  
- Fabricated Sanskrit/translation/approvals  
- Dependency installs during P01B (D08 spike docs only)

## Owner decisions affecting requirements

See `OWNER_DECISIONS.md` (D01–D12) and `OWNER_OPEN_DECISIONS.md` (OD-01–OD-16).
