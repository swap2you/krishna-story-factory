# WhatsApp Business Cloud API Guide

This is the preferred WhatsApp path for v1 parent delivery using Meta's Cloud API.

Official docs:

- [WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform)
- [Get started](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started)
- [Send messages](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages)

## v1 scope

- **Individual broadcast only** — one message per opted-in phone number from `input/whatsapp_recipients.csv`
- **No WhatsApp group sending in v1**
- **Template messages only** — start with Meta's `hello_world` test template
- **No direct MP3/PDF/image upload yet** — recommended production path is:
  **approved WhatsApp template + Google Drive / output package link**

## Meta test setup (example)

```env
WHATSAPP_GRAPH_API_VERSION=v25.0
WHATSAPP_BUSINESS_ACCOUNT_ID=your_waba_id
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_TEST_RECIPIENT_PHONE=17143074266
WHATSAPP_TEMPLATE_NAME=hello_world
WHATSAPP_TEMPLATE_LANGUAGE=en_US
```

## `.env` values

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=cloud
WHATSAPP_GRAPH_API_VERSION=v25.0
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_CLOUD_TOKEN=
WHATSAPP_TEST_RECIPIENT_PHONE=
WHATSAPP_TEMPLATE_NAME=hello_world
WHATSAPP_TEMPLATE_LANGUAGE=en_US
WHATSAPP_RECIPIENTS_CSV=input/whatsapp_recipients.csv
```

**Never commit `.env` or `WHATSAPP_CLOUD_TOKEN`.**

`WHATSAPP_ACCESS_TOKEN` is still read as a legacy alias if `WHATSAPP_CLOUD_TOKEN` is empty.

## Recipient CSV

`input/whatsapp_recipients.csv`:

```csv
name,phone_e164,opt_in,status,notes
Swapnil Test,+17143074266,true,active,Meta test recipient
```

Rules:

- Only `opt_in=true` and `status=active` rows receive messages
- Phone numbers are normalized to digits only for the API
- No group IDs or group broadcast in v1

## Smoke tests

Single Meta test recipient:

```powershell
.\.venv\Scripts\python.exe scripts/test_whatsapp_cloud.py
```

Broadcast to all active opted-in recipients:

```powershell
.\.venv\Scripts\python.exe scripts/test_whatsapp_broadcast.py
```

Expected success output:

```text
SUCCESS
Meta message id: wamid....
```

If `WHATSAPP_CLOUD_TOKEN` is missing:

```text
Paste a fresh Meta temporary token into WHATSAPP_CLOUD_TOKEN in .env, then rerun.
```

## Daily story integration

```powershell
python run_daily_story.py --mode prod --force
```

When `WHATSAPP_SEND_ENABLED=true` and `WHATSAPP_SENDER_TYPE=cloud`:

1. Full story package is generated locally
2. `hello_world` template is sent to active opted-in recipients
3. Each send is logged in `tracking/send_log.csv`

Test mode does **not** call WhatsApp even if send is enabled.

## Switching to production business number later

Update in local `.env` only:

```env
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_CLOUD_TOKEN=
WHATSAPP_TEMPLATE_NAME=daily_krishna_story
```

Use an approved Meta template such as `daily_krishna_story` for real daily parent sends.

## Suggested rollout

Week 1 — local package + manual forward:

```env
WHATSAPP_SENDER_TYPE=web_test
```

Week 2 — Meta test number + `hello_world`:

```powershell
scripts/test_whatsapp_cloud.py
```

Production — approved template + package link:

```env
WHATSAPP_TEMPLATE_NAME=daily_krishna_story
```

## Important limitation

WhatsApp Cloud API is for business messaging to individual opted-in numbers. It is not the same as posting to a normal WhatsApp group.
