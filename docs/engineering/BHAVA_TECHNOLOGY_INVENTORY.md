# Bhāva Technology Inventory

**Branch baseline:** `chore/platform-modernization-and-release-automation` from `origin/develop` @ `ab37275`  
**Production baseline (unchanged by this doc):** SHA `19af3c458e47c86b0fcf932fb10e5d2fb34c3bea`, content `bhava-content-001-009-v1`  
**Inventory date:** 2026-07-31

## Summary table

| Component | Location | Pinned / declared | Executed (operator laptop) | Latest stable / LTS | Support | Security | Target | Decision | Justification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Node.js (app) | `.nvmrc`, Docker `Dockerfile.web`, CI `NODE_VERSION` | **24** (Active LTS) | 22.23.1 local | 24.18.1 LTS | Active LTS | Prefer LTS security releases | **24** | **Upgrade required** | Align engines/CI/Docker; reject Node 26 Current |
| npm | with Node | 10.x (Node 22 local) | 10.9.8 | ships with Node 24 | Active | — | Node 24 bundled npm | Follow Node | Do not chase npm major alone |
| Next.js | `apps/web/package.json` | 15.5.22 | lock 15.5.22 | 15.5.x | Active | Monitor advisories | keep 15.5.22 | **Defer** | No forced bump without app regression budget |
| React | root + web | 19.1.9 | lock | 19.x | Active | — | keep | **Defer** | Stable for portal |
| TypeScript | web | ^5.8.3 → lock 5.9.3 | 5.9.3 | 5.x | Active | — | keep | **Defer** | |
| Playwright | web | ^1.54 → lock 1.61.1 | 1.61.1 | current 1.x | Active | browsers via install | keep | **Optional** | Upgrade browsers in CI via `npx playwright install` |
| Vitest / ESLint | web | vitest 3.2.7 / eslint 9.39.5 | lock | current | Active | — | keep | **Defer** | |
| Python (API) | Docker, CI, `.python-version` | **3.14** | 3.14.6 | 3.14.6 | Active | Prefer current stable | **3.14** | **Upgrade required** | Production lock + factory deps install on 3.14.6 |
| Python (factory) | `requirements.txt` ranges | >=3.12 | 3.14.6 proven install | 3.14 | Active | — | 3.14 | **Upgrade** | Recreate venvs; do not mutate in place |
| pip / setuptools / wheel | builder image | latest at build | pip 26.2, setuptools 83, wheel 0.47 | current | Active | — | upgrade at image build | **Optional** | |
| FastAPI | `requirements.production.lock` | 0.141.1 | 0.141.1 | 0.141.1 | Active | — | keep | **Defer** | Already current at inventory |
| Uvicorn | lock | 0.52.0 | 0.52.0 | 0.52.x | Active | — | keep | **Defer** | |
| Pydantic | lock | 2.13.4 | 2.13.4 | 2.13.x | Active; v1 EOL on 3.14 | — | keep v2 | **Required constraint** | No pydantic.v1 |
| SQLAlchemy | lock | 2.0.51 | 2.0.51 | 2.0.x | Active | — | keep | **Defer** | |
| SQLite | Python stdlib | host/container | **3.50.4** (Win 3.14.6) | bundled | — | — | bundled | **Defer** | No separate SQLite package required |
| Caddy | compose | `caddy:2.10-alpine` | VPS image tag | 2.10.x | Active | — | keep tag | **Defer** | Upgrade only with staging proof |
| Ubuntu (VPS) | bootstrap | 24.04 | 24.04 | 24.04 LTS | Active | — | keep | **Defer** | |
| Docker Engine | VPS / CI | apt / GH runner | Desktop offline locally; Compose **v5.1.4** | current | Active | — | keep | **Defer** | |
| OpenSSL | VPS / images | distro | OpenSSL 3.x | 3.x | Active | — | keep | **Defer** | |
| GitHub Actions checkout | workflows | **@v6** | — | v6/v7 | Node 24 runtime | Clears Node 20 deprecation | **v6** | **Upgrade required** | Was @v4 (Node 20 warning) |
| setup-node | workflows | **@v6** | — | v6/v7 | Node 24 | — | **v6** | **Upgrade required** | |
| setup-python | workflows | **@v6** | — | v6 | Node 24 | — | **v6** | **Upgrade required** | @v5 still Node 20 |
| upload-artifact | ci.yml | **@v6** | — | v6 | Node 24 default | merge-same-name behavior | **v6** | **Upgrade required** | Unique artifact names already |
| OpenAI SDK | factory req | openai>=2 → resolved 2.52.0 in trial venv | — | 2.x | Active | keys never in git | keep range | **Defer pin chase** | Paid calls forbidden in this release |
| ElevenLabs | HTTP via requests | no SDK pin | — | n/a | — | — | keep | **Defer** | |
| Media/PDF | Pillow, reportlab, pypdf, mutagen, miniaudio | ranges in requirements.txt | installed on 3.14 | current | — | — | keep | **Defer** | Proven install on 3.14.6 |

## GitHub Actions `uses:` (post-modernization)

All first-party `actions/*` moved off Node 20 action runtimes. No third-party marketplace actions requiring commit SHA pins. Local composites:

- `.github/actions/provision-content`
- `.github/actions/configure-pinned-ssh`
- `.github/actions/smoke-with-tls`

## Rejected / deferred upgrades

| Candidate | Decision | Reason |
| --- | --- | --- |
| Node 26 Current | Rejected | Not LTS; policy prefers LTS maintenance |
| Caddy floating `:latest` | Rejected | Pin major.minor alpine tag |
| Blind `npm audit fix --force` | Rejected | Breaking changes without review |
| Separate managed SQLite | Deferred | App uses Python sqlite3; 3.50.4 sufficient |
| Next.js major | Deferred | No product requirement in this release |

## Compatibility proof (this release)

- API hashed lock installs on Python 3.14.6
- `tests/test_public_production_boundary.py` PASS on 3.14.6
- Factory `requirements.txt` installs on 3.14.6
- Node 24 proven in CI/Docker (`node:24-bookworm-slim`); local laptop may remain on 22 until operator upgrades NVM
