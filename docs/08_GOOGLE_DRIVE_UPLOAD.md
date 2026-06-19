# Google Drive Upload

Upload generated story packages to a Google Drive parent folder for parent access.

## Why Drive

v1 sends parents a WhatsApp template with a package link. Direct MP3/PDF upload via WhatsApp Cloud API is not implemented yet.

## Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Drive API**.
3. Configure OAuth consent screen (External or Internal as appropriate).
4. Create **OAuth Desktop** client credentials.
5. Download JSON and save locally as:
   `credentials/google_drive_oauth_client.json`
6. Do **not** commit `credentials/`.

## Local `.env`

```env
GOOGLE_DRIVE_UPLOAD_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei
GOOGLE_DRIVE_FOLDER_URL=https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei?usp=sharing
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials/google_drive_oauth_client.json
GOOGLE_DRIVE_TOKEN_FILE=credentials/google_drive_token.json
```

First upload opens a browser for OAuth. Token is saved to `credentials/google_drive_token.json` (local only).

Install Drive dependencies if missing:

```powershell
pip install -r requirements.txt
```

Required packages: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`.

## Parent folder permissions

- Share the parent folder with parents as **Viewer**.
- The uploader Google account must have **Editor** access to upload files.
- Do not give parents Editor access on the parent folder.

## Upload behavior

When enabled, each prod run:

1. Creates `<chapter_no>_<slug>` under the parent folder
2. Uploads all package files
3. Sets `manifest.package.package_link` to the per-story folder link
4. Updates `whatsapp_caption.txt` with that link
5. Logs results to `tracking/storage_log.csv`

## Fallback: local sync

If API upload is disabled but `GOOGLE_DRIVE_LOCAL_SYNC_ROOT` points to a synced Drive folder, the pipeline copies the output folder there and uses the parent folder URL as the link.

## Test upload

```powershell
.\scripts\test_google_drive_upload.ps1
```

## Troubleshooting

- Missing credentials → save OAuth JSON locally
- Token expired → delete `credentials/google_drive_token.json` and re-auth
- Upload disabled → check `GOOGLE_DRIVE_UPLOAD_ENABLED=true`
