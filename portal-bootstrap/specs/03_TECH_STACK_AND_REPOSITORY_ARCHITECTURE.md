# Technical Stack and Repository Architecture

## Chosen stack

### Frontend
- Next.js App Router
- TypeScript
- React Server Components where useful
- Tailwind CSS
- Accessible headless component primitives
- CSS variables for the Bhāva design system
- Progressive Web App support
- Markdown rendering with strict sanitization
- PDF.js or native-object fallback
- HTML5 audio with a custom waveform layer
- Device-local bookmarks, notes, playlist and progress

### Backend
- FastAPI
- Python 3.12-compatible codebase
- Pydantic v2 contracts
- SQLAlchemy 2 + Alembic
- SQLite locally
- PostgreSQL-ready repository interfaces
- Read-only filesystem/Drive catalog adapters
- Loopback-only factory-control endpoints

### Testing
- Pytest for Python
- Vitest / React Testing Library
- Playwright for browser and API end-to-end tests
- axe accessibility checks
- visual screenshot regression
- contract tests for the existing eight-file package

## Monorepo target

```text
apps/
  web/                  Next.js public/teacher/local UI
  api/                  FastAPI catalog and local factory gateway

packages/
  ui/                   Bhāva design system
  contracts/            JSON Schema and generated types
  content/              markdown/source rendering helpers

data/
  catalog/              SQLite and local index state

docs/
  product/
  architecture/
  operations/

portal-bootstrap/       imported planning package; removable after handoff
```

## Locked boundaries

The following existing logic is not rewritten:

```text
krishna_story_factory/
scripts/
tracking/
output/
input/
credentials/
```

The API invokes approved existing commands through explicit adapters. It must never expose arbitrary shell execution.

## Deployment strategy

### Local
- web on `localhost:3000`
- API on `127.0.0.1:8000`
- private factory routes available only on loopback
- SQLite catalog
- local filesystem and Google Drive adapters

### Public later
- `bhava.me` for the public PWA
- no public factory endpoints
- PostgreSQL
- object storage/CDN
- HTTPS
- DNS configured only after local acceptance
