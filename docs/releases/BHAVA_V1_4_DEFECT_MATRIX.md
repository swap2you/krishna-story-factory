# Bhāva V1.4 — Defect Matrix

Authoritative inputs: V1.3 CoWork UAT, master prompt, current `feature/bhava-portal-v1` code.

| ID | Finding | Status |
|----|---------|--------|
| DEF-06 | Live CoWork: media element issues no narration request; fetch works | `partial` → fixing in V1.4 audio lab + blob fallback + buffered Next proxy |
| DEF-07 | Keyboard shortcuts leak into modal/carousel | `implemented_not_verified` (code present; re-verify in matrix) |
| LOGO-01 | Header crops approved wide `logo-small-header` to 44×44 icon | `contradicted` → corrected to true-aspect header + mobile icon+text |
| BRAND-01 | Assets imported but not all rendered | `partial` |
| KNOW-01 | 20 placeholder roadmap vs 348 CSV | `missing` → imported 348 governed records |
| KNOW-02 | Studio stub only | `scaffold_only` → bootstrap studio + roadmap filters |
| KNOW-03 | Search is substring only | `partial` → SQLite FTS5 + PostgreSQL DDL |
| KNOW-04 | Content types incomplete | `partial` |
| KNOW-05 | Governance gates missing in runtime | `partial` → API evaluate endpoint |
| NAV-008 | Story 007 linked to unreleased 008 | `contradicted` → end-of-release message |
| TEST-01 | Targeted audio recheck ≠ full matrix | `missing` → full post-fix required |

Classification vocabulary: `implemented_and_verified` | `implemented_not_verified` | `partial` | `scaffold_only` | `missing` | `contradicted` | `deferred_by_explicit_user_decision` | `blocked`
