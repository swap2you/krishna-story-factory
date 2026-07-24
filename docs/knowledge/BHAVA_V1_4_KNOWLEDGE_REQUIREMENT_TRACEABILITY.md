# Bhāva V1.4 — Knowledge Requirement Traceability

Package root: `MyPilotDropbox/bhava-knowledge-library-v1.0`

| Requirement | Package source | Implementation | Status |
|-------------|----------------|----------------|--------|
| Nav label Knowledge / title Knowledge Library | Blueprint §1 | `layout.tsx` nav + `/knowledge` metadata | `implemented_not_verified` |
| `/blog` permanent redirect | Blueprint IA | existing blog redirect | `implemented_not_verified` |
| 348-topic roadmap import | `data/topic_backlog.csv` | `content/knowledge/roadmap/records.json` | `implemented_not_verified` |
| Lifecycle states | Master prompt | mapped; public gate approved/published only | `implemented_not_verified` |
| Public screens / pathways | Blueprint mega-menu | `/knowledge/**` routes + pathway pages | `partial` |
| Content types (13) | Master prompt | `lib/knowledge/types.ts` templates + validators | `partial` |
| SQLite FTS + PostgreSQL-ready | Master prompt | `bhava_api/knowledge/search.py` + SQL migration | `implemented_not_verified` |
| Editorial Studio roles/workflow | Master prompt | `/studio/knowledge` bootstrap auth + filters | `partial` |
| Private ask/correction | Blueprint engagement | `/knowledge/ask`, `/corrections` mailto | `implemented_not_verified` |
| Source tiers / confidential gates | Blueprint §4–5 | `governance.py` + standards page | `partial` |
| No fabricated scripture | Master prompt | seed corpus unchanged; roadmap titles only | `implemented_and_verified` |
| Exact private counts | Master prompt | Studio dashboard | `implemented_not_verified` |
| Public excludes non-published | Master prompt | `listRoadmap(false)` + FTS filter | `implemented_not_verified` |

Accepted requirements must not disappear without an explicit deferred/blocked reason in this table.
