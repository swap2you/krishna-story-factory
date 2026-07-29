# Scheduled production runner - isolated .NET Process launch (CreateNoWindow; console-detached).
# Modes:
#   .\scripts\run_daily_story_scheduled.ps1
#   .\scripts\run_daily_story_scheduled.ps1 -ValidateScheduler
#   .\scripts\run_daily_story_scheduled.ps1 -SimulateProduction
param(
    [string]$ProjectRoot = "",
    [switch]$ValidateScheduler,
    [switch]$SimulateProduction
)

$ErrorActionPreference = "Stop"
$WrapperVersion = "v1.7.0-dotnet-process"
if (-not $ProjectRoot) { $ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EntryPoint = Join-Path $ProjectRoot "run_daily_story.py"
$LogDir = Join-Path $ProjectRoot "logs\scheduler"
$History = Join-Path $ProjectRoot "tracking\run_history.csv"
$QueuePath = Join-Path $ProjectRoot "tracking\queue_state.csv"
$LockPath = Join-Path $ProjectRoot ".pipeline.lock"
$ValidateLockPath = Join-Path $ProjectRoot ".pipeline.validate.lock"
$HealthPath = Join-Path $ProjectRoot "tracking\scheduler_health.json"

function Get-Sha256Hex {
    param([string]$LiteralPath)
    if (-not (Test-Path -LiteralPath $LiteralPath)) { return "missing" }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        try {
            $hash = $sha.ComputeHash($stream)
            return ([BitConverter]::ToString($hash) -replace "-", "").ToUpperInvariant()
        } finally {
            $stream.Dispose()
        }
    } finally {
        $sha.Dispose()
    }
}

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
    @(
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
        "wrapper_pid=$PID"
    ) -join "`n"
}

function Write-SchedulerHealth {
    param([hashtable]$Fields)
    $Fields["updated_at"] = (Get-Date).ToUniversalTime().ToString("o")
    ($Fields | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $HealthPath -Encoding utf8
}

function Invoke-IsolatedPython {
    param(
        [string[]]$ArgumentList,
        [string]$StdOutLog,
        [string]$StdErrLog,
        [string]$RunId,
        [string]$ModeLabel,
        [string]$StoryHint = ""
    )

    $gitSha = Get-GitSha
    $env:BHAVA_WRAPPER_PID = "$PID"
    $env:BHAVA_GIT_SHA = $gitSha
    $env:BHAVA_RUN_ID = $RunId

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Python
    $psi.WorkingDirectory = $ProjectRoot
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.Arguments = ($ArgumentList | ForEach-Object {
        if ($_ -match '[\s"]') { '"{0}"' -f ($_ -replace '\\', '\\' -replace '"', '\"') } else { $_ }
    }) -join " "

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    if (-not $proc.Start()) { throw "Failed to start Python process" }
    $childStart = Get-Date
    $script:lastOutput = $childStart

    # Async drain both streams before waiting (avoids pipe deadlocks; no ScriptBlock callbacks).
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()

    $heartbeatSeconds = 45
    while (-not $proc.HasExited) {
        Write-SchedulerHealth @{
            run_id = $RunId
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            wrapper_pid = $PID
            child_pid = $proc.Id
            elapsed_seconds = [int]((Get-Date) - $childStart).TotalSeconds
            current_stage = $ModeLabel
            last_output_time = $script:lastOutput.ToUniversalTime().ToString("o")
            queue_story = $StoryHint
            mode = $ModeLabel
            git_sha = $gitSha
            wrapper_version = $WrapperVersion
        }
        $null = $proc.WaitForExit($heartbeatSeconds * 1000)
    }
    $null = $proc.WaitForExit(5000)
    $childExit = [int]$proc.ExitCode
    $childEnd = Get-Date
    $stdoutText = $outTask.Result
    $stderrText = $errTask.Result
    $script:lastOutput = Get-Date
    Set-Content -LiteralPath $StdOutLog -Value $stdoutText -Encoding utf8
    Set-Content -LiteralPath $StdErrLog -Value $stderrText -Encoding utf8

    Write-SchedulerHealth @{
        run_id = $RunId
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        wrapper_pid = $PID
        child_pid = $proc.Id
        child_start = $childStart.ToUniversalTime().ToString("o")
        child_exit = $childEnd.ToUniversalTime().ToString("o")
        elapsed_seconds = [int]($childEnd - $childStart).TotalSeconds
        current_stage = "exited"
        last_output_time = $script:lastOutput.ToUniversalTime().ToString("o")
        queue_story = $StoryHint
        mode = $ModeLabel
        git_sha = $gitSha
        wrapper_version = $WrapperVersion
        child_exit_code = $childExit
    }

    return @{
        ExitCode = $childExit
        ChildPid = $proc.Id
        StdOut = $stdoutText
        StdErr = $stderrText
        ChildStart = $childStart
        ChildEnd = $childEnd
    }
}

# Avoid converting native stderr into terminating errors.
$PSDefaultParameterValues['*:ErrorAction'] = 'Continue'
trap {
    try {
        Write-SchedulerHealth @{
            run_id = "trap"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            wrapper_pid = $PID
            current_stage = "trap"
            error = $_.Exception.Message
            wrapper_version = $WrapperVersion
        }
    } catch { }
    break
}

if (-not (Test-Path -LiteralPath $Python)) { throw "Virtual-environment Python not found: $Python" }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $HealthPath) | Out-Null

