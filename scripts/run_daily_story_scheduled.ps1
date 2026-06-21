param([string]$ProjectRoot = "")

$ErrorActionPreference = "Stop"
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EntryPoint = Join-Path $ProjectRoot "run_daily_story.py"
$LogDir = Join-Path $ProjectRoot "logs\scheduler"
$History = Join-Path $ProjectRoot "tracking\run_history.csv"
if (-not (Test-Path -LiteralPath $Python)) { throw "Virtual-environment Python not found: $Python" }

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Get-ChildItem -LiteralPath $LogDir -Filter "daily_*.log" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -Skip 30 | Remove-Item -Force

$Started = Get-Date
$Log = Join-Path $LogDir ("daily_{0}.log" -f $Started.ToString("yyyyMMdd_HHmmss"))
$env:WHATSAPP_SEND_ENABLED = "false"
$env:TELEGRAM_SEND_ENABLED = "false"
$env:GOOGLE_DRIVE_UPLOAD_ENABLED = "true"

Push-Location $ProjectRoot
try {
    & $Python $EntryPoint --mode prod *>&1 | Tee-Object -FilePath $Log
    $ExitCode = $LASTEXITCODE
} catch {
    $_ | Out-String | Add-Content -LiteralPath $Log
    $ExitCode = 1
} finally {
    Pop-Location
}

$Completed = Get-Date
$Detail = (Get-Content -LiteralPath $Log -Raw -ErrorAction SilentlyContinue)
if ($Detail.Length -gt 1000) { $Detail = $Detail.Substring($Detail.Length - 1000) }
$Row = [pscustomobject]@{
    started_at = $Started.ToString("o"); completed_at = $Completed.ToString("o")
    status = $(if ($ExitCode -eq 0) { "SUCCESS" } else { "FAILED" })
    chapter_no = ""; slug = ""; detail = $Detail; exit_code = [string]$ExitCode
}
if (-not (Test-Path -LiteralPath $History)) {
    $Row | Export-Csv -LiteralPath $History -NoTypeInformation
} else {
    $Row | Export-Csv -LiteralPath $History -NoTypeInformation -Append
}
exit $ExitCode

