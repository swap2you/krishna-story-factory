# Content Model — Canonical Prayer Record Package

**Status:** PROPOSED for owner freeze at OD-15  
**Reject as SoT:** roadmap JSON alone; legacy `prayer_item`/`shloka` schemas as Phase 1 page model (adapters only)

## Package layout (OD-11 recommend)

```
content/knowledge/packages/<record_id>/
  record.json
  content.json          # ordered blocks
  source_dossier.json
  claims.json
  rights.json
  assets.json
  reviews.json
  manifest.json
```

Private corpus originals never enter this tree.

## record.json (core)

`record_id`, `slug`, `title`, `title_iast`, `content_type` (prayer|arati|mantra_collection|sloka), `pillar`, `cluster`, `pathway`, `source_tier_required`, `lifecycle`, `package_status`, `visibility`, `audience_default`, `min_age`, `max_age`, `purpose_sentence`, `record_version`, `canonical_text_hash`, `unicode_normalization` (`NFC`), `relationships[]`, `roadmap_ref` (optional `TOP-*`)

## Stanza block

`block_id`, `block_type=stanza`, `ord`, `devanagari`, `devanagari_nfc`, `iast`, `translation_en`, `translator`, `edition`, `exact_locator`, `word_meanings[]` (optional + source), `variant_readings[]` (documented only), `pronunciation_notes`, `asset_refs[]`, `lens_explanations` map by `presentation_profile`

## Lenses

Profiles: `little_learner` | `explorer` | `teen` | `study`  
Adapt scaffolding/examples/density only — never mantra, translation, doctrine, quoted speech, or historical fact.

## reviews.json

`review_id`, `role` (editorial|scriptural|sanskrit_source|rights|age_education|specialist|final_owner), `decision`, `reviewer`, `reviewed_at`, `notes`, `record_version` — human only; no agent fabrication.

## rights.json

Separate: quotation, adaptation, translation, download, commercial; attribution; restrictions; scope split for text vs art vs audio.

## assets.json

Per ASSET_POLICY.md fields.

## Export manifest

`record_id`, `record_version`, `template_id/version`, `scripture_hash`, `translation_hash`, `canonical_content_hash`, `asset_hashes[]`, `page_sizes`, `generators`, `generated_at`, `validation`, `artifact_sha256`

## Reviewer gate before any public or shared preview

All required roles PASS for that version; dossier `DOSSIER_READY`; rights not `RIGHTS_BLOCKED`.
