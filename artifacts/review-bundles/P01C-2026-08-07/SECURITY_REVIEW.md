# SECURITY_REVIEW — P01C (PR #70 remediation)

## Changes since first draft

- Vendored SIL-OFL Noto Sans + Noto Sans Devanagari with `CHECKSUMS.sha256`; export fails closed on missing/mismatch
- Loopback Host parsing supports `localhost`, `127.x`, `::1`, `[::1]:port`, IPv4-mapped IPv6; positive/negative unit tests
- Signed studio session cookies retain expiry; forgeable `X-Bhava-Studio: 1` alone still rejected
- Studio capability copy no longer overclaims mutations/workflows
- Review ZIP removed from Git history on the feature branch (local-only handoff artifact)

## Residual risks

| ID | Risk | Status |
|---|---|---|
| R-SEC-01 | Public bind + Host forgery | Mitigate by binding studio to `127.0.0.1` + `BHAVA_PUBLIC_SITE=0` |
| R-SEC-02 | Default local bootstrap token outside production | Documented; production requires env |
| R-SEC-03 | Unauthenticated `/gates/evaluate` and `/postgres-ddl` | Pre-existing; not expanded |
| R-SEC-04 | Docker image build not validated on this workstation | Rely on Production CI after push |

## Secrets

No secrets in remediations. Fonts/OFL are public SIL-licensed files. Manual review of fixture JSON: no private paths.
