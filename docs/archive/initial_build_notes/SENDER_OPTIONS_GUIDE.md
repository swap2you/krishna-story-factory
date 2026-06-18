# Sender Options Guide

## Recommendation

Primary: WhatsApp Business Cloud API (template + package link).

Fallback: Telegram.

Reason: Telegram bot/channel delivery is usually simpler than WhatsApp business onboarding. WhatsApp remains best for parents once Meta business assets are approved.

## Supported sender types

```env
WHATSAPP_SENDER_TYPE=manual
WHATSAPP_SENDER_TYPE=web_test
WHATSAPP_SENDER_TYPE=cloud
WHATSAPP_SENDER_TYPE=telegram
WHATSAPP_SENDER_TYPE=slack
WHATSAPP_SENDER_TYPE=discord
```

## Manual

No external send. Logs package location.

## Web test

Creates a local outbox for private testing.

## WhatsApp Cloud (v1)

Uses Meta WhatsApp Business Cloud API.

v1 behavior:

- Sends approved **template** messages only (`hello_world` for Meta test setup)
- Broadcasts one-by-one to active opted-in numbers in `input/whatsapp_recipients.csv`
- Does **not** send to WhatsApp groups
- Does **not** upload MP3/PDF/image yet
- Logs each recipient result to `tracking/send_log.csv`

Smoke tests:

```powershell
.\.venv\Scripts\python.exe scripts/test_whatsapp_cloud.py
.\.venv\Scripts\python.exe scripts/test_whatsapp_broadcast.py
```

See [WHATSAPP_BUSINESS_CLOUD_GUIDE.md](WHATSAPP_BUSINESS_CLOUD_GUIDE.md).

## Telegram

Needs:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Slack

Needs:

```env
SLACK_WEBHOOK_URL=
```

## Discord

Needs:

```env
DISCORD_WEBHOOK_URL=
```

## Do not use fragile automation first

Do not build the first production version on unofficial browser automation. It may break, require QR sessions, or violate platform expectations.

Group sending is intentionally **not** part of v1.
