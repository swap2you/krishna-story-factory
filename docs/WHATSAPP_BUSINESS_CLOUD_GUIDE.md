# WhatsApp Business Cloud API Guide

This is the preferred WhatsApp path if you want a supported business-account-based integration.

Official docs:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform
- https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started
- https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages

## What you need

- Meta developer account
- Meta Business account
- WhatsApp Business Account (WABA)
- Business phone number registered for Cloud API
- Phone Number ID
- Permanent or system-user access token
- Target recipient phone numbers in international format
- Approved message templates if sending proactive daily messages outside the customer-service window

## High-level setup

1. Go to Meta for Developers.
2. Create or open an app.
3. Add WhatsApp product.
4. Connect or create a WhatsApp Business Account.
5. Add/register your business phone number.
6. Get the `Phone Number ID`.
7. Create a system user/token with required WhatsApp permissions.
8. Add test recipient numbers first.
9. Send a test text message from Meta's API explorer or Postman collection.
10. Add credentials to `.env`.

## `.env` values

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=cloud
WHATSAPP_GRAPH_API_VERSION=v23.0
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID
WHATSAPP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
WHATSAPP_TARGET_PHONE=15551234567
WHATSAPP_TEMPLATE_NAME=
WHATSAPP_LANGUAGE_CODE=en_US
```

## Important limitation

WhatsApp Cloud API is good for business messaging. It is not the same as logging into your personal WhatsApp and posting to a normal group. If the parents are in a normal WhatsApp group, the cleanest production path may still require manual forwarding or a supported business messaging flow.

## Suggested rollout

Week 1:

```env
WHATSAPP_SENDER_TYPE=web_test
```

Generate local packages and forward manually to your private test group.

After successful trial:

```env
WHATSAPP_SENDER_TYPE=cloud
```

Send to approved/test numbers or a compliant business messaging list.

## Templates

For daily proactive sends, create a template such as:

Name:

```text
krishna_story_daily
```

Possible body:

```text
Hare Krishna! Today's Krishna-katha package is ready: {{1}}. Please read/listen with your child and complete the activity sheet.
```

Meta must approve templates before production use.
