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

## Streamlit

Official docs:

- https://docs.streamlit.io/get-started/installation
- https://docs.streamlit.io/develop/concepts/architecture/run-your-app

Run:

```powershell
streamlit run dashboard.py
```
