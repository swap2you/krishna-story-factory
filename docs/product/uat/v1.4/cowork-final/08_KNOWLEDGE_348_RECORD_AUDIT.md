# V1.4 Knowledge Library — 348-Record Roadmap Audit

## Verdict-relevant summary: the 348-record import claim is TRUE (positive finding, verified two independent ways)

This directly re-checks the V1.3 finding ("Missing/Contradicted — only 20 synthetic placeholder records existed against a real 348-record source"). In V1.4 this has been genuinely fixed.

## 1. File-level verification (local, on-disk)

`content/knowledge/roadmap/records.json`:
- Record count: **348** (`len(records) == 348`, verified programmatically).
- Lifecycle histogram: **`{"source_research": 348}`** — matches the mission's exact expected value.
- Sample record (`TOP-0001`):
```json
{
  "id": "TOP-0001", "pillar": "Sanatana-dharma", "cluster": "Foundations of Sanatana-dharma",
  "title": "What Sanatana-dharma Means", "content_type": "concept", "audience": "general",
  "level": "beginner_to_intermediate", "priority": "P1", "source_tier_required": "A1",
  "required_reviewer": "Scriptural reviewer", "visibility": "public",
  "package_status": "research_backlog", "lifecycle": "source_research",
  "provenance": {
    "source_file": "MyPilotDropbox\\bhava-knowledge-library-v1.0\\...\\data\\topic_backlog.csv",
    "source_line": 2,
    "source_csv_sha256": "1f28347ba4017cf1546fce53cf027483d77702c82da69839524d4b3b4c16cab3",
    "package": "bhava-knowledge-library-v1.0"
  }
}
```
Real titles, pillars, clusters, source tiers, and reviewer fields preserved (not generic "Backlog topic N" placeholders as in V1.3). Provenance back-references the exact source CSV row and its checksum.

`docs/knowledge/BHAVA_V1_4_RESOURCE_IMPORT_REPORT.md` claims source SHA-256 `1f28347ba4017cf1546fce53cf027483d77702c82da69839524d4b3b4c16cab3` for `MyPilotDropbox/bhava-knowledge-library-v1.0/.../data/topic_backlog.csv` — matches the `source_csv_sha256` recorded in every sampled record's provenance block.

## 2. Live, authenticated Editorial Studio verification (independent of the file check)

Logged into `/studio/knowledge` with the documented local bootstrap token (`bhava-local-studio`, role `steward` — a loopback-only dev credential explicitly documented in the page itself, not a production secret). The live UI, rendered from the running API (not from static file inspection), reported:
```
Roadmap total: 348 — Exact imported governed records
source_research: 348
Filter roadmap → Showing 348 of 348
```
Filters for lifecycle (`All lifecycles` / `source_research`) and pillar (Culture and Festivals, Devotee Lives, Editorial Standards, Gaudiya Vaisnavism, Holy Places, ISKCON, Practice, Prayer and Sloka, Questions, Sanatana-dharma, Teaching Resources) are present and functional. The record table lists ID/Title/Pillar/Type/Lifecycle/Reviewer/Tier columns, with `TOP-0001 | What Sanatana-dharma Means | Sanatana-dharma | concept | source_research | Scriptural…` matching the file-level record exactly.

This is a genuine two-source confirmation (static file + live authenticated API-backed UI) of the exact 348-record, single-lifecycle-state import the release claims.

## 3. Public-side gate (no leakage) — verified live

- Public Knowledge search API: `GET /api/v1/knowledge/search?q=Sanatana-dharma` → `{"count":0,"results":[],"engine":"sqlite_fts5","postgres_ready":true}`. None of the 348 `source_research` roadmap topics leak through public search, even when searching for an exact pillar name that exists 30+ times in the roadmap.
- Public search results page for the same query renders an honest **"No matches. Try another phrase or ask privately."** — no roadmap titles, no `TOP-####` IDs visible in the rendered page.
- Direct API probes: `GET /api/v1/knowledge/roadmap` → 404; `GET /api/v1/knowledge/roadmap/TOP-0001` → 404. The roadmap is not exposed as a public REST resource.
- `sitemap.xml` (5,250 bytes) does not reference `roadmap`, `/dev/audio-lab`, `/dev/logo-sheet`, or `/studio`.
- `robots.txt`: `Disallow: /studio` present (intentional, expected — not itself a leak, just a crawler directive).
- The Studio itself is gated behind the bootstrap-token sign-in; before authenticating, the same URL renders only the sign-in form, no data.

## Search engine honesty

`engine: "sqlite_fts5"` was reported directly by the live API response — confirms SQLite FTS5 is the actual runtime search engine, with `postgres_ready: true` as a separate, lower-confidence claim about migration readiness that this session did **not** independently verify (no PostgreSQL instance was connected to or queried this session; the DDL/migration files were not re-inspected). Per the mission's instruction, this review does not claim PostgreSQL is running — only that SQLite FTS5 demonstrably is.

## Not completed this session

- The remaining 347 roadmap records were not individually spot-checked against the source CSV row-by-row; only `TOP-0001` was compared field-by-field. The exact record count (348) and lifecycle histogram were verified programmatically across the full set, which is the primary claim at stake.
- The 12–16-pathway mega-menu / public IA requirement was not re-audited in depth this session (carried forward from V1.3's finding that no header mega-menu flyout exists; not re-tested).
