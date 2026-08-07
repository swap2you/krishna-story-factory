# KNOWN_LIMITATIONS — P01C

1. **Golden record remains `SOURCE_BLOCKED`.** Synthetic fixture only; no approved scripture.
2. **Studio must bind to loopback** (`127.0.0.1`) with `BHAVA_PUBLIC_SITE=0`. Host-only loopback is not sufficient against a publicly bound process.
3. **`next start` is incompatible with `output: standalone`** in this app; use the standalone server entry or `next dev` for local studio preview.
4. **No new search indexing** for Knowledge packages during the pilot.
5. **Etiquette/Deity Worship 12 PDFs** still not restored — see `PDF_RECOVERY_MANIFEST.csv` (not a P01C blocker).
6. **PDF/UA not claimed**; exports are study-neutral structural renders.
7. **Board B artwork** uses governed placeholder slots only — no production art.
8. **Automated axe / full e2e matrix / Compose prod image** not claimed PASS this run (see `TEST_RESULTS.md`).
9. **Default bootstrap token** exists for local non-production only.
10. Merge / staging / production / scheduler **out of scope**.
