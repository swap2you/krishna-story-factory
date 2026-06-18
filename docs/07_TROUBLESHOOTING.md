# Troubleshooting

## Streamlit launcher broken after moving project

```powershell
.\scripts\repair_venv.ps1
python -m streamlit run dashboard.py
```

## WhatsApp token expired

Paste fresh token into `WHATSAPP_CLOUD_TOKEN` in `.env`, then:

```powershell
python scripts/test_whatsapp_cloud.py
```

## No pending story

Reset or edit `input/series_plan.csv` and set a row to `pending`.

## ElevenLabs fails in prod

- Verify `ELEVENLABS_VOICE_ID`
- Or set `ALLOW_PLACEHOLDER_AUDIO=true` temporarily for debugging only

## OpenAI image fails

Pipeline falls back to local story card. Check `manifest.json` `image_source`.

## Duplicate send blocked

Use `--force` only when intentional. Check `tracking/story_log.csv`.

## Clean local generated output

```powershell
.\scripts\clean_local_outputs.ps1
```
