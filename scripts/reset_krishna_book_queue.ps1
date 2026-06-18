$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$src = Join-Path $PSScriptRoot "..\input\series_plan.csv"
if (-not (Test-Path $src)) { throw "series_plan.csv not found" }
Copy-Item -Force $src "input\series_plan.csv"
Write-Host "Restored Krishna Book queue from repository template."
