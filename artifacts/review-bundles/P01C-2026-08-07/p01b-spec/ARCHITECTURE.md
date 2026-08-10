# Architecture — Phase 1 Private Preview Pilot

**Stack (locked):** Next.js App Router + FastAPI + SQLite FTS. No framework migration.  
**Base SHA for future branch:** `develop` @ `27c3f35a72a0ffbea864361bab597cc627eaeb0f` (re-verify at G3).  
**Proposed branch (do not create in P01B):** `feature/kf-p01-visual-learning-pilot`

## System view

```text
[Canonical packages under content/knowledge/packages/]
        │
        ├─► Web loader adapters ─► /studio/knowledge/preview/[slug] (loopback)
        ├─► Studio roadmap UI (348 + pagination)
        ├─► Export service (reportlab PDF; DOCX after OD-02)
        └─► Derived FTS (optional OD-12) / publication gates
[Public /knowledge/**] ── only published articles/questions; prayer stubs stay empty
[Private corpus bhava-library] ── never served publicly; checksumed export only
```

## Key decisions

| Topic | Decision | ADR |
|---|---|---|
| Schema | One package schema + generated adapters | ADR-001 |
| Routes | Preview under `/studio/...`; public Knowledge unchanged for pilot | ADR-002 |
| Auth | Loopback + Studio session; deprecate forgeable header alone | ADR-003 |
| SEO | noindex/nofollow/noarchive; never sitemap preview | ADR-004 |
| Lens state | URL query + optional sessionStorage; no accounts | ADR-005 |
| Export | reportlab primary; python-docx recommended; Study-neutral hashes | ADR-006 |
| Migrate | Additive packages; FTS rebuild; git revert | ADR-007 |

## Private-preview controls (D06)

1. Routes under existing middleware/Caddy private prefixes.  
2. `BHAVA_PUBLIC_SITE=1` ⇒ 404 private prefixes.  
3. API private search requires loopback + valid session (not `X-Bhava-Studio: 1` alone).  
4. Bootstrap token env-required for any non-local; cookies HttpOnly/SameSite; Secure on TLS.  
5. Shared preview = separate owner authorization + real auth.

## Studio P1-F08

Replace 200-row cap with pagination over full filtered 348; counts always global to filter.

## Rejected

Framework migration; public pilot routes; four age content trees; bulk 348 promotion; Postgres cutover; paid PDF APIs; Story Factory changes; live Canva/Figma SoT; child accounts.

## Cost / provider policy

Paid providers **off**. Local reportlab / pypdf / pdfjs / future pinned python-docx only after OD-02.
