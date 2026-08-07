# KNOWN_LIMITATIONS — P01C

1. Golden record remains `SOURCE_BLOCKED` with synthetic fixture text only.
2. Studio must bind to loopback (`127.0.0.1`) with `BHAVA_PUBLIC_SITE=0`.
3. `next start` is incompatible with `output: standalone` in this app; use standalone server entry or `next dev` for local studio.
4. No new Knowledge FTS indexing in the pilot.
5. Etiquette/Deity Worship 12 PDFs still MISSING (not a P01C blocker).
6. PDF/UA is not claimed.
7. Board B artwork uses placeholder slots only.
8. Related-content links (P1-F10), full 44px audit (P1-U02), and full zoom matrix (P1-U03) remain deferred.
9. Local Docker image build was unavailable on the remediation workstation; Production CI must validate images.
10. `P01C_REVIEW_BUNDLE.zip` is local-only (not in Git).
11. Merge / staging / production / scheduler remain out of scope.
