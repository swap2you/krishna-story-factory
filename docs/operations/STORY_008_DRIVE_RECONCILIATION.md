# Story 008 Drive reconciliation

**Do not modify Drive.** Evidence-only reconciliation.

## Observed sequence

1. **Recovery generation (no-upload):** initial recovery CLI used `--no-upload` / upload disabled by flag while completing missing six artifacts and atomic publish to local `output/`.
2. **Separate upload + verify:** later operator/recovery step uploaded the exact-eight package to Drive folder `13Eou8ulavxq811tpgugpCyDo1YTfiQnQ` and ran verify.
3. **Docs conflict:** `docs/releases/STORY_008_DRIVE_SYNC.json` records `verify_ok: false` with caption/link mismatch detail while `STORY_008_RECOVERY_RELEASE.md` reports verify PASS — treat the JSON as an intermediate snapshot and the release note as the later operator-accepted state unless re-verified live.
4. **Queue:** `008=done` with `drive_folder_id=13Eou8ulavxq811tpgugpCyDo1YTfiQnQ`.

## Honest conclusion

Recovery without upload, followed by a separate upload/verify pass, is the real sequence. Intermediate verify failures may exist in frozen JSON snapshots; do not rewrite raw logs. Live Drive re-verify is optional and out of scope for V1.6 (no Drive mutation).
