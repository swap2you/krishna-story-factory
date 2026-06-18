# API Keys Guide

Do not commit `.env`.

## OpenAI

Official docs:

- https://developers.openai.com/api/docs/quickstart
- https://developers.openai.com/api/reference/responses/overview/
- https://developers.openai.com/api/docs/guides/image-generation

Steps:

1. Open the OpenAI Platform.
2. Create or select a project.
3. Create an API key.
4. Copy `.env.example` to `.env`.
5. Set:

```env
OPENAI_TEXT_ENABLED=true
OPENAI_API_KEY=YOUR_KEY
OPENAI_TEXT_MODEL=gpt-4.1
```

For image generation:

```env
OPENAI_IMAGE_ENABLED=true
OPENAI_IMAGE_MODEL=gpt-image-1
OPENAI_IMAGE_SIZE=1024x1024
OPENAI_IMAGE_QUALITY=medium
```

Run:

```powershell
python run_daily_story.py --mode prod --force
```

## ElevenLabs

Official docs:

- https://elevenlabs.io/docs/overview/capabilities/text-to-speech
- https://elevenlabs.io/docs/api-reference/text-to-speech/convert
- https://elevenlabs.io/docs/api-reference/voices/search

Steps:

1. Open ElevenLabs.
2. Create an API key.
3. Pick or create a narration voice.
4. Copy the voice ID.
5. Set:

```env
ELEVENLABS_ENABLED=true
ELEVENLABS_API_KEY=YOUR_KEY
ELEVENLABS_VOICE_ID=YOUR_VOICE_ID
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

## WhatsApp Business Cloud

Official docs:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started

Steps:

1. Create Meta app with WhatsApp product.
2. Copy Phone Number ID and temporary access token from Meta.
3. Add test recipient in Meta dashboard.
4. Set local `.env` only (never commit):

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=cloud
WHATSAPP_GRAPH_API_VERSION=v25.0
WHATSAPP_BUSINESS_ACCOUNT_ID=YOUR_WABA_ID
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID
WHATSAPP_CLOUD_TOKEN=YOUR_TEMP_OR_SYSTEM_TOKEN
WHATSAPP_TEST_RECIPIENT_PHONE=17143074266
WHATSAPP_TEMPLATE_NAME=hello_world
WHATSAPP_TEMPLATE_LANGUAGE=en_US
WHATSAPP_RECIPIENTS_CSV=input/whatsapp_recipients.csv
```

Smoke test:

```powershell
.\.venv\Scripts\python.exe scripts/test_whatsapp_cloud.py
```

v1 sends template messages to opted-in individuals from CSV. Group sending is not supported.

For production daily parent sends, switch later to approved template `daily_krishna_story` plus a Google Drive package link.

## Streamlit

Official docs:

- https://docs.streamlit.io/get-started/installation
- https://docs.streamlit.io/develop/concepts/architecture/run-your-app

Run:

```powershell
streamlit run dashboard.py
```
