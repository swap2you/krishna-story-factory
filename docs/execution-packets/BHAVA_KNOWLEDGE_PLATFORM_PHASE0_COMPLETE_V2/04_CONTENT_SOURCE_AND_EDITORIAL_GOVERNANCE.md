# Content, Source, and Editorial Governance

## Source acquisition rule

Use sources in this order:

1. verified private `bhava-library` corpus;
2. authorized editions and official ISKCON/BBT/Ministry sources;
3. primary source needed to fill a recorded gap;
4. secondary material for discovery only, never as unverified authority.

Do not download from arbitrary mirrors. Availability does not establish authenticity, permission, edition, completeness, or doctrinal context.

## Private/public boundary

Private originals remain immutable and are never served by public routes, public search, sitemap, CDN, source panels, or Git. The public application receives only a checksumed export containing approved metadata, locators, permitted excerpts, rights status, and source dossier references.

## Canonical record package

- `record.json` — schema-valid identity, taxonomy, lifecycle, relationships;
- `content` — ordered typed blocks;
- `source_dossier.json` — edition/source identity, locators, checksums, adequacy;
- `claims.json` — claim-to-evidence map;
- `rights.json` — quotation/adaptation/translation/commercial permissions separately;
- `assets.json` — provenance, rights, accessibility, review, hashes;
- `reviews.json` — immutable review decision references;
- `manifest.json` — package/template/tool versions and all hashes.

## Sanskrit and translation contract

For prayer/mantra/verse content, store separately:

- original script (`sa-Deva` where applicable);
- normalized Unicode form;
- IAST transliteration;
- verified English translation;
- translator/edition and exact locator;
- optional word-for-word meanings with source;
- variant readings only when explicitly documented;
- pronunciation notes as editorial metadata, not invented phonetics.

AI may format verified text but must not reconstruct missing Sanskrit or silently “correct” an edition. Any discrepancy becomes `SOURCE_CONFLICT` and stops publication.

## Age adaptation

Each adaptation records the canonical record/version, presentation profile, adaptation author/tool/prompt version, fidelity checks, and reviewer decisions. It may simplify vocabulary and explanation; it may not change the canonical mantra, translation, philosophical conclusion, historical fact, or quoted speech.

## Required human decisions

| Review | Required for |
|---|---|
| Editorial | all public records/derivatives |
| Scriptural/devotional | all doctrinal or scriptural explanation |
| Sanskrit/source | original text, transliteration, translation, quotations |
| Rights | quotations, translations, images, third-party materials, publication |
| Age/education | child/teen pages, teacher packs, worksheets |
| Specialist | operational Deity worship or other trained practices |
| Final owner publication | every public release candidate |

No agent fills reviewer names or approval dates without a real decision.

## Batch policy

- Pilot: five representative private-preview pages.
- Controlled batch: 25 after pilot lock.
- Factory batch: 50 after two manual cycles prove reviewer capacity and defect control.
- Remaining roadmap: prioritized batches, never bulk-promoted from research to published.

Each batch manifest freezes item IDs, source dossiers, template version, required assets/reviewers, and exclusions before drafting begins.

## Failed attachments

These files were unavailable and were not read or used:

- `Letter to Hayagriva TW.pdf`
- `SB 2-3-22 TW.pdf`
- `NoD ch 13 TW.pdf`
- `Cc Madhya 15.108 TW.pdf`
- `Letters from Srila PrabhupadaTW.pdf`
- `SB 7.5.23-24TW.pdf`
- `NOD chapter 8TW.pdf`
- `Offenses in deity worshipTW.pdf`
- `NoD ch 9 TW.pdf`
- `Who are you offending - HG Mahatma Dasa.pdf`
- `Dangers of Vaisnava Aparadha - HH Radhanath Swami.pdf`
- `Cleanliness and PunctualityTW.pdf`

Please re-upload them before the Etiquette/Deity Worship/Offenses vertical reaches source-adequacy review, unless verified equivalents are already present in `bhava-library`.

## Stop conditions

Stop at `HOLD` for missing/inadequate/contradictory sources; rights uncertainty; unverifiable Sanskrit, attribution, quote, or locator; absent required reviewer; private-data leakage; doctrinal drift; failed accessibility; export mismatch; or manifest/hash mismatch. Never silently substitute a weaker source or approval.

