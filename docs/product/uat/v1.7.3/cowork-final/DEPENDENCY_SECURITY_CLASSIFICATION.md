# V1.7.3 CoWork UAT — Dependency Security Classification

Commands executed (read-only; no `npm audit fix`, no dependency modification):

- `npm audit --json` → `npm-audit-full.json` (this folder)
- `npm audit --omit=dev --json` → `npm-audit-prod.json` (this folder)
- `npm ls eslint-visitor-keys` → `npm-ls-eslint-visitor-keys.txt` (this folder)

## Totals

- Full tree: **1 critical + 11 high = 12** (matches the reported "11 high and 1 critical")
- Production tree (`--omit=dev`): **1 critical + 2 high = 3**

## Classification of the 12 findings

### Development/build-only (9 of 12) — NOT reachable in production runtime

`eslint`, `eslint-config-next`, `@eslint/eslintrc`, `@eslint/config-array`, `eslint-plugin-import`, `eslint-plugin-jsx-a11y`, `eslint-plugin-react`, `brace-expansion`, `minimatch` — all belong to the lint toolchain (devDependencies of `apps/web`). The high-severity root causes in this cluster are the `brace-expansion` unbounded-expansion DoS and a `minimatch` issue; the eslint-family entries are flagged transitively through those. None ship in the production build or run on the server at runtime. `npm ls eslint-visitor-keys` confirms all instances (3.4.3 / 4.2.1 / 5.0.1) sit under eslint-family packages only.

### Production-tree (3 of 12) — reachability assessed individually

1. **`next` — CRITICAL, direct production dependency (installed 15.3.5, vulnerable range includes it).** Advisories: (a) Cache Key Confusion for Image Optimization API routes, (b) Content Injection for Image Optimization, (c) SSRF via Improper Middleware Redirect Handling.
   Reachability in this app, verified against source:
   - **No `middleware.ts` exists** (checked `apps/web/` and `apps/web/src/`) → the SSRF-via-middleware advisory has no attack surface here.
   - **No `next/image` usage found in app code** and no `images` config in `next.config.ts` → the two Image-Optimization advisories have no configured remote-image surface; the app serves story imagery via its own local API routes.
   - The deployment is a **local-first portal bound to 127.0.0.1** (not an internet-exposed multi-tenant server), further limiting practical exploitability today.
   - **Conclusion: reachable-in-principle (production dependency, critical), not reachable-in-practice via the advisory paths in the current app shape.** Still the top-priority upgrade: bump `next` to a patched release before any public/hosted deployment. Classified **P2 now / P0 precondition for public hosting**.
2. **`postcss` (high, indirect — bundled at `apps/web/node_modules/next/node_modules/postcss@8.4.31`, prod per lockfile).** PostCSS advisories are build-time (stringify output XSS, source-map path traversal at build). PostCSS executes during `next build`, not at runtime request-handling. **Build-time only in practice; resolved automatically by the `next` upgrade.**
3. **`sharp` (high, indirect, optional, 0.34.5 < 0.35.0).** Inherited libvips CVEs affect processing of attacker-controlled images. This app does not accept user image uploads and does not use Next image optimization on remote images; sharp would only touch local, self-produced assets. **Not reachable via attacker-controlled input in the current app shape**; upgrade alongside `next`.

## Bottom line

The headline "1 critical + 11 high" decomposes into: 9 dev-only lint-toolchain findings (no production exposure), 2 prod-tree findings that are build-time or not-attacker-reachable in this app's shape (`postcss`, `sharp`), and 1 genuine production dependency critical (`next`) whose specific advisory paths (middleware SSRF, image-optimization) are **not exposed by this app today** (no middleware file, no next/image usage, localhost binding) but which **must be upgraded before any public hosting**. No `npm audit fix` was run; dependencies unmodified.
