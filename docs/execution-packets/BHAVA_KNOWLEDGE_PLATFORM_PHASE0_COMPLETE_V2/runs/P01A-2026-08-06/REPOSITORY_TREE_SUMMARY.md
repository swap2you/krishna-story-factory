# Repository Tree Summary — P01A

**Root:** `C:/Development/Workspace/DevotionalRepo/krishna-story-factory`  
**Label:** **VERIFIED** top-level inventory (2026-08-06)

```text
apps/                 # web (Next.js) + api (FastAPI)
assets/
config/
content/              # knowledge articles, questions, pathways, roadmap
deploy/               # ionos Caddy/compose + RELEASE_CONTENT
docs/                 # includes execution-packets/ (this package + runs)
input/                # CSV plans (source of truth for factory)
krishna_story_factory/# Python factory package
packages/             # ui, contracts
prompts/
scripts/              # test_all, run_prod/test, schedulers
tests/
tracking/             # queue_state CSV
.github/workflows/    # CI + deploy/rollback
MyPilotDropbox/       # gitignored operator inbox (archive source)
output/               # gitignored generated packages
credentials/          # gitignored
node_modules/         # present locally
.venv/                # present locally
```

## Knowledge content tree (complete)

```text
content/knowledge/
  index.json
  articles/{what-is-bhava,source-and-permissions,printing-and-classroom-use}/
  questions/{what-is-bhava-faq,is-bhava-official-bbt,does-bhava-collect-child-data}/
  pathways/index.json
  roadmap/{index.json,records.json}   # 348 records
```

## Phase packet tree (extracted)

```text
docs/execution-packets/BHAVA_KNOWLEDGE_PLATFORM_PHASE0_COMPLETE_V2/
  00_START_HERE.md … 11_CURRENT_STATE_BASELINE.md
  controls/phase-manifest.yaml
  prompt-library/
  templates/
  runs/P01A-2026-08-06/   # this discovery run
```
