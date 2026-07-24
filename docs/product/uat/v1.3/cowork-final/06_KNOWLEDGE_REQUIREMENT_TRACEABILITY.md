# V1.3 Knowledge Library Requirement Traceability

Classification legend: Implemented and live / Implemented but incomplete / Scaffold only / Deferred
with accepted reason / Missing / Contradicted / Not testable.

| Requirement (per `00_EXECUTIVE_DECISIONS.md`) | Classification | Evidence |
|---|---|---|
| Nav label "Knowledge" | Implemented and live | Header nav, all pages, confirmed via `read_page` |
| Page title "Bhāva Knowledge Library" | Implemented and live | `/knowledge` `<title>` and H1, confirmed via `get_page_text` |
| Curated documentation system, not open forum | Implemented and live | No comment system found; Ask/Corrections are private mailto only |
| Public may submit: question, correction, broken-link, private rating | Partially implemented | Ask (`/knowledge/ask`) and Suggest a correction (`/knowledge/corrections`) exist as mailto forms; a distinct "broken-link report" or "private usefulness rating" control was not found as a separate feature — may be folded into the general correction form (not confirmed) |
| Nothing public submissions publish automatically | Implemented and live | Both forms use `mailto:`/clipboard, no server-side public-write path found |
| Mega-menu, 16 named pathways | Implemented and live | All 16 pathway names present exactly as specified, confirmed via `/knowledge`, `/knowledge/topics`, `/knowledge/learning-paths` |
| Mega-menu ≤4 columns, 12–16 primary links | Not testable this session | The live header nav does not render a mega-menu dropdown — pathways are only reachable via the `/knowledge` home page's card grid, not a header flyout. This is a **narrower implementation than specified** (no mega-menu UI element found at all) — classify as **Implemented but incomplete** relative to spec |
| Source authority tiers (A1/A2/B1/B2/C1/D) | Not testable / not found in UI | No visible tier indicator on the one article opened (`what-is-bhava`); its `sources` field uses a simpler `tier: "editorial"` label, not the A1–D scheme. **Missing** from the rendered product, though the concept may exist in the schema |
| Confidential-content restrictions (mantra text, initiation scripts, etc.) | Not testable | No prayer/śloka content is published yet (`/knowledge/prayers`, `/knowledge/slokas` both empty), so there is nothing to check for over-disclosure. The restriction is untested because there's nothing to leak yet — this is a low-risk gap, not a confirmed pass |
| Bhaktamal — later curated collection, not unsupervised translation | Not testable | No Bhaktamal content found anywhere in the live app or in `content/knowledge/` |
| File-first storage: MD/MDX + JSON + YAML front matter + DB index for search/workflow | Implemented but incomplete | Content is file-first (`content/knowledge/{articles,questions,pathways,roadmap}` as JSON meta + `.md` body) — matches the spec's file-first principle. No YAML front matter observed (JSON `meta.json` used instead); no DB index found — search runs by scanning the file tree at request time (`searchKnowledge()` in `loader.ts`), not a database |
| No XML; no proprietary rich-text DB as sole copy | Implemented and live | Confirmed — plain JSON + Markdown |
| UX: calm cream/ivory, deep navy, muted gold accents, no infinite scroll, no popularity counters | Implemented and live | Matches visually across all Knowledge pages viewed; no counters or infinite scroll seen |
| V1 thin slice: home/nav, topic browsing, search, article/FAQ/prayer/śloka templates, source/review components, 20–30 seed resources, private forms, no public editorial studio | Implemented but incomplete | Home/nav/browsing/search: yes. Article template: yes (basic). FAQ/Q&A template: yes (basic). Prayer/śloka templates: page shells exist but zero content populates them. Seed resources: only **6** published items exist (3 articles + 3 questions) — well short of the "20–30 fully reviewed seed resources" V1 target. Private forms: yes. No public editorial studio: confirmed (`/studio/knowledge` is a disclosed non-public stub) |
| 348-resource proposed inventory available as governed roadmap metadata | **Missing / Contradicted** | Real `topic_backlog.csv` (348 records, real titles/pillars/clusters/tiers) was not imported. Live `content/knowledge/roadmap/index.json` contains only 20 generic placeholder records ("Backlog topic N"). See `07_KNOWLEDGE_RESOURCE_STATUS_COUNTS.md` |
| Editorial roles (steward/admin/editor/contributor/reviewers/moderator/auditor) | Not testable | No role-based UI or authentication surface found on the public side; `/studio/knowledge` is a static disclosure page, not a functioning editorial console |
| Workflow: Draft → Source Review → Devotional Review → Copy Review → Approved → Scheduled → Published → Updated → Archived | Scaffold only | The `review_state` field in content schema supports values consistent with parts of this (`draft`/`published`/`approved`/`review_due`/`archived` seen in `loader.ts`'s allow-list), but no visible workflow UI drives transitions between them |
| Server-side authorization for any mutation | Implemented and live (by omission) | No public mutation path was found at all — the safest possible interpretation, since there is nothing to authorize around |

## Summary judgment

The Knowledge Library is a genuine, honestly-labeled **thin slice** exactly matching the spirit of the
V1 release philosophy in the blueprint — but it is thinner than the blueprint's own V1 target (6 seed
resources vs. a 20–30 target), is missing the mega-menu navigation pattern and source-authority-tier
display entirely, and its headline "proposed resource inventory" claim does not reflect the actual
researched backlog. None of this constitutes fabrication or a safety problem — every gap found is a
gap of omission (missing/incomplete), not commission (nothing false is being asserted to the public) —
but it falls short of "package implemented," which is exactly the trap the mission's Phase 7 warns
against accepting at face value.
