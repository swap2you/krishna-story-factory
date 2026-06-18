$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
.\.venv\Scripts\python.exe scripts\test_google_drive_upload.py
