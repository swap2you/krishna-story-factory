# Sender Options Guide

## Recommendation

Primary: WhatsApp Business Cloud API.

Fallback: Telegram.

Reason: Telegram bot/channel delivery is usually simpler than WhatsApp business onboarding. But WhatsApp remains best for parents if your business setup is approved.

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

## WhatsApp Cloud

Uses Meta WhatsApp Business Cloud API.

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
