# Scheduled production runner — exit code must reflect Python, not stderr noise.
# Safe validation (no generation / no queue mutation / no Drive):
#   .\scripts\run_daily_story_scheduled.ps1 -ValidateScheduler
param(
    [string]$ProjectRoot = "",
    [switch]$ValidateScheduler
)

$ErrorActionPreference = "Stop"
$WrapperVersion = "v1.6.0-start-process"
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EntryPoint = Join-Path $ProjectRoot "run_daily_story.py"
$LogDir = Join-Path $ProjectRoot "logs\scheduler"
$History = Join-Path $ProjectRoot "tracking\run_history.csv"
$QueuePath = Join-Path $ProjectRoot "tracking\queue_state.csv"
$LockPath = Join-Path $ProjectRoot ".pipeline.lock"

function Get-GitSha {
    try {
        Push-Location $ProjectRoot
        return (git rev-parse HEAD 2>$null).Trim()
    } catch {
        return "unknown"
    } finally {
        Pop-Location
    }
}

function Write-RunHeader {
    param(
        [string]$Mode,
        [string]$TaskName,
        [string]$QueueBefore,
        [string]$QueueAfter,
        [int]$ExitCode,
        [string]$ProviderCalls = "0",
        [string]$DriveActions = "none"
    )
    $header = @(
        "wrapper_version=$WrapperVersion"
        "git_sha=$(Get-GitSha)"
        "task_name=$TaskName"
        "trigger_time=$((Get-Date).ToString('o'))"
        "mode=$Mode"
        "queue_before=$QueueBefore"
        "queue_after=$QueueAfter"
        "provider_calls=$ProviderCalls"
        "drive_actions=$DriveActions"
        "exit_code=$ExitCode"
    ) -join "`n"
    return $header
}

if (-not (Test-Path -LiteralPath $Python)) { throw "Virtual-environment Python not found: $Python" }

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if ($ValidateScheduler) {
    $Started = Get-Date
    $Stamp = $Started.ToString("yyyyMMdd_HHmmss")
    $Log = Join-Path $LogDir ("validate_{0}.log" -f $Stamp)
    $queueBefore = if (Test-Path -LiteralPath $QueuePath) { (Get-FileHash -LiteralPath $QueuePath -Algorithm SHA256).Hash } else { "missing" }
    $failures = New-Object System.Collections.Generic.List[string]

    if (-not (Test-Path -LiteralPath $EntryPoint)) { $failures.Add("missing_entry_point") }
    if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "krishna_story_factory\stage_state.py"))) { $failures.Add("missing_stage_state") }
    if (-not (Test-Path -LiteralPath $QueuePath)) { $failures.Add("missing_queue") }

    # Read-only queue probe (no writes).
    $queueProbe = & $Python -c "from pathlib import Path; import csv; p=Path(r'$QueuePath'); rows=list(csv.DictReader(p.open(encoding='utf-8'))); print(len(rows)); print(next((r['status'] for r in rows if r.get('chapter_no')=='009'),'missing'))"
    if ($LASTEXITCODE -ne 0) { $failures.Add("queue_read_failed") }

    # Lock acquire/release without leaving a stale lock.
    $lockOwned = $false
    try {
        if (Test-Path -LiteralPath $LockPath) {
            $failures.Add("lock_already_present")
        } else {
            Set-Content -LiteralPath $LockPath -Value ("validate:{0}:{1}" -f $PID, (Get-Date).ToString('o')) -Encoding utf8
            $lockOwned = $true
        }
    } catch {
        $failures.Add("lock_acquire_failed")
    } finally {
        if ($lockOwned -and (Test-Path -LiteralPath $LockPath)) {
            Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Import stage_state without side effects.
    $stageProbe = & $Python -c "import sys; sys.path.insert(0, r'$ProjectRoot'); from krishna_story_factory import stage_state; print('stage_state_ok')"
    if ($LASTEXITCODE -ne 0) { $failures.Add("stage_state_import_failed") }

    $driveConfigured = [bool]$env:GOOGLE_DRIVE_UPLOAD_ENABLED
    $queueAfter = if (Test-Path -LiteralPath $QueuePath) { (Get-FileHash -LiteralPath $QueuePath -Algorithm SHA256).Hash } else { "missing" }
    if ($queueBefore -ne $queueAfter) { $failures.Add("queue_mutated") }

    $ExitCode = if ($failures.Count -eq 0) { 0 } else { 1 }
    $body = @(
        Write-RunHeader -Mode "validate-scheduler" -TaskName "Krishna Story Factory MWF" -QueueBefore $queueBefore -QueueAfter $queueAfter -ExitCode $ExitCode -ProviderCalls "0" -DriveActions "none"
        "drive_env_present=$driveConfigured"
        "queue_probe=$queueProbe"
        "stage_probe=$stageProbe"
        "failures=$($failures -join ',')"
        "note=Validation mode never invokes --mode prod, providers, Drive upload, or Story 009 generation."
    ) -join "`n"
    Set-Content -LiteralPath $Log -Value $body -Encoding utf8
    Write-Output $body
    exit $ExitCode
}

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
$queueBefore = if (Test-Path -LiteralPath $QueuePath) { (Get-FileHash -LiteralPath $QueuePath -Algorithm SHA256).Hash } else { "missing" }
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
[void]$merged.AppendLine((Write-RunHeader -Mode "prod" -TaskName "Krishna Story Factory MWF" -QueueBefore $queueBefore -QueueAfter "see-after" -ExitCode $ExitCode))
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
$queueAfter = if (Test-Path -LiteralPath $QueuePath) { (Get-FileHash -LiteralPath $QueuePath -Algorithm SHA256).Hash } else { "missing" }
[void]$merged.AppendLine("")
[void]$merged.AppendLine("queue_after=$queueAfter")
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
