# Source Availability — P01A

**Rule:** Do not invent text or select a record with inadequate source/rights merely to fill a pilot slot.

## Public Knowledge prayer/śloka bodies

| Surface | Count | Label |
|---|---|---|
| Published prayer/śloka content under `content/knowledge/` | **0** | **VERIFIED** |
| `/knowledge/prayers`, `/knowledge/slokas` | empty stubs | **VERIFIED** |
| Story companion Sanskrit in `reviewed_shlokas.py` | intentionally null | **VERIFIED** — not usable as golden text |

## Roadmap metadata candidates (titles only)

All: `lifecycle=source_research`, `package_status=research_backlog`.  
**Adequacy for publication: INADEQUATE in-repo** (no Devanāgarī/IAST/translation/dossier/rights package).

| Pilot slot | Candidate IDs / titles | Decision now |
|---|---|---|
| Golden — multi-stanza Nṛsiṁha | `TOP-0147` Sri Nrsimha Pranama and Prayers; `TOP-0148` Nrsimha Arati | **SOURCE_BLOCKED** pending corpus/edition |
| Praṇāma collection | `TOP-0141` Srila Prabhupada Pranati; `TOP-0142` Guru-pranama; `TOP-0158` Vaisnava Pranama | **SOURCE_BLOCKED** |
| Prasāda prayer | `TOP-0153` Prasada Prayers | **SOURCE_BLOCKED** |
| Single verse + word meanings | `TOP-0167`–`TOP-0184` cluster (guides/collections; no verse bodies) | **SOURCE_BLOCKED** |
| Context-rich prayer | e.g. `TOP-0152` Damodarastakam; `TOP-0156` Sri Siksastakam; `TOP-0144` Mangalacarana | **SOURCE_BLOCKED** |

Stub dossiers: `dossiers/CANDIDATE_*.md` (all `SOURCE_BLOCKED`).

## `bhava-library` local corpus (VERIFIED presence, UNKNOWN rights for temple prayer editions)

| Finding | Detail |
|---|---|
| Export contract | `data/exports/bhava-candidates/` — 553 metadata + 553 briefs, `binary_files: 0` |
| Catalog scale | ~2470 resources; ~1922 on-disk PDFs scanned |
| Nṛsiṁha hits | curriculum/drama/coloring packs — **not** established temple prayer-book editions |
| Prema dhvani / mahamantra PDFs | exist as education materials — rights/edition **UNKNOWN** |
| Standard prayer packages matching roadmap titles | **not found** as verified editions this run |

## Twelve failed Phase 0 attachments (Etiquette / Deity Worship)

Listed in package `04_CONTENT_SOURCE_AND_EDITORIAL_GOVERNANCE.md`.

**VERIFIED:** **0/12** present in `bhava-library` under exact or fragment filename matches.

These block the Etiquette/Deity Worship vertical’s source-adequacy review; they do **not** by themselves block a prayer pilot **if** authorized prayer editions are supplied separately. They remain an owner action item.

## Provenance gap

Import CSV path recorded in roadmap provenance (`MyPilotDropbox\bhava-knowledge-library-v1.0\...\topic_backlog.csv`) is **not present** under current `MyPilotDropbox/`.

## Recommended golden-page path (PROPOSED)

1. Owner designates an authorized edition (private corpus ID or official BBT/ISKCON/Ministry locator) for one multi-stanza Nṛsiṁha prayer.  
2. Complete dossier → Sanskrit/source + rights reviews → only then freeze golden title.  
3. Select four confirmation pages from the same authorized source family when dossiers pass.  

Until then: **no golden-page text is approved**; Phase 1B may specify UI/export against a placeholder schema but must not fabricate scripture.
