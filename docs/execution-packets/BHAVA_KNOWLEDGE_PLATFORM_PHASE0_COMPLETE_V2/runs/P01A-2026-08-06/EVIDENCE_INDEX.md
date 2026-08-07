# Evidence Index — P01A

| Evidence ID | Requirement(s) | Type | Command/method | Result | Artifact/path | SHA-256 | Date/reviewer |
|---|---|---|---|---|---|---|---|
| E-INTAKE-01 | G0 | Repository | Get-FileHash SHA256; zip safety audit; extract; CHECKSUMS verify | PASS ok=38 | `INTAKE_REPORT.md` | — | 2026-08-06 / orchestrator |
| E-BASE-01 | G1 | Repository | git status/branch/log/rev-list; gh pr list | PASS discovery | `BASELINE_REPORT.md` | — | 2026-08-06 |
| E-REL-01 | boundary | Repository | read `deploy/content/RELEASE_CONTENT.json` | tag 001-022-v1 max 22 | `PROTECTED_ASSETS.md` | — | 2026-08-06 |
| E-RM-01 | P1-F08/F09 | Content | python Counter on `records.json` | 348/source_research | `ROADMAP_VISIBILITY_REPORT.md` | — | 2026-08-06 |
| E-ROUTE-01 | IA | Repository | specialist read-only inventory | map complete | `ROUTE_COMPONENT_DATA_MAP.md` | — | 2026-08-06 / routes agent |
| E-UX-01 | P1-U* | Repository | specialist UX inventory | gaps logged | `SOURCE_AND_REUSE_INVENTORY.md` | — | 2026-08-06 / UX agent |
| E-SRC-01 | source gov | Content | specialist + bhava-library scan | 0 prayer bodies; 0/12 PDFs | `SOURCE_AVAILABILITY.md` | — | 2026-08-06 / source agent |
| E-EXP-01 | P1-F07/E* | Repository | specialist export/deps scan | no DOCX; reportlab exists | `EXPORT_SPIKE_OPTIONS.md` | — | 2026-08-06 / export agent |
| E-SEC-01 | P1-F09 | Security | specialist auth/middleware/Caddy review | header auth risk | `RISK_REGISTER.md` R03–R06 | — | 2026-08-06 / security agent |
| E-PKG-01 | G0 | Rights | package archive hash | `3955E964…C56DC` | `phase-state.yaml` | `3955E964FEE420436842E7C93C22D33BDEEA808B31A961057CCCEF24346C56DC` | 2026-08-06 |

## Environment

- OS: Windows 10 (build 26200)  
- Node observed: v22.23.1 (pin 24)  
- Python: 3.14.6  
- Browser tests: **not executed** (discovery only; no app mutation)  
- Repository branch/SHA: `develop` / `d6159e9af6b7033d1876141eae31944ec93fffc0`

## Limitations

| Skipped | Why | Severity | Compensating control |
|---|---|---|---|
| Live production HTTP re-probe | Discovery local; no deploy access requested | P2 | Use prior Phase 0 notes + code/Caddy review |
| Full `bhava-publishing-studio` re-baseline | Non-blocking for prayer pilot discovery | P3 | Schemas path noted; reverify at intake to that repo |
| Export spike execution | No dependency installs/paid calls | expected | Options documented for P01B/C |
| Independent QA of implementation | No implementation | n/a | Due in P01C |
| Human Sanskrit/rights review | No source text yet | P0 for build | Owner D03 |

Never hide skipped checks: P01A does not claim P01C acceptance criteria PASS.
