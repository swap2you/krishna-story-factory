# Troubleshooting

## `python` is not recognized

Install Python and ensure it is on PATH.

## PowerShell blocks activation

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Missing package error

Run:

```powershell
pip install -r requirements.txt
```

## No pending story

Open `input/series_plan.csv` and set one row:

```text
status=pending
```

## Quality check failed

Open the generated `manifest.json` and the console output. Usually the issue is a missing/empty file.

## WhatsApp failed

First switch to safe local mode:

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=web_test
```

Then rerun:

```powershell
.\scripts\run_prod.ps1 --force
```

If local outbox works, your issue is external API configuration, not package generation.
