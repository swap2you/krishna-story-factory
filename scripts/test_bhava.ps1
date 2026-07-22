param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Write-Output "== Existing factory suite =="
& (Join-Path $ProjectRoot "scripts\test_all.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "== Portal API / guards =="
$env:PYTHONPATH = Join-Path $ProjectRoot "apps\api"
& $Python -m pytest tests\portal -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "== Frontend unit =="
npm run test:web
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "== Typecheck =="
npm run typecheck:web
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "== Production build =="
npm run build:web
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "Bhāva test pack PASS"
