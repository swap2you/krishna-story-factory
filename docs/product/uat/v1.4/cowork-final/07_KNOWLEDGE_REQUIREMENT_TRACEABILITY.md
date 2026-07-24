# V1.4 Knowledge Library Requirement Traceability (update from V1.3)

Classification legend: Implemented and live / Implemented but incomplete / Scaffold only / Deferred with accepted reason / Missing / Contradicted / Not testable.

| Requirement | V1.3 finding | V1.4 status this session | Evidence |
|---|---|---|---|
| Nav "Knowledge", title "Bhāva Knowledge Library" | Implemented and live | **Unchanged, confirmed live** | `/knowledge` title/H1 |
| 348-resource governed roadmap import | **Missing/Contradicted** (only 20 placeholders) | **Implemented and live — fixed** | `08_KNOWLEDGE_348_RECORD_AUDIT.md`, two independent verifications |
| Public gate excludes roadmap/source_research records | Not testable (nothing to leak) | **Implemented and live** — now genuinely testable and passing | Public search returns 0 for a pillar name present 30+ times in the roadmap; direct API 404s |
| Editorial Studio role/workflow | Scaffold only (static disclosure page) | **Implemented and live** — real auth, real role list, real workflow display, real live data | `10_EDITORIAL_STUDIO_GOVERNANCE.md` |
| SQLite FTS5 search | Not explicitly confirmed | **Implemented and live, confirmed via API `engine` field** | `{"engine":"sqlite_fts5"}` |
| PostgreSQL-ready search | N/A | **Not independently verified** — API claims `postgres_ready: true`; no Postgres instance was queried this session | Not tested |
| Published seed content (articles/questions) | 6 items (3 articles + 3 questions), short of 20–30 target | **Unchanged: still 3 articles + 3 questions visible on `/knowledge`** | Screenshot of "Published guides" section |
| 16 named pathway mega-menu | Implemented but incomplete (no header flyout, card-grid only) | **Not re-tested this session** | Carried forward from V1.3, not re-verified |
| Rich per-type WYSIWYG editors | Scaffold only | **Unchanged — explicitly and honestly deferred** in `BHAVA_V1_4_RELEASE_CANDIDATE.md`'s "Residual non-blocking" section | Documentation review only |
| Source-authority tier display on public articles | Missing in V1.3 | **Not re-tested this session** | Not opened |
| Confidential-content restrictions | Not testable (nothing to leak) | **Not re-tested this session** — same published-content set as V1.3 | Not opened |

## Summary judgment

V1.4 delivers a genuine, verified fix to the single largest V1.3 Knowledge Library gap (the 348-record import) and a genuine upgrade to the Editorial Studio (from static stub to authenticated, role-aware, live-data console). The public-facing seed content depth (6 published items) and the mega-menu/source-tier-display gaps identified in V1.3 were not re-tested this session and should not be assumed fixed; they simply were not re-opened given the session's time allocation toward the two release-blocking checks (audio, automated-matrix authenticity).
