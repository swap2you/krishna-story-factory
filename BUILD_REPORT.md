# Build Report

Build pack version: `1.0`  
Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)  
Validation date: 2026-06-18

## WhatsApp Cloud v1 changes

- Template-based WhatsApp Cloud sender for individual opted-in recipients
- `input/whatsapp_recipients.csv` broadcast list
- `scripts/test_whatsapp_cloud.py` and `scripts/test_whatsapp_broadcast.py` smoke tests
- `WHATSAPP_CLOUD_TOKEN` loaded from local `.env` only (never committed)
- Test mode skips WhatsApp send; prod mode sends `hello_world` template when cloud sender is enabled
- No WhatsApp group sending in v1
- No direct MP3/PDF/image WhatsApp upload in v1

## Validation commands run

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/test_whatsapp_cloud.py
```

## Validation results

| Check | Result |
|-------|--------|
| `pytest -q` | **PASSED** — 10 tests |
| `python run_daily_story.py --mode test --force` | **SUCCESS**, quality **PASS** |
| `python scripts/test_whatsapp_cloud.py` | **SUCCESS** — Meta message id returned |
| `.env` gitignored | Yes |
| Token committed | No |

## Known limitations

- v1 uses template messages only; switch to `daily_krishna_story` after Meta approval
- Recommended production path: template + Google Drive package link
- WhatsApp group delivery is not supported in v1

## Docs

See [README.md](README.md) and [docs/WHATSAPP_BUSINESS_CLOUD_GUIDE.md](docs/WHATSAPP_BUSINESS_CLOUD_GUIDE.md).
