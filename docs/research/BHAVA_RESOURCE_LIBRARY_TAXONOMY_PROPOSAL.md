# Bhāva Resource Library — Taxonomy Proposal

**Status:** Research proposal for a future unified Resource Library. Does **not** block Stories production launch.  
**Inputs:** ISKCON education media reference audit; existing Knowledge pillars; Printables planned types; `/source-permissions` provenance categories.  
**Constraint:** Taxonomy enables discovery and governance; it does not authorize ingestion of uncleared third-party works.

---

## 1. Goals

1. One consistent facet set across Stories, Knowledge articles, Printables, Teacher packs, and future external-cleared resources.  
2. Make **rights** and **review** first-class filters (not footnotes).  
3. Support honest **Planned** / draft states without leaking private roadmap records to public search.  
4. Stay lightweight: CSV/JSON/SQLite-friendly; no mandatory CMS.

---

## 2. Facet model (proposed)

Every resource record SHOULD carry these facets. Required vs optional noted per field.

### 2.1 Audience / Age / Level

| Field | Cardinality | Example values | Required? |
| --- | --- | --- | --- |
| `audience` | multi | `children`, `youth`, `families`, `teachers`, `preachers`, `general` | yes |
| `age_band` | multi | `5-7`, `8-12`, `13-15`, `16-20`, `adult`, `all_ages` | recommended |
| `level` | single | `introductory`, `developing`, `deepening`, `facilitator` | recommended |

Align UI copy with homepage audiences (Little Listeners → Youth Leaders → Families & Educators).

### 2.2 Resource Type

| Field | Cardinality | Controlled vocabulary (v1) |
| --- | --- | --- |
| `resource_type` | single | `story`, `article`, `question`, `pathway`, `printable`, `lesson_plan`, `audio_narration`, `prayer`, `sloka`, `teacher_pack`, `preacher_outline`, `reference_policy`, `external_link` |

Map today’s surfaces:

| Surface | `resource_type` |
| --- | --- |
| `/stories/NNN` | `story` (+ linked `audio_narration`, `printable`) |
| Knowledge article | `article` |
| Knowledge Q&A | `question` |
| Pathway | `pathway` |
| Printables live assets | `printable` |
| Sunday School week | `lesson_plan` |
| `/source-permissions`, standards | `reference_policy` |

### 2.3 Format

| Field | Cardinality | Values |
| --- | --- | --- |
| `format` | multi | `html`, `markdown`, `pdf`, `png`, `mp3`, `txt`, `json`, `external_url` |

Stories packages already imply multi-format bundles; the library index may expose child assets as related records or as `format` multi on the parent.

### 2.4 Theme / Scripture

| Field | Cardinality | Values / pattern |
| --- | --- | --- |
| `theme` | multi | `krishna-book`, `practice`, `festival`, `values`, `holy-places`, `teacher-craft`, … |
| `scripture_work` | multi | `krishna_book`, `srimad_bhagavatam`, `bhagavad_gita`, `caitanya_caritamrta`, `ramayana`, `other`, `none` |
| `scripture_locator` | single string | Free text: “KB Ch. 6”, “SB 10.x”, etc. |

Keep `scripture_locator` human-readable; structured canto/verse IDs can come later.

### 2.5 Source / Publisher

| Field | Cardinality | Values |
| --- | --- | --- |
| `source_class` | single | `bhava_original`, `bbt_source_reference`, `third_party`, `pending_review` (match public provenance page) |
| `publisher` | single | `bhava`, `bbt`, `iskcon_education`, `temple:<id>`, `other:<name>`, `unknown` |
| `attribution` | text | Citation line shown in UI |
| `permissions_status` | single | Same as package manifest field where applicable |

### 2.6 Language

| Field | Cardinality | Values |
| --- | --- | --- |
| `language` | multi | BCP-47 tags: `en`, `hi`, … |
| `script_presentation` | multi | `latin`, `devanagari`, `iast_transliteration` |

