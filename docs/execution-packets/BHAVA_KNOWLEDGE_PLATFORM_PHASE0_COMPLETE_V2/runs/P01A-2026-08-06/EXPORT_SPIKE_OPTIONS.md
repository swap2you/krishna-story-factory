# Export Spike Options — P01A

**Constraint:** No dependency preselected blindly; no installs in P01A. Accessibility of PDF is an early spike — do not claim PDF/UA until proven.

## Existing capabilities (VERIFIED)

| Capability | Stack | Fit for Knowledge prayer pages |
|---|---|---|
| Activity sheet PDF | Python `reportlab` | Partial — Unicode/layout experience; wrong document model |
| PDF stamp/merge | `pypdf` / `pypdfium2` | Post-process only |
| In-browser PDF view | `pdfjs-dist` (`PdfJsViewer`) | Viewer reuse after server generate |
| HTML `window.print` | story / teachers / preachers | Interim preview only — not P1-F07 |
| TXT blob download | story notes / class packs | Not DOCX |
| DOCX libraries | **none** in package manifests | Greenfield |

## Spike options (PROPOSED — evaluate in P01B/C after owner auth)

### PDF

| Option | Pros | Cons | Evidence needed |
|---|---|---|---|
| A. Server `reportlab` platypus flowables | Already in factory; Python-controlled fonts | Complex a11y/bookmarks; not PDF/UA by default | Selectable text, embedded Devanāgarī/IAST fonts, reading order, Letter/A4 |
| B. HTML→PDF (Playwright/Chromium print) | Visual parity with web | Heavier runtime; font embedding/a11y uneven; CI cost | Same checks + deterministic hashes |
| C. External managed PDF API | Fast | Paid provider; forbidden without auth; data egress | Reject unless owner approves |

**Recommendation to spike first:** Option A (reuse reportlab) with a minimal prayer template; keep B as fallback if Devanāgarī shaping fails. Option C out of scope by default.

### DOCX

| Option | Pros | Cons | Evidence needed |
|---|---|---|---|
| 1. `python-docx` | Real styles/headings/images/alt | New dependency (owner must approve install) | Opens without repair; styles; lang metadata |
| 2. OOXML template fill | Deterministic | More engineering | Same |
| 3. Pandoc subprocess | Flexible | Extra binary; supply-chain | Same |
| 4. Client-only DOCX | No server dep | Weak control; harder hashing | Likely reject |

**Recommendation:** Spike Option 1 only after owner approves adding one library; document license and pin in lockfile.

## Shared export contract (required by P1-E*)

- Same canonical scripture/translation hash as web lenses  
- Manifest: record/template/asset versions + hashes  
- US Letter and A4 without split mantra units  
- No inventing text during export  

## Out of scope for Phase 1

- Live Canva/Figma embed  
- Claiming PDF/UA conformance before spike evidence  
- Broad dependency upgrades unrelated to chosen spike
