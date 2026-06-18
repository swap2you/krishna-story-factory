# WhatsApp Cloud — v1

## Scope

- Individual opted-in numbers from `input/whatsapp_recipients.csv`
- Template messages only
- **No WhatsApp groups in v1**
- No direct MP3/PDF/image upload yet

## Recommended production path

Approved WhatsApp template + Google Drive / output package link.

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
