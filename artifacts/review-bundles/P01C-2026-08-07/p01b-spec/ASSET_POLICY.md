# Asset Policy — Phase 1

## Rules

1. Generate art only after exact stanza/context is approved (D03 / OD-14).  
2. Never put Sanskrit or translation only inside an image.  
3. Every asset requires: stable ID; linked record/stanza; brief/tool/version; reference provenance/permission; theological/iconographic checklist; age suitability; alt **or** decorative flag; dimensions/crops; sha256; license; reviewer; status; supersession.  
4. Informative vs decorative classification is mandatory for a11y (P1-U05).  
5. Phase 1 boards are placeholders only (D07); no production artwork in P01B.  
6. Prefer brand registry patterns (`brand-assets.json`) for shared chrome; stanza art is package-local under `assets.json`.  
7. Prohibit photoreal deities, meme/neon/AI-gloss, inconsistent tilaka/tulasī, particles, cursor-follow.  

## D05 identity assets

Footer/civil-name remediation is **specified only** in P01B — no logo/footer code change this run.

## Export assets

Embedded fonts for PDF must be license-cleared (OD-13). PDF manifests list `embedded_font_hashes`. DOCX manifests list `font_resource_hashes` with `fonts_embedded: false` until OOXML embedding is implemented.
