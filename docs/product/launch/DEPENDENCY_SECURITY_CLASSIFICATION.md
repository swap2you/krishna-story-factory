# Dependency security classification — Bhāva Stories Production Launch

**Product SHA:** `122f2300b4d02c91ca99b3f6efa941e1686f2543`  
**Node:** v22.23.1  
**Declared web stack:** Next.js `15.5.22`, React / React DOM `19.1.9`, eslint-config-next `15.5.22`

## Public-hosting gate

| Check | Result |
|---|---|
| Critical production vulnerabilities | **0** |
| High production vulnerabilities after overrides + nested postcss removal | **0** (`npm audit --omit=dev`) |
| Next.js / RSC advisory on installed 15.3.5 | **Cleared** by upgrade to 15.5.22 |
| Dependency downgrade | **None** |
| Unsupported Node engine | **None** (Node 22.23.1 ≥ 20.19.0) |

## Controlled upgrades

- `next` 15.3.5 → **15.5.22**
- `react` / `react-dom` → **19.1.9** (workspace overrides)
- `eslint-config-next` → **15.5.22**
- Root overrides: `postcss@8.5.24`, `sharp@0.35.3`
- `scripts/ensure_native_optionals.cjs` removes nested `next/node_modules/postcss@8.4.31` so runtime resolves the patched hoisted PostCSS

## Development audit

Full `npm audit` may still report toolchain findings outside the production omit set. Those are classified as **dev-only** and do not block the public-hosting gate when `--omit=dev` is clean.

## Notes

- Do not run `npm audit fix --force` (it proposes a breaking Next downgrade).
- `npm ci` on Windows may fail with EPERM while a live Next process holds `@next/swc-*.node`; stop the portal before clean installs.
