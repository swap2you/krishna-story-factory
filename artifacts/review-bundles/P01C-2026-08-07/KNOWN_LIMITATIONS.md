# KNOWN_LIMITATIONS — P01C

1. Golden record remains `SOURCE_BLOCKED` with synthetic fixture text only.
2. Studio must bind to loopback (`127.0.0.1`) with `BHAVA_PUBLIC_SITE=0`.
3. `next start` is incompatible with `output: standalone` in this app; use the standalone server entry for review screenshots (not `next dev`).
4. No new Knowledge FTS indexing in the pilot.
5. Etiquette/Deity Worship PDF set is tracked separately under local library ingestion (not a P01C merge blocker). Owner-authorized ingestion is recorded outside this PR.
6. PDF/UA is not claimed.
7. Board B artwork uses placeholder slots only.
8. Related-content links (P1-F10), full 44px audit (P1-U02), and full zoom matrix (P1-U03) remain deferred.
9. DOCX OOXML font embedding is deferred: manifests use `font_resource_hashes` with `fonts_embedded: false` and Noto family names on runs/styles.
10. Headers/footers, native image-alt, multi-page mantra-unit protection, orphan-heading prevention, and full stress-layout validation remain PARTIAL/DEFERRED in P1-E05/E06.
11. Local Docker image build may be unavailable on some workstations; Production CI validates images.
12. `P01C_REVIEW_BUNDLE.zip` is local-only (not in Git).
