# SECURITY_REVIEW — P01C

## Specialist reviewers (read-only)

1. UX/accessibility — findings remediated (radiogroup focus steal, heading hierarchy, source details, print/reduced-motion polish)
2. Architecture/security — findings partially remediated (see residual)
3. Export/content-governance — PDF Unicode font + test no-op fixed; python-docx pinned; export gates added

## Remediations applied

- Signed studio session cookies with HMAC + expiry (`role.nonce.exp.sig`)
- Forgeable `X-Bhava-Studio: 1` alone rejected on private Knowledge API
- Loopback Host gate; forwarded headers accepted only if every hop is loopback
- Export rejects `visibility=public`; stderr not echoed; tempdir cleaned
- Non-fixture `SOURCE_BLOCKED` bodies suppressed in UI; export `assert_export_allowed`
- Dual-font PDF (Noto Latin + Nirmala Devanāgarī); fail closed if fonts missing
- `python-docx==1.2.0`

## Residual risks (documented, not claimed fixed)

| ID | Risk | Mitigation / limit |
|---|---|---|
| R-SEC-01 | Host header alone is forgeable if Next binds `0.0.0.0` | Bind studio to `127.0.0.1`; set `BHAVA_PUBLIC_SITE=0`; require bootstrap token in production |
| R-SEC-02 | Default local bootstrap token when env unset (non-production) | Production throws if unset; local default documented |
| R-SEC-03 | `/gates/evaluate` and `/postgres-ddl` remain unauthenticated API surfaces | Pre-existing; lock down in later packet |
| R-SEC-04 | PDF/UA not claimed | Explicit false in manifests |

## Secrets scan (manual)

No API keys, `.env`, or private corpus binaries in the feature commits or review bundle.
