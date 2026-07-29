# V1.3 Knowledge Resource Status Counts

## Published content — exact counts from `content/knowledge/`

| Type | Directory | Count | Slugs |
|---|---|---:|---|
| Articles | `content/knowledge/articles/` | 3 | `printing-and-classroom-use`, `source-and-permissions`, `what-is-bhava` |
| Questions | `content/knowledge/questions/` | 3 | `does-bhava-collect-child-data`, `is-bhava-official-bbt`, `what-is-bhava-faq` |
| Prayers | (no dedicated directory found; `/knowledge/prayers` renders "No reviewed items published yet") | 0 | — |
| Ślokas | (no dedicated directory found; `/knowledge/slokas` renders "No reviewed items published yet") | 0 | — |
| Pathways | `content/knowledge/pathways/index.json` | 16 total, 4 `published` / 12 `proposed` | See main report |

**Total live public Knowledge content items: 6** (3 articles + 3 questions). The V1 release target
stated in the blueprint's executive decisions is "20-30 fully reviewed seed resources" — the live count
is well under that target.

## Roadmap / proposed-resource backlog — the 348-vs-20 finding

`content/knowledge/roadmap/index.json`:
```json
{
  "schema_version": "1.0",
  "note": "348-resource backlog is metadata only; not published content.",
  "records": [ /* 20 records, "roadmap-001" .. "roadmap-020" */ ]
}
```
- Record count: **20** (verified programmatically: `len(records) == 20`).
- All 20 records: `status: "proposed"`, `content_type: "article"`, `title: "Backlog topic N"` (generic
  placeholder, not a real working title).

Compare to the actual source research package,
`MyPilotDropbox/bhava-knowledge-library-v1.0/Bhava_Knowledge_Library_Research_and_Cursor_Prompt_Library_v1.0/data/topic_backlog.csv`:
- 349 lines total = 1 header + **348 real records**.
- Real schema: `topic_id, pillar, cluster, working_title, content_type, audience, level, priority, source_tier_required, required_reviewer, visibility, status`.
- Real example titles: "What Sanatana-dharma Means," "The Difference Between Dharma and Religion,"
  "The Self: Ātma and the Body," "Karma and Reincarnation" — all under the pillar "Sanatana-dharma,"
  cluster "Foundations of Sanatana-dharma," with real audience/level/priority/tier/reviewer metadata.
- Original `status` value for these sample rows: `research_backlog` (not `proposed`).

**Finding: the real 348-item researched backlog was not imported.** What exists in the live repo
under the same conceptual "roadmap" name is a 20-item synthetic placeholder set that matches neither
the count nor the content of the actual research. The one honest mitigating factor: the live file
does self-annotate as "metadata only; not published content," and this roadmap file is not surfaced
anywhere in the public UI that this session found (no page renders its contents to end users) — so
there is no public-facing fabrication or misleading claim. But per the mission's Phase 7D instruction
("If the inventory was ignored or only partially imported, record that clearly"): it was effectively
**ignored**, not partially imported — a 20-item synthetic stand-in is not a partial import of a
348-item real inventory, it is a different, smaller, unrelated dataset that happens to live at a
similarly-named path.

## Lifecycle state counts (published content only, since roadmap records don't map to the same lifecycle)

| State | Count |
|---|---:|
| `published` | 6 (all 6 live items) |
| `approved` | 0 observed |
| `review_due` | 0 observed |
| `draft` | 0 observed (would not be visible publicly by design) |
| `review_pending` | 0 observed (would not be visible publicly by design) |
| `archived` | 0 observed |

No draft or review-pending content was found exposed publicly — consistent with the `isPublic()` gate
in `apps/web/lib/knowledge/loader.ts` and with the direct-route security probe
(`/knowledge/daily-practice` → 404) documented in the main report.
