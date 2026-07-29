# Knowledge Library — Repository Discovery (V1.3)

**Package:** `MyPilotDropbox/bhava-knowledge-library-v1.0`  
**App boundary:** `knowledge_library`  
**Public root:** `/knowledge` (nav label: Knowledge)

## Existing overlaps

| Area | Before V1.3 | V1.3 approach |
| --- | --- | --- |
| `/blog` | Planned taxonomy page | Permanent redirect → `/knowledge` |
| FAQ | Standalone `/faq` | Remains; seeded Q&A also in Knowledge |
| Prayers | `/library/prayers-mantras` | Linked; Knowledge prayers shell empty until reviewed |
| Vāṇī / Teachers / Preachers | Existing workspaces | Linked from pathways; no content duplication |
| Factory Studio | Loopback `/studio` | Knowledge editorial stub at `/studio/knowledge` |

## Stack

- Next.js App Router SSR over `content/knowledge/**`
- No proprietary CMS lock-in
- Mailto/copy for private ask/correction
- SQLite/PG FTS interface deferred; local search is in-memory over published JSON/MD
