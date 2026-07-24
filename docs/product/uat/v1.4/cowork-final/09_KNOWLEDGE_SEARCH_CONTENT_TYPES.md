# V1.4 Knowledge Search and Content Types (partial)

## Search — verified live

- Engine: `sqlite_fts5` (confirmed via live API response field, not assumed).
- Zero-result query (`Sanatana-dharma`, a term/pillar name present in the private 348-record roadmap but not in the 6 published items) correctly returns **0 public results** with an honest "No matches. Try another phrase or ask privately." UI and `zero_result_suggestions` (bhakti, Prabhupāda, Bhagavad-gītā, Sunday School, deity worship) — no fabricated or leaked content.
- Private Studio search/filter (lifecycle + pillar) verified live and functional against the full 348 — see `08_KNOWLEDGE_348_RECORD_AUDIT.md`.

## Not tested this session

- A successful (non-zero-result) public search query was not tried against the 6 real published items (e.g., searching "printing" or "sources and permissions") to confirm relevant-result ranking, snippet quality, and correct exclusion of non-public state.
- Diacritic/non-diacritic/alternate-spelling search behavior was not tested.
- Per-content-type audit (article/question/prayer/ārati/śloka/stuti/learning-path/checklist/glossary/teacher-resource/preacher-resource/policy-standard/source-guide) against the "schema exists / loader exists / editor form exists / route exists / representative record works" checklist was not performed this session. The only content types with a live, published representative confirmed this session are **article** and **question/FAQ** (both present in the "Published guides" list on `/knowledge`); prayer/śloka/ārati/stuti templates were reported empty in V1.3 ("No reviewed items published yet") and were not re-opened this session to confirm whether that is still the case.
- PostgreSQL DDL/migration/adapter tests were not inspected this session (see `08_KNOWLEDGE_348_RECORD_AUDIT.md` — the `postgres_ready: true` API claim is unverified, not confirmed or contradicted).
