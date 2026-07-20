# Architecture

`krishna-story-factory` is a local-first Python automation project.

The project deliberately avoids heavy infrastructure. The source of truth is CSV. The core engine is the CLI. The dashboard is optional and only calls the CLI or edits CSV.

## Main flow

1. Read the next pending row from `input/series_plan.csv`.
2. Generate child-friendly Krishna-conscious story content.
3. Generate an audio narration script.
4. Generate `narration.mp3` using ElevenLabs in prod, or a local placeholder in test mode.
5. Generate image prompt and story card.
6. Generate printable activity sheet PDF.
7. Save all files under `output/<chapter_no>_<slug>/`.
8. Run quality checks.
9. Write `manifest.json`.
10. Update `tracking/story_log.csv`.
11. Send or stage the package through the configured sender.

## CLI is source of truth

Core command:

```bash
.\scripts\run_test.ps1
```

Production command:

```bash
.\scripts\run_prod.ps1
```

Force override:

```bash
.\scripts\run_prod.ps1 --force
```

## Modules

```text
krishna_story_factory/
  audio/          ElevenLabs or local placeholder MP3
  generation/     OpenAI or deterministic test generator
  image/          OpenAI image or local Pillow story card
  pdf/            ReportLab activity sheet
  quality/        Automated gates
  senders/        Pluggable delivery adapters
  config.py       .env loading
  csv_store.py    CSV queue and logs
  manifest.py     manifest writer
  models.py       dataclasses
  pipeline.py     orchestration
```

## Sender strategy

Preferred real parent delivery: WhatsApp Business Cloud API.

Fallback senders:

- Telegram
- Slack
- Discord
- Manual/local outbox

Ordinary WhatsApp group automation is intentionally not treated as safe production automation. Keep it as a stub/private test path unless a supported official method is available.

## Optional dashboard

Run:

```bash
streamlit run dashboard.py
```

Dashboard responsibilities:

- show next pending story
- show queue
- show logs
- edit CSV
- trigger test/prod CLI

Dashboard must not replace the CLI.
