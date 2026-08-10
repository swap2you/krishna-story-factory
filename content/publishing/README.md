# Publishing Studio handoff (private scaffold)

Private packaging lane for **Bhāva-original** works only (lesson packs, family sheets, teacher guides, and future print/EPUB outputs that Bhāva authors).

This directory is a **handoff scaffold**, not a commercial authoring dump and not a place for private source PDFs, OCR corpora, secrets, or third-party book bodies.

## Rules

1. Package only works with `rights_status: bhava_original` (or an explicit permitted adaptation recorded in provenance).
2. Never commit owner PDF originals, full copyrighted scripture bodies, API keys, or commercial authoring internals.
3. Public site must not advertise downloads until `export_manifest.downloadable` is true and artifacts are validated.
4. Studio / handoff remains private; do not link this tree from public navigation.
5. Identity metadata below applies only when publication metadata is truly required for a Bhāva-original work.

## Layout

```
content/publishing/
  README.md                          ← this file
  identity_metadata.template.json    ← author/publisher identity template
  packages/                          ← one folder per handoff package (gitkept empty until real packages)
```

## Package folder convention (when a real handoff exists)

```
packages/<package-id>/
  manifest.json          ← export version, formats, canonical lineage, review state
  identity.json          ← filled from identity_metadata.template.json
  assets/                ← cover/provenance notes only as needed (no secret dumps)
  exports/               ← validated PDF/EPUB/print outputs when ready
```

## Related contracts

- Learning derivatives: `packages/contracts/schemas/learning_derivative.schema.json`
- Content policy: `docs/unified-platform-v2/specs/04_SOURCE_AND_CONTENT_POLICY.md`