# ---------- ValidateScheduler ----------
if ($ValidateScheduler) {
    $Started = Get-Date
    $Stamp = $Started.ToString("yyyyMMdd_HHmmss")
    $Log = Join-Path $LogDir ("validate_{0}.log" -f $Stamp)
    $queueBefore = if (Test-Path -LiteralPath $QueuePath) { (Get-Sha256Hex -LiteralPath $QueuePath) } else { "missing" }
    $failures = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $EntryPoint)) { $failures.Add("missing_entry_point") }
    if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "krishna_story_factory\stage_state.py"))) { $failures.Add("missing_stage_state") }
    if (-not (Test-Path -LiteralPath $QueuePath)) { $failures.Add("missing_queue") }

    $queueProbe = & $Python -c "from pathlib import Path; import csv; p=Path(r'$QueuePath'); rows=list(csv.DictReader(p.open(encoding='utf-8-sig'))); print(len(rows)); print(next((r['status'] for r in rows if str(r.get('chapter_no','')).zfill(3)=='009'),'missing'))"
    if ($LASTEXITCODE -ne 0) { $failures.Add("queue_read_failed") }

    $lockOwned = $false
    try {
        if (Test-Path -LiteralPath $ValidateLockPath) {
            $failures.Add("validate_lock_already_present")
        } else {
            $payload = @{
                run_id = "validate-$PID"
                host = $env:COMPUTERNAME
                wrapper_pid = $PID
                child_pid = $null
                created_at = (Get-Date).ToUniversalTime().ToString("o")
                heartbeat_at = (Get-Date).ToUniversalTime().ToString("o")
                git_sha = Get-GitSha
                story_no = ""
                mode = "validate"
            } | ConvertTo-Json -Depth 4
            Set-Content -LiteralPath $ValidateLockPath -Value $payload -Encoding utf8
            $lockOwned = $true
        }
    } catch {
        $failures.Add("lock_acquire_failed")
    } finally {
        if ($lockOwned -and (Test-Path -LiteralPath $ValidateLockPath)) {
            Remove-Item -LiteralPath $ValidateLockPath -Force -ErrorAction SilentlyContinue
        }
    }

    $stageProbe = & $Python -c "import sys; sys.path.insert(0, r'$ProjectRoot'); from krishna_story_factory import stage_state; print('stage_state_ok')"
    if ($LASTEXITCODE -ne 0) { $failures.Add("stage_state_import_failed") }

    # Prove .NET process construction without providers.
    $simOut = Join-Path $LogDir ("validate_proc_{0}.stdout.log" -f $Stamp)
    $simErr = Join-Path $LogDir ("validate_proc_{0}.stderr.log" -f $Stamp)
    try {
        $probe = Invoke-IsolatedPython -ArgumentList @("-c", "print('process_ok')") -StdOutLog $simOut -StdErrLog $simErr -RunId ("validate-proc-$PID") -ModeLabel "validate-process"
        if ($probe.ExitCode -ne 0) { $failures.Add("process_probe_failed") }
        if ($probe.StdOut -notmatch "process_ok") { $failures.Add("process_probe_output_missing") }
    } catch {
        $failures.Add("process_probe_exception")
    }

    $driveConfigured = [bool]$env:GOOGLE_DRIVE_UPLOAD_ENABLED
    $queueAfter = if (Test-Path -LiteralPath $QueuePath) { (Get-Sha256Hex -LiteralPath $QueuePath) } else { "missing" }
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

# ---------- SimulateProduction / Prod ----------
Get-ChildItem -LiteralPath $LogDir -Filter "daily_*.log" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -Skip 30 | Remove-Item -Force -ErrorAction SilentlyContinue

