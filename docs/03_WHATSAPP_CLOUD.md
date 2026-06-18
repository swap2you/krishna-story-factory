# WhatsApp Cloud — v1

## Scope

- Individual opted-in numbers from `input/whatsapp_recipients.csv`
- Template messages only
- **No WhatsApp groups in v1**
- No direct MP3/PDF/image upload yet

## Recommended production path

Approved WhatsApp template + **Google Drive parent folder link** (viewer access for parents).

Set in `.env`:

- `GOOGLE_DRIVE_FOLDER_URL` — parent folder shared with families
- `GOOGLE_DRIVE_LOCAL_SYNC_ROOT` — optional local Google Drive sync path for auto-copy

v1 does not require Drive API. Copy each `output/<chapter>_<slug>/` folder into the synced Drive parent folder, or set `GOOGLE_DRIVE_LOCAL_SYNC_ROOT` so the pipeline copies automatically.

## Why individual CSV broadcast, not WhatsApp group

v1 sends template messages only to opted-in numbers in `input/whatsapp_recipients.csv`. WhatsApp Cloud API does not support ordinary group posting in this project.

## Why Drive link instead of direct media

Templates are reliable for parent notification. MP3/PDF/image upload via Cloud API is not implemented in v1.

## Switch from hello_world to daily_krishna_story

1. Get Meta approval for `daily_krishna_story` with body variables: family name, story title, package link.
2. Set `WHATSAPP_TEMPLATE_NAME=daily_krishna_story` in local `.env`.
3. Keep `GOOGLE_DRIVE_FOLDER_URL` configured so {{3}} is the package link.
4. Use `hello_world` only for smoke tests.

## Failure diagnosis

```powershell
Get-Content tracking\send_log.csv -Tail 10
.\scripts\diagnose_whatsapp_failure.ps1
```

Structured failure reasons in send log: `TOKEN_EXPIRED`, `TEMPLATE_NOT_FOUND`, `TEMPLATE_PARAMS_MISMATCH`, `RECIPIENT_NOT_ALLOWED`, `META_API_ERROR`.

## Test setup

Use Meta test number and `hello_world` template:

```powershell
python scripts/test_whatsapp_cloud.py
python scripts/test_whatsapp_broadcast.py
```

## Recipient CSV rules

- `opt_in=true` and `status=active` required
- Rows with `REPLACE` in phone number are skipped
- Phone numbers normalized to digits only

## Daily story integration

When `WHATSAPP_SEND_ENABLED=true` and `WHATSAPP_SENDER_TYPE=cloud`, prod runs send after quality PASS.

If `WHATSAPP_TEMPLATE_NAME=daily_krishna_story` is not approved, package generation still succeeds and send is skipped with a log note.

## Switching to production business number

Update local `.env` only:

- `WHATSAPP_BUSINESS_ACCOUNT_ID`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_CLOUD_TOKEN`
- `WHATSAPP_TEMPLATE_NAME`
