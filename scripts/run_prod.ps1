param([Parameter(ValueFromRemainingArguments = $true)][string[]]$RemainingArgs)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Run scripts/bootstrap.ps1 first." }
& $Python (Join-Path $ProjectRoot "run_daily_story.py") --mode prod @RemainingArgs
exit $LASTEXITCODE
