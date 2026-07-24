# Claude Adversarial Review — Bhāva Portal V1.5

**Tested SHA:** `fe57b46`

## Attack angles checked

1. Incomplete package exposure → blocked by exact-eight + publish gates + staging.
2. Duplicate paid narration → recovery reuses hashes; explicit `--enable-production-recovery`.
3. CSRF / factory actions → factory actions default off; CSRF on state-changing routes.
4. Identity leakage → Playwright identity-leak suite green on public routes.
5. Knowledge private roadmap → studio header required for private search; public lifecycle gated.
6. Font license → Tillana as brand display; no unofficial Samarkan download.

## Residual non-blocking

- Education destinations (Teachers / Sunday School / Preachers / Vāṇī) remain “coming soon” for curated content — pages are structural/ready, not content-complete.
- Lighthouse CI not automated; axe critical/serious covered in Playwright accessibility project.

## Verdict

**No open release-blocking adversarial findings** on tested SHA.
