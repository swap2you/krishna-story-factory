# bhava.me Deployment Guide (planning only)

This document explains a future public deployment. It does **not** change DNS, SSL, or hosting.

## Intended split

| Host | Role |
| --- | --- |
| `bhava.me` | Public Next.js PWA |
| `www.bhava.me` | Redirect to apex |
| optional `api.bhava.me` | Public read-only catalog API |
| never public | `/api/v1/local/*` Factory Studio |

## IONOS checklist (manual, later)

1. Confirm domain ownership for `bhava.me`.
2. Add HTTPS certificate after hosting target exists.
3. Point DNS A/AAAA or CNAME to the chosen host.
4. Do **not** publish factory credentials or loopback studio routes.
5. Prefer PostgreSQL + object storage adapters when leaving SQLite/filesystem.

## Local acceptance gate

Deploy only after `feature/bhava-portal-v1` is accepted and Stories 001–007 remain unchanged.