Default launch corpus: `en`. Śloka records should declare script presentation explicitly when verses exist.

### 2.7 Review Status

| Field | Values | Public visibility |
| --- | --- | --- |
| `review_status` | `unreviewed`, `steward_review`, `scriptural_review`, `rights_review`, `approved`, `rejected`, `needs_revision` | Only `approved` (and explicitly allowlisted) in public loaders |

Editorial roadmap / 348 research records remain non-public until `approved`.

### 2.8 Rights Status

| Field | Values | Meaning |
| --- | --- | --- |
| `rights_status` | `bhava_owned`, `licensed`, `permission_documented`, `citation_only`, `link_out_only`, `unknown`, `blocked` | Gate for publish |
| `rights_doc_ref` | string | Pointer to internal clearance note (path or ticket id — **not** a secret) |
| `allowed_uses` | multi | `on_site_display`, `classroom_print`, `audio_stream`, `download`, `derivative_forbidden`, … |

**Rule:** `rights_status=unknown` or `blocked` ⇒ not publicly listed.

### 2.9 Published Status

| Field | Values | Notes |
| --- | --- | --- |
| `published_status` | `draft`, `planned`, `preview_internal`, `published`, `retired` | Public site shows `published` (+ honest `planned` shells without fabricating bodies) |
| `published_at` | ISO date | Optional |
| `slug` / `id` | string | Stable public id |

Honest empty states (e.g. planned crossword) are `published_status=planned` with no downloadable binary.

---

## 3. Record sketch (JSON)

```json
{
  "id": "res_story_009",
  "title": "Pūtanā Killed",
  "audience": ["children", "families"],
  "age_band": ["5-7", "8-12"],
  "level": "introductory",
  "resource_type": "story",
  "format": ["html", "mp3", "pdf", "png"],
  "theme": ["krishna-book", "values"],
  "scripture_work": ["krishna_book"],
  "scripture_locator": "Krishna Book — Chapter 6",
  "source_class": "bbt_source_reference",
  "publisher": "bhava",
  "language": ["en"],
  "review_status": "approved",
  "rights_status": "citation_only",
  "allowed_uses": ["on_site_display", "classroom_print", "audio_stream", "download"],
  "published_status": "published",
  "routes": ["/stories/009"],
  "related_ids": ["res_print_009_activity", "res_print_009_coloring"]
}
```

---

## 4. Public filters (future UI)

Recommended public filter chips (only over `published` + cleared rights):

1. Audience / age  
2. Resource type  
3. Format  
4. Theme / scripture work  
5. Language  

Do **not** expose `review_status` enums for drafts, internal reviewer names, or `rights_doc_ref` paths on the public site.

---

## 5. Alignment with existing Bhāva systems

| Existing | Facet bridge |
| --- | --- |
| Story `manifest.json` | Seed `source_class`, scripture, age_range, asset formats |
| Knowledge `meta.json` | Seed type, review, publish flags |
| Printables planned list | `resource_type=printable`, `published_status=planned` |
| Knowledge pillars (Sanātana-dharma, Practice, …) | Map into `theme` + optional `pillar` alias |
| `/source-permissions` | Canonical `source_class` vocabulary |

---

## 6. Implementation phases (non-blocking)

| Phase | Work | Launch impact |
| --- | --- | --- |
| P0 | Adopt vocabulary in docs + editorial checklists | None |
| P1 | Add facets to Knowledge meta + story web-manifest normalization | Low |
| P2 | Public Resource Library browse page using facets | Post-launch |
| P3 | External cleared resources as `external_link` or licensed assets | Post-rights |

---

## 7. Anti-patterns

- Using theme tags to imply official BBT endorsement.  
- Publishing `third_party` without `permission_documented`.  
- Mixing `planned` shells with fake worksheet PDFs.  
- Collapsing Level and Type into one free-text “category” field.  
- Rehosting reference-library files to “fill” taxonomy facets.
