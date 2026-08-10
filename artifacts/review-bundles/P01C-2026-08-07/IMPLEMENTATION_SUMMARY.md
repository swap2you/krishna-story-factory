# P01C Implementation Summary

## Scope delivered

Smallest complete vertical foundation for the Knowledge learning page:

| Area | Delivery |
|---|---|
| Schema | `packages/contracts/schemas/knowledge_record_package.schema.json` + loaders |
| Fixture | `content/knowledge/packages/KF-P01C-FIXTURE-001/` — `SOURCE_BLOCKED`, conspicuous `TEST FIXTURE` labels |
| API | Private package list/detail; forgeable `X-Bhava-Studio: 1` alone rejected; secret + loopback required |
| Studio | Roadmap pagination (50/page), package queue, loopback gate |
| Preview | `/studio/knowledge/preview/[slug]` — signed session + loopback Host |
| Lenses | Little Learner / Explorer / Teen / Study; APG radiogroup; `sessionStorage` after explicit choice |
| Shell | Stanzas, focus mode, context/practice/source/download, Board B tokens, placeholders |
| Export | Study-neutral PDF (vendored Noto embedded) and DOCX (`python-docx`) with canonical hash manifests; DOCX uses `font_resource_hashes` / `fonts_embedded:false` (OOXML embedding deferred) |
| Footer | `© 2026 Svarna Gauranga Das · Dauji Publication · Bhāva` |

## Owner decisions applied

- OD-01 Board B editorial gouache  
- OD-02 `python-docx` pinned  
- Explorer default; `?lens=` URL; sessionStorage after selection  
- Study-neutral exports  
- Loopback-only authenticated Studio preview  
- No new FTS indexing  
- Approved Bhāva/Dauji footer  
- Production scripture/artwork blocked  

## Explicitly not delivered

- Real Nṛsiṁha / prayer bodies  
- Production artwork  
- Public publication  
- Merge / staging / production / scheduler  
- Etiquette PDF restoration (recovery manifest only)
