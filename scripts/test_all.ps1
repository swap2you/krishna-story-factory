$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Run scripts/bootstrap.ps1 first." }
Push-Location $ProjectRoot
try { & $Python -m pytest -q; exit $LASTEXITCODE } finally { Pop-Location }
