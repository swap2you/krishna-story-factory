"""Scheduled production runner — exit code must reflect Python, not stderr noise."""
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
$Stamp = $Started.ToString("yyyyMMdd_HHmmss")
$Log = Join-Path $LogDir ("daily_{0}.log" -f $Stamp)
$StdOutLog = Join-Path $LogDir ("daily_{0}.stdout.log" -f $Stamp)
$StdErrLog = Join-Path $LogDir ("daily_{0}.stderr.log" -f $Stamp)

$env:WHATSAPP_SEND_ENABLED = "false"
$env:TELEGRAM_SEND_ENABLED = "false"
$env:GOOGLE_DRIVE_UPLOAD_ENABLED = "true"

# Critical: do NOT pipe native stderr through PowerShell's error stream.
# With $ErrorActionPreference=Stop, Python logging.warning() on stderr was aborting
# the 2026-07-24 Story 008 run after narration and leaving a stale .pipeline.lock.
$ExitCode = 1
try {
    $proc = Start-Process -FilePath $Python `
        -ArgumentList @($EntryPoint, "--mode", "prod") `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StdOutLog `
        -RedirectStandardError $StdErrLog `
        -Wait -PassThru -NoNewWindow
    $ExitCode = if ($null -eq $proc.ExitCode) { 1 } else { [int]$proc.ExitCode }
} catch {
    $_ | Out-String | Set-Content -LiteralPath $Log -Encoding utf8
    $ExitCode = 1
}

# Merge stdout/stderr into the daily log without NativeCommandError conversion.
$merged = New-Object System.Text.StringBuilder
if (Test-Path -LiteralPath $StdOutLog) {
    [void]$merged.Append((Get-Content -LiteralPath $StdOutLog -Raw -ErrorAction SilentlyContinue))
}
if (Test-Path -LiteralPath $StdErrLog) {
    $errText = Get-Content -LiteralPath $StdErrLog -Raw -ErrorAction SilentlyContinue
    if ($errText) {
        [void]$merged.AppendLine("")
        [void]$merged.AppendLine("--- stderr ---")
        [void]$merged.Append($errText)
    }
}
Set-Content -LiteralPath $Log -Value $merged.ToString() -Encoding utf8
Remove-Item -LiteralPath $StdOutLog, $StdErrLog -Force -ErrorAction SilentlyContinue

$Completed = Get-Date
$Detail = (Get-Content -LiteralPath $Log -Raw -ErrorAction SilentlyContinue)
if ($Detail -and $Detail.Length -gt 1000) { $Detail = $Detail.Substring($Detail.Length - 1000) }
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
