# Bhāva Runtime Support Policy

## Principles

1. Prefer **latest supported LTS / stable** over newest Current.
2. Application, CI, container, and docs versions must match.
3. Do not upgrade solely because a higher number exists.
4. Every upgrade requires compatibility proof: unit/CI, container build, staging smoke.
5. Production changes only after staging PASS.
6. Paid providers and the story scheduler are out of band from runtime upgrades.

## Supported runtimes

| Runtime | Supported line | Notes |
| --- | --- | --- |
| Node.js | **24 LTS** | Engines `>=24 <25`; `.nvmrc` / `.node-version` / Docker / `setup-node` |
| Python (API + CI) | **3.14** | Docker `python:3.14-slim-bookworm`; hashed production lock |
| Python (factory local) | 3.12–3.14 | Recreate venv on upgrade; never mutate in place |
| SQLite | Bundled with Python | No separately managed SQLite unless a proven need appears |
| Caddy | `2.10-alpine` tag | Bump only with staging TLS proof |
| Ubuntu VPS | 24.04 LTS | |

## GitHub Actions

- Use current stable majors that run on **Node 24 action runtime**.
- Prefer official `actions/*` major tags with readable comments when pinning SHAs for third parties.
- No self-hosted runners in current topology; if added, require runner ≥ versions needed for Node 24 actions.

## Promotion path

```
feature/* → develop → staging → main → production
```

Never develop directly on `main`. Never publish Story 010 via runtime bumps alone — content tag + `BHAVA_PUBLIC_STORY_MAX` + Caddy allowlist must change together in a dedicated release.
