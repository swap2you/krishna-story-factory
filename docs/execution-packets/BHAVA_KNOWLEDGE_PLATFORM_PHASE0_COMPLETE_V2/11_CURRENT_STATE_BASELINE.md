# Current-State Baseline Carried Forward from Phase 0

**Observed:** 2026-08-06. Reverify at implementation time; repository and live state can change.

## Public platform repository

| Item | Phase 0 evidence |
|---|---|
| Repository | `swap2you/krishna-story-factory` |
| Remote branches | `main`, `develop` only |
| Open PRs | none |
| `main` SHA | `257692f2d927d2215cf7a07efa22411f4cf46db9` |
| `develop` SHA | `d6159e9af6b7033d1876141eae31944ec93fffc0` |
| Relationship | `develop` one sync merge ahead; no file delta reported |
| Production content tag | `bhava-content-001-022-v1` |
| Public story maximum | 22 |
| Story 023 | private; live route returned 404 during narrow audit |

Do not treat these SHAs as permission or as permanently current. Phase 1A must fetch/read-only verify the repository, clean working tree, remote branches, PRs, release manifest, and public/private boundary before any branch or edit.

## Existing Knowledge foundation

- 348 roadmap records exist at the reported path `content/knowledge/roadmap/records.json`.
- All 348 were reported in research/backlog lifecycle, not publication-ready.
- SQLite FTS5 public search and PostgreSQL-target DDL exist; SQLite is current, PostgreSQL is not a deployed fact.
- Thirteen preliminary content templates and a partial private Studio exist.
- Public Knowledge/search/pathways and seeded records exist.
- Current schema logic is fragmented across roadmap JSON, TypeScript, Python, and SQL.

Phase 1 must reuse and consolidate this foundation—not rebuild it blindly.

## Routes and information architecture

- Preserve Home, Knowledge, Library, Learning, Prabhupāda Vāṇī, About, Contact.
- `/blog` redirects to `/knowledge`.
- Private Studio/factory/draft routes remain outside the public allowlist.
- Worksheets, printables, e-books, audio, and podcasts remain formats/assets under the four pillars rather than top-level navigation tabs.

## Known risks to reverify

- Public footer reportedly exposed `Svarna Gauranga Das (Swapnil Patil)`, conflicting with locked public-identity policy.
- Exact live Story 022 manuscript/audio behavior was not conclusively verified because the prior browser could not call the site's API.
- The actual private corpus bytes/catalog and the user's local Windows working tree were unavailable in the prior workspace.
- Existing content templates omit some robust provenance, claims/evidence, review, rights, correction, adaptation, and asset controls.
- Private Studio authentication must not rely on headers alone in production.

## Separate repository state

- `bhava-library` Phase 0 reported branches `main`, `feature/library-curation-v1`, and `fix/curation-quality-v1.1`, with PR #2 open. This package does not authorize merging it.
- `bhava-publishing-studio` baseline was reported but not independently reverified.
- No private corpus originals are included in this package.

