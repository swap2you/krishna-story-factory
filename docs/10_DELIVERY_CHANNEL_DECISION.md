# Delivery channel decision

- WhatsApp Cloud templates provide strong parent reach but require approved templates, recipient consent,
  token maintenance, and per-recipient delivery controls.
- A Telegram bot or channel is simpler to automate but requires families to adopt another channel and is
  outside this release's tested sender architecture.
- Google Drive link-only delivery keeps generation independent of messaging credentials and avoids an
  accidental broadcast during the pilot.

Recommendation: use Google Drive generation only for the current pilot. Keep
`WHATSAPP_SEND_ENABLED=false` and `TELEGRAM_SEND_ENABLED=false`. Add a delivery sender only after the
pilot establishes recipient consent, operational ownership, and failure handling.

