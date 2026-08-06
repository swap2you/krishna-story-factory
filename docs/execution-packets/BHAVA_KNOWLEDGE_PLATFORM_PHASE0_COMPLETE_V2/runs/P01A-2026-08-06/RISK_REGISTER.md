# Risk Register — P01A

| ID | Severity | Area | Finding | Label | Mitigation / owner ask |
|---|---|---|---|---|---|
| R01 | P0 | Source | No reviewed prayer/śloka bodies for pilot slots | VERIFIED | Supply authorized editions + dossiers before build |
| R02 | P0 | Source | 12 Etiquette/Deity Worship PDFs missing from corpus | VERIFIED | Re-upload or confirm equivalents before that vertical |
| R03 | P1 | Security | Knowledge private search auth = forgeable `X-Bhava-Studio: 1` | VERIFIED | Stronger auth before private preview beyond loopback |
| R04 | P1 | Security | Studio bootstrap token default `bhava-local-studio`; `secure: false` | VERIFIED | Env-required secret + secure cookies for any shared preview |
| R05 | P1 | Privacy | Roadmap provenance embeds `MyPilotDropbox\…` in tracked JSON | VERIFIED | Redact/normalize provenance in a later approved change |
| R06 | P1 | SEO | Knowledge article pages indexable; private preview needs explicit noindex/robots | VERIFIED | Spec private-preview metadata in P01B |
| R07 | P2 | Identity | Footer shows civil name `Swapnil Patil`; Phase 0 notes policy tension | VERIFIED/REPORTED | Owner identity decision before public Knowledge expansion |
| R08 | P2 | Config | `public_story_max` 22 vs defaults 20 vs AGENTS 020 | VERIFIED | Align docs/defaults with RELEASE_CONTENT (out of P01A mutate scope) |
| R09 | P2 | Runtime | Local Node 22 vs pin 24 | VERIFIED | Use Node 24 before web build CI parity |
| R10 | P2 | UX | Devanāgarī font named but not loaded | VERIFIED | License + load font in P01C after owner visual direction |
| R11 | P2 | Schema | Fragmented lifecycle/content_type vocabularies | VERIFIED | Consolidation ADR in P01B |
| R12 | P2 | Studio | Roadmap table shows first 200 of 348 | VERIFIED | Pagination for P1-F08 |
| R13 | P2 | Export | No DOCX dependency; PDF/UA unproven | VERIFIED | Export spikes post-approval |
| R14 | P3 | API | `postgres-ddl` endpoint info disclosure | VERIFIED | Consider deny on public edge in later hardening |
| R15 | P3 | Hygiene | Local `main` 21 commits behind `origin/main` | VERIFIED | Fast-forward local main when convenient |

No discovery hard-stop that prevents completing P01A evidence. **R01** is a hard-stop for P01C implementation of real prayer text.
