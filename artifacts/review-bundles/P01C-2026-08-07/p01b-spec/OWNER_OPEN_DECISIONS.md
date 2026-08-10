# Owner Open Decisions — P01B (resolved for P01C foundation)

Resolved by owner authorization on 2026-08-07 for P01C engineering foundation. Historical P01B statements elsewhere remain valid point-in-time evidence.

| OD | Decision | Resolution |
|---|---|---|
| **OD-01** | Visual direction | **Board B — editorial gouache** |
| **OD-02** | DOCX library | **`python-docx` (MIT) approved** for pinned install in P01C |
| **OD-03** | PDF a11y bar | **Capability-proven, not PDF/UA** (accepted for Phase 1 foundation) |
| **OD-04** | Export lens policy | **Study-neutral** PDF/DOCX (canonical text only) |
| **OD-05** | Default web lens | **Explorer** |
| **OD-06** | Lens URL contract | `?lens=` + optional `?focus=` + `?stanza=` |
| **OD-07** | Remember lens | **`sessionStorage` only after explicit user selection** |
| **OD-08** | Footer string | **`© {year} Svarna Gauranga Das · Dauji Publication · Bhāva`** (civil name removed) |
| **OD-09** | Preview URL | **`/studio/knowledge/preview/[slug]`** |
| **OD-10** | Private API binding | Studio session + **loopback**; deprecate forgeable `X-Bhava-Studio: 1` alone |
| **OD-11** | Package directory | **`content/knowledge/packages/<id>/`** |
| **OD-12** | FTS for pilot packages | **No new search indexing during pilot** |
| **OD-13** | Devanāgarī font | Load **Noto Serif Devanagari** (OFL) for preview; license noted in evidence |
| **OD-14** | Golden edition | **Still blocked** — production scripture/artwork not authorized; synthetic fixtures only |
| **OD-15** | Accept P01B package | **Accepted** |
| **OD-16** | Authorize P01C build | **Engineering foundation authorized**; merge/staging/production/publication/scheduler **not** authorized; draft PR only |

## Still blocked (not foundation)

- Actual Nṛsiṁha / confirmation-page scripture and production artwork  
- Merge of feature branch to `develop`  
- Staging / production / public publication / scheduler enablement  
- Etiquette/Deity Worship vertical (D10)  
- Shared non-loopback preview
