# Bhāva Tech Baseline

Recorded during `feature/bhava-portal-v1` bootstrap.

| Tool | Version |
| --- | --- |
| Node.js | 20.11.1 |
| npm | 10.2.4 |
| Python | 3.14.6 |
| Package manager | **npm** workspaces (pnpm/corepack failed on this Node; do not mix managers) |

## Frontend

- Next.js App Router (current stable compatible with Node 20)
- TypeScript `strict`
- React (Next.js bundled)
- Tailwind CSS
- Vitest + Testing Library
- Playwright (+ axe)

## Backend

- FastAPI + Uvicorn
- Pydantic v2
- SQLAlchemy 2
- SQLite at `data/catalog/bhava.sqlite`
- Pytest for API and portal guards

## Local ports

| Service | URL |
| --- | --- |
| Web | http://localhost:3000 |
| API | http://127.0.0.1:8000 |

## Notes

- Prefer npm scripts from repo root (`npm run …`).
- Factory actions remain disabled unless `BHAVA_FACTORY_ACTIONS_ENABLED=true`.
