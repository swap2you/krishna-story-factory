$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
.\.venv\Scripts\python.exe scripts/test_whatsapp_cloud.py @args
exit $LASTEXITCODE
