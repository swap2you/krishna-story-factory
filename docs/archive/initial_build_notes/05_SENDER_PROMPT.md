# 05 Sender Prompt

Implement sender behavior through a clean interface.

Required senders:
- `ManualSender`
- `WhatsAppCloudSender`
- `WhatsAppGroupSender`
- `WhatsAppWebTestSender`
- `TelegramSender`
- `SlackWebhookSender`
- `DiscordWebhookSender`

Rules:
- `manual`: never sends externally; logs file paths.
- `web_test`: creates a local outbox for private manual testing.
- `cloud`: uses WhatsApp Business Cloud API.
- `group`: should remain explicit unsupported/stub unless a safe official method is provided.
- `telegram`: sends message + files to configured chat.
- `slack`: sends a webhook notification with local file paths.
- `discord`: sends a webhook notification.

Do not create unsafe WhatsApp scraping automation.

Deliverable: sender tests using mocked HTTP calls.
