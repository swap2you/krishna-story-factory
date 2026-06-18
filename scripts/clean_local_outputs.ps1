$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
Get-ChildItem "output" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "Cleaned output/* (kept output/.gitkeep)"
