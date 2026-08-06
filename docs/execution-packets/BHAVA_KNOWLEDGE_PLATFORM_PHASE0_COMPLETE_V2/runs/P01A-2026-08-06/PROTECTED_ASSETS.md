# Protected Assets — P01A

Do not mutate these without separate explicit owner authorization beyond Phase 1A.

## Story Factory & release boundary

| Asset | Protection |
|---|---|
| Accepted story packages / `output/` artifacts | gitignored; never commit |
| `deploy/content/RELEASE_CONTENT.json` (`public_story_max: 22`, tag `bhava-content-001-022-v1`) | release pin; Phase 1 must not alter |
| Public story routes `001…PUBLIC_STORY_MAX` | preserve production max policy |
| Stories 023+ private packages | remain private; not public routes |
| Scheduler tasks (`Krishna Story Factory MWF`, install scripts) | locked disabled unless approved |
| Locked Stories 001–006 editorial content | senior review lock (AGENTS.md) |

## Public / private route allowlists

| Surface | Mechanism |
|---|---|
| `/studio`, `/dev`, factory/scheduler/queue/local APIs | Next `middleware.ts` 404 when public site |
| Same prefixes | Caddy `@private_paths` 404 |
| Roadmap 348 records | public loader requires `approved|published` lifecycle (none today) |
| Private corpus originals | never in public repo; `bhava-library` only |

## Secrets & operator folders

| Path | Rule |
|---|---|
| `.env`, `credentials/` | never commit |
| `MyPilotDropbox/` | gitignored drop inbox; may contain keys |
| API keys / TTS / Drive tokens | paid calls forbidden this phase |

## Brand / identity

| Item | Note |
|---|---|
| Public brand “Bhāva” + four pillars | preserve |
| Footer civil credit tension | see `RISK_REGISTER.md` — reconcile under owner decision before public Knowledge expansion |

## Phase 1 proposed branch (not created)

- Proposed later: `feature/kf-p01-visual-learning-pilot` from `develop`  
- **Not created** in P01A
