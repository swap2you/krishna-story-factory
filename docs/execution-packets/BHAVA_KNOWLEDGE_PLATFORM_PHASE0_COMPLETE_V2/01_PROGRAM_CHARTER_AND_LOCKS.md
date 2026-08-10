# Program Charter and Locked Decisions

## Mission

Build Bhāva into a governed devotional-learning platform for ages 5–22, families, teachers, preachers, and serious students while preserving fidelity to Śrīla Prabhupāda's teachings and the approved source record.

## Key assumptions

1. The current repository remains Next.js/TypeScript + FastAPI + SQLite unless discovery proves otherwise; this program does not force a framework migration.
2. The 348 roadmap entries are planning metadata in `source_research`, not completed documents.
3. The private `bhava-library` corpus exists, but only a read-only, provenance-aware export may feed public authoring.
4. Current implementation begins with visual pages and export; audio/podcasts are later phases.
5. Owner approval is required at every implementation, merge, staging, production, and scheduler-enable gate.

## Why the 348 records are invisible

`records.json` is a private roadmap/catalogue. The records have not passed the publication lifecycle. Public search and routes correctly exclude research, draft, rejected, and restricted records.

The fix is a visible private Studio workbench with counts and states:

`roadmap → dossier → draft → reviews → approved → release candidate → published`

Exposing raw roadmap JSON publicly would bypass governance and create misleading empty pages.

## Repository boundaries

| Repository | Owns | Must not own |
|---|---|---|
| `krishna-story-factory` | Public platform, governed Knowledge/Learning records, private Studio, approved delivery | Private corpus originals, commercial publishing internals |
| `bhava-library` | Acquisition, immutable originals, metadata, taxonomy, evidence, source dossiers | Public routing/public APIs for originals |
| `bhava-publishing-studio` | Original/commercial publication packaging | Public platform runtime or private Ministry archive |
| 3D workstream | Experiments only | Current site dependencies or public navigation |

## Program locks

- Preserve Story Factory policy, accepted packages, existing scheduler, releases, and public/private boundary.
- Keep the four public pillars; formats are facets/assets, not new top-level tabs.
- No open forum, child accounts, public comments, or automatic publishing.
- Do not expose legal/civil identity where public brand policy prohibits it.
- Never fabricate Sanskrit, translation, quotation, source locator, permission, reviewer, or approval.
- Never copy arbitrary third-party source PDFs into the public repo.
- Never download a missing source merely because it is findable. Use the local corpus first, then official/authorized sources with recorded provenance and rights.
- Approved records and exported artifacts are immutable; corrections create a new version.
- No agent may self-certify independent review of its own work.

## Product principles

- One canonical truth; multiple age-appropriate explanations.
- Simple before clever: server-rendered content and small interactive islands.
- Motion supports comprehension; it never competes with prayer or text.
- Beautiful does not mean busy. Devotional, serene, premium, warm, and readable wins.
- Every visible claim has source lineage; every asset has rights/provenance.
- Blocked work is shown honestly in Studio rather than silently skipped.

## Decisions that require versioned change control

- pillar/navigation model;
- canonical record schema;
- age-presentation profiles;
- required review roles and publication gates;
- source-tier and rights policy;
- approved visual system;
- public/private route rules;
- scheduler authority boundaries.

Changes require an ADR/decision record, impact analysis, migration plan, tests, and owner approval.

