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
.\scripts\diagnose_whatsapp_failure.ps1
Get-Content tracking\send_log.csv -Tail 10
```

Look for `reason=TOKEN_EXPIRED` in send_log detail.

## Audio says "pause"

Regenerate with updated prompts. Pipeline sanitizes `[pause]` to `<break time="1.2s" />` before ElevenLabs.

## Audio too short

Prod quality fails if narration.mp3 is <= 500 KB or outside the validated duration window. The audio
performance script is stored in the hidden metadata section of `story.md`.

## Drive package link missing

Set `GOOGLE_DRIVE_FOLDER_URL` in `.env`. Optionally set `GOOGLE_DRIVE_LOCAL_SYNC_ROOT` to auto-copy output folders.

## No pending story

Inspect ignored `tracking/queue_state.csv`. Reset the intended row there or use the queue reset helper;
never add mutable status to `input/series_plan.csv`.

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