$Started = Get-Date
$Stamp = $Started.ToString("yyyyMMdd_HHmmss")
$ModeName = if ($SimulateProduction) { "simulate-production" } else { "prod" }
$Log = Join-Path $LogDir ("{0}_{1}.log" -f $(if ($SimulateProduction) { "simulate" } else { "daily" }), $Stamp)
$StdOutLog = Join-Path $LogDir ("{0}_{1}.stdout.log" -f $(if ($SimulateProduction) { "simulate" } else { "daily" }), $Stamp)
$StdErrLog = Join-Path $LogDir ("{0}_{1}.stderr.log" -f $(if ($SimulateProduction) { "simulate" } else { "daily" }), $Stamp)
$RunId = "{0}-{1}" -f $ModeName, $Stamp

if (-not $SimulateProduction) {
    $env:WHATSAPP_SEND_ENABLED = "false"
    $env:TELEGRAM_SEND_ENABLED = "false"
    $env:GOOGLE_DRIVE_UPLOAD_ENABLED = "true"
}

$ExitCode = 1
$queueBefore = if (Test-Path -LiteralPath $QueuePath) { (Get-Sha256Hex -LiteralPath $QueuePath) } else { "missing" }
$result = $null

try {
    $argList = if ($SimulateProduction) {
        @($EntryPoint, "--scheduler-simulate")
    } else {
        @($EntryPoint, "--mode", "prod")
    }
    $result = Invoke-IsolatedPython -ArgumentList $argList -StdOutLog $StdOutLog -StdErrLog $StdErrLog -RunId $RunId -ModeLabel $ModeName -StoryHint "auto"
    $ExitCode = [int]$result.ExitCode
} catch {
    $_ | Out-String | Set-Content -LiteralPath $Log -Encoding utf8
    $ExitCode = 1
} finally {
    # Never leave validate lock; prod lock is owned by Python child and released there.
    if (Test-Path -LiteralPath $ValidateLockPath) {
        Remove-Item -LiteralPath $ValidateLockPath -Force -ErrorAction SilentlyContinue
    }
}

$merged = New-Object System.Text.StringBuilder
[void]$merged.AppendLine((Write-RunHeader -Mode $ModeName -TaskName "Krishna Story Factory MWF" -QueueBefore $queueBefore -QueueAfter "see-after" -ExitCode $ExitCode -ProviderCalls $(if ($SimulateProduction) { "0" } else { "see-log" }) -DriveActions $(if ($SimulateProduction) { "none" } else { "see-log" })))
if ($null -ne $result) {
    [void]$merged.AppendLine("child_pid=$($result.ChildPid)")
    [void]$merged.AppendLine("child_start=$($result.ChildStart.ToString('o'))")
    [void]$merged.AppendLine("child_exit=$($result.ChildEnd.ToString('o'))")
}
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
$queueAfter = if (Test-Path -LiteralPath $QueuePath) { (Get-Sha256Hex -LiteralPath $QueuePath) } else { "missing" }
[void]$merged.AppendLine("")
[void]$merged.AppendLine("queue_after=$queueAfter")
if ($SimulateProduction -and $queueBefore -ne $queueAfter) {
    $ExitCode = 1
    [void]$merged.AppendLine("failures=queue_mutated")
}
Set-Content -LiteralPath $Log -Value $merged.ToString() -Encoding utf8
Remove-Item -LiteralPath $StdOutLog, $StdErrLog -Force -ErrorAction SilentlyContinue

$Completed = Get-Date
$Detail = (Get-Content -LiteralPath $Log -Raw -ErrorAction SilentlyContinue)
if ($Detail -and $Detail.Length -gt 1000) { $Detail = $Detail.Substring($Detail.Length - 1000) }
$Row = [pscustomobject]@{
    started_at = $Started.ToString("o"); completed_at = $Completed.ToString("o")
    status = $(
        if ($SimulateProduction) {
            if ($ExitCode -eq 0) { "SIMULATE_SUCCESS" } else { "SIMULATE_FAILED" }
        } elseif ($ExitCode -eq 0) {
            "SUCCESS"
        } else {
            "FAILED"
        }
    )
    chapter_no = ""; slug = ""; detail = $Detail; exit_code = [string]$ExitCode
}
if (-not (Test-Path -LiteralPath $History)) {
    $Row | Export-Csv -LiteralPath $History -NoTypeInformation
} else {
    $Row | Export-Csv -LiteralPath $History -NoTypeInformation -Append
}
exit $ExitCode

