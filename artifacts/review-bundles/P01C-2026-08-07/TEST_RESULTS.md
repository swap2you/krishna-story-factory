# TEST_RESULTS — P01C

**Environment:** Node v24.19.0 · repository `.venv` Python · Windows  

## Executed

| Suite | Result | Notes |
|---|---|---|
| `tests/test_knowledge_packages_p01c.py` | **PASS** (7) | schema/lifecycle/export Unicode/hash/auth negatives |
| `tests/test_knowledge_v14.py` | **PASS** | knowledge regression |
| `tests/test_private_reader_public_boundary.py` | **PASS** | public boundary |
| `apps/web` vitest (full) | **PASS** (49) | includes packages + footer |
| `npm run build` (web, Node 24) | **PASS** | earlier this run; remediations after build need rebuild before prod image |
| Playwright screenshots (manual) | **PASS** | studio + preview lenses + footer via `next dev` + `BHAVA_PUBLIC_SITE=0` |
| PDF/DOCX Unicode extract | **PASS** | Devanāgarī + IAST + fixture markers; hash parity |
| Forgeable header alone | **PASS** | API 403 without secret |

## Not claimed PASS

| Check | Status |
|---|---|
| Full `scripts/test_all.ps1` | **NOT RE-RUN** after final remediation commit in this session |
| Full Playwright e2e CI matrix / axe CI job | **NOT RUN** as automated suite (manual screenshots only) |
| Production Compose image rebuild | **NOT RUN** (not authorized for staging/prod) |
| Secret scanners (gitleaks/trufflehog full) | **NOT RUN**; manual review found no secrets in fixture/docs |
| Automated axe-core suite | **NOT RUN**; UX specialist review used instead |

Do **not** treat skipped rows as PASS.
