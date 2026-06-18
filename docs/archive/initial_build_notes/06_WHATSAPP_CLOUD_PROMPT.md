# 06 WhatsApp Business Cloud Prompt

Improve `WhatsAppCloudSender` using Meta WhatsApp Business Cloud API assumptions.

Required config values:
- `WHATSAPP_GRAPH_API_VERSION`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_TARGET_PHONE`
- optional `WHATSAPP_TEMPLATE_NAME`
- optional `WHATSAPP_LANGUAGE_CODE`

Behavior:
- Send the caption as text if within the customer-service window or approved policy allows it.
- For proactive daily messages outside the service window, document that approved templates may be required.
- Upload/send media files only if practical and supported by current code.
- If media upload is not fully implemented, make it explicit in `BUILD_REPORT.md` and keep package generated locally.

Deliverable: docs and tests using mocked requests. Do not require live Meta credentials for unit tests.
