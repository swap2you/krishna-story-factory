# Test and Security Plan — Phase 1

## Policy

- Independent QA does not self-certify implementer work.  
- No PDF/UA claim (OD-03).  
- Node 24 for P01C web (D12).  
- Paid providers off.

## Matrix

| Layer | Coverage | IDs |
|---|---|---|
| Unit | Hash helpers, NFC/glyphs, gates, export serializer | E01–E03, E07, F09 |
| Integration | PDF/DOCX generate + manifest round-trip Letter/A4 | F07, E04–E07 |
| E2E | 4 lenses + focus + downloads; Chromium/Firefox/WebKit | F01–F07 |
| A11y | axe + keyboard + zoom + reduced motion + 44px | U01–U07 |
| Unicode | Conjunct/IAST fixtures web+PDF+DOCX | E02–E04 |
| Privacy | Research never public; noindex preview; no private paths | F09, U07, P01 |
| Security | Loopback+session; no forgeable-header-alone; secrets | F09, ADR-003 |
| Studio | Pagination shows all 348 under filters | F08 |
| Regression | Story packages; release pin; existing axe hubs | AGENTS, D09 |

## Suites to add in P01C

- `tests/test_knowledge_export_*.py`  
- `apps/web/e2e/knowledge-prayer*.spec.ts`  
- Extend `test_knowledge_v14.py` for preview boundaries  

## Threat model (summary)

| Threat | Control |
|---|---|
| Forge private search header | Loopback + session (ADR-003) |
| Public index of draft | noindex + sitemap deny + loader gates |
| Private path leakage | Redact provenance in public responses; no corpus in Git |
| Weak Studio token on shared host | Env-required secret; Secure cookies; D06 loopback |

## Exit for validation packet

All P0/P1 requirements PASS or OWNER_DEFERRED with risk; zero unresolved P0 privacy/source/security defects; hash parity web↔PDF↔DOCX.
