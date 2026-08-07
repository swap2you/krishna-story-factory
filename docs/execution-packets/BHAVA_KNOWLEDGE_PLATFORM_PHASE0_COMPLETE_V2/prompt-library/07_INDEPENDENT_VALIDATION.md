---
id: PL-07
version: 1.0.0
phase: P01C
purpose: Produce independent findings before any remediation
---

# Independent validation

Freeze implementation edits while reviewers complete findings. The implementer cannot approve its own output.

Run and evidence:

- schema/migration/adapter parity and fixtures;
- unit/integration/route/API/search/sitemap/private-boundary/security/regression tests;
- Chromium, Firefox, WebKit plus representative mobile widths; console/network failures;
- keyboard, focus, screen reader sampling, contrast, headings/landmarks, 200%/400% zoom, reduced motion;
- Devanāgarī/IAST shaping, copy/search/print/export character accuracy;
- Letter/A4 PDF render/structure/text/links/images; DOCX open/render/styles/alt/accessibility checker;
- canonical hash parity across lenses and exports;
- source dossier/claim/translation/rights/reviewer/asset provenance;
- visual/iconographic/devotional quality and age suitability;
- performance on representative pages;
- zero Story Factory/public release/private corpus regression.

Output findings with severity, requirement ID, evidence, root-cause hypothesis, affected paths, and retest. Do not edit implementation files. Produce one combined `VALIDATION_FINDINGS.md` and all required reports/evidence.

