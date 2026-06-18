# Validation Artifacts

Validation date: 2026-06-18

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/test_whatsapp_cloud.py
```

## Pytest result

```text
10 passed
```

Includes:

- `tests/test_pipeline_test_mode.py`
- `tests/test_whatsapp_sender.py` (phone normalization, config errors, recipient filtering, mocked Meta success, no token in errors)

## Pipeline result (test mode)

```json
{
  "status": "SUCCESS",
  "quality_status": "PASS",
  "whatsapp_status": "NOT_ATTEMPTED"
}
```

Test mode does not call WhatsApp even when cloud sender is configured locally.

## WhatsApp Cloud smoke test

```text
SUCCESS
Meta message id: wamid....
```

Template: `hello_world`  
Recipient: configured `WHATSAPP_TEST_RECIPIENT_PHONE`  
Token source: local `.env` only (`WHATSAPP_CLOUD_TOKEN`)

## Recipient CSV template

`input/whatsapp_recipients.csv`:

```csv
name,phone_e164,opt_in,status,notes
Swapnil Test,+17143074266,true,active,Meta test recipient
```

## Send log schema

`tracking/send_log.csv` columns:

```text
date,chapter_no,slug,sender_type,recipient_name,recipient_phone,status,detail,message_id,created_at
```

## Regenerate locally

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
python run_daily_story.py --mode test --force
python scripts/test_whatsapp_cloud.py
python scripts/test_whatsapp_broadcast.py
```

Next pending story in sample queue: `005_boat-crossing`.
