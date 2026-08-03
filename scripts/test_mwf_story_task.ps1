param([string]$TaskName = "Krishna Story Factory MWF", [switch]$StaticOnly)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1") -Raw
$Installer = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\install_mwf_story_task.ps1") -Raw
$Failures = @()

# Runner: .NET Process isolation (no Start-Process / NoNewWindow production path)
if ($Runner -notmatch 'System\.Diagnostics\.Process') { $Failures += "runner must use System.Diagnostics.Process" }
if ($Runner -notmatch 'UseShellExecute\s*=\s*\$false') { $Failures += "runner must set UseShellExecute=false" }
if ($Runner -notmatch 'CreateNoWindow\s*=\s*\$true') { $Failures += "runner must set CreateNoWindow=true" }
if ($Runner -notmatch 'RedirectStandardOutput\s*=\s*\$true') { $Failures += "runner must redirect stdout" }
if ($Runner -notmatch 'RedirectStandardError\s*=\s*\$true') { $Failures += "runner must redirect stderr" }
if ($Runner -notmatch 'ReadToEndAsync') { $Failures += "runner must drain stdout/stderr asynchronously (ReadToEndAsync)" }
if ($Runner -match 'Start-Process') { $Failures += "runner must not use Start-Process in the production path" }
if ($Runner -match 'NoNewWindow') { $Failures += "runner must not use -NoNewWindow" }
if ($Runner -match 'Tee-Object') { $Failures += "runner must not Tee-Object native stderr" }
if ($Runner -notmatch '\.venv\\Scripts\\python\.exe') { $Failures += "runner does not use venv Python" }
if ($Runner -notmatch '"--mode", "prod"' -and $Runner -notmatch '--mode prod') { $Failures += "runner command is not safe production command" }
if ($Runner -match '--force') { $Failures += "runner command must not use --force" }
if ($Runner -notmatch 'WHATSAPP_SEND_ENABLED\s*=\s*"false"') { $Failures += "WhatsApp is not disabled" }
if ($Runner -notmatch 'TELEGRAM_SEND_ENABLED\s*=\s*"false"') { $Failures += "Telegram is not disabled" }
if ($Runner -notmatch 'GOOGLE_DRIVE_UPLOAD_ENABLED\s*=\s*"true"') { $Failures += "Drive upload is not enabled for production" }

# Installer source expectations — safe MWF: 10:00 only, no noon loop, no catch-up.
if ($Installer -notmatch 'MultipleInstances IgnoreNew') { $Failures += "overlap prevention is missing" }
if ($Installer -notmatch 'RestartCount 0') { $Failures += "RestartCount must be 0 (no paid auto-retry loop)" }
if ($Installer -notmatch 'PrimaryTime = "10:00"') { $Failures += "primary 10:00 schedule missing" }
if ($Installer -match 'BackupTime') { $Failures += "noon BackupTime must be removed (no 12:00 retry loop)" }
if ($Installer -match '-At \$BackupTime' -or $Installer -match '12:00') {
    $Failures += "installer must not schedule 12:00 backup triggers"
}
if ($Installer -notmatch 'Hours 4' -and $Installer -notmatch 'PT4H') { $Failures += "installer must set ExecutionTimeLimit to 4 hours (PT4H)" }
if ($Installer -notmatch 'StartWhenAvailable = \$false') { $Failures += "StartWhenAvailable must be false (no immediate catch-up)" }
if ($Installer -match 'StartWhenAvailable = \$true') { $Failures += "StartWhenAvailable must not be true" }
if ($Installer -notmatch 'StopOnIdleEnd = \$false' -and $Installer -notmatch 'DontStopOnIdleEnd') {
    $Failures += "StopOnIdleEnd must be false (DontStopOnIdleEnd / IdleSettings)"
}
if ($Installer -notmatch 'WakeToRun = \$false') { $Failures += "WakeToRun must be False" }
foreach ($day in @("Monday", "Wednesday", "Friday")) {
    if ($Installer -notmatch "-DaysOfWeek $day -At \`\$PrimaryTime" -and $Installer -notmatch "-DaysOfWeek $day") {
        $Failures += "missing weekly day wiring: $day"
    }
}
if ($Installer -notmatch 'Krishna Story Factory MWF') { $Failures += "MWF task name missing from installer" }

if (-not $StaticOnly) {
    $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
    $Info = Get-ScheduledTaskInfo -TaskName $TaskName
    if ($Task.State -notin @("Disabled", "Ready", "Running")) { $Failures += "unexpected task state: $($Task.State)" }

    $action = @($Task.Actions)[0]
    $args = [string]$action.Arguments
    $wd = [string]$action.WorkingDirectory
    $runnerPath = Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1"
    if ($args -match '--force') { $Failures += "registered action uses --force" }
    if ($args -notmatch [regex]::Escape($runnerPath) -and $args -notmatch 'run_daily_story_scheduled\.ps1') {
        $Failures += "registered action is not the current wrapper"
    }
    if ($wd -and ((Resolve-Path $wd).Path -ne (Resolve-Path $ProjectRoot).Path)) {
        $Failures += "registered WorkingDirectory mismatch: $wd"
    }

    if ($Task.Settings.MultipleInstances -ne "IgnoreNew") { $Failures += "registered task permits overlap" }
    if ($Task.Settings.StartWhenAvailable -ne $false) {
        $Failures += "StartWhenAvailable must be False (saw: $($Task.Settings.StartWhenAvailable))"
    }
    if ($Task.Settings.WakeToRun -eq $true) { $Failures += "WakeToRun must not be True" }

    $limit = $Task.Settings.ExecutionTimeLimit
    $limitOk = $false
    if ($limit -is [TimeSpan]) {
        $limitOk = $limit.TotalHours -eq 4
    } else {
        $limitOk = ("$limit" -match 'PT4H' -or "$limit" -eq "04:00:00")
    }
    if (-not $limitOk) { $Failures += "ExecutionTimeLimit must be PT4H (saw: $limit)" }

    $stopIdle = $null
    if ($null -ne $Task.Settings.IdleSettings) {
        $stopIdle = $Task.Settings.IdleSettings.StopOnIdleEnd
    }
    if ($stopIdle -ne $false) { $Failures += "StopOnIdleEnd must be false (saw: $stopIdle)" }

    $restart = $Task.Settings.RestartCount
    if ([int]$restart -ne 0) { $Failures += "RestartCount must be 0 (saw: $restart)" }

    $triggers = @($Task.Triggers)
    if ($triggers.Count -ne 3) { $Failures += "expected 3 triggers (Mon/Wed/Fri 10:00); saw $($triggers.Count)" }

    $dayNames = @{}
    $times = New-Object System.Collections.Generic.HashSet[string]
    foreach ($t in $triggers) {
        $raw = $t.DaysOfWeek
        $daysForTrigger = @()
        if ($null -ne $raw) {
            if ($raw -is [int] -or "$raw" -match '^\d+$') {
                $mask = [int]$raw
                if ($mask -band 2) { $daysForTrigger += "Monday" }
                if ($mask -band 4) { $daysForTrigger += "Tuesday" }
                if ($mask -band 8) { $daysForTrigger += "Wednesday" }
                if ($mask -band 16) { $daysForTrigger += "Thursday" }
                if ($mask -band 32) { $daysForTrigger += "Friday" }
                if ($mask -band 64) { $daysForTrigger += "Saturday" }
                if ($mask -band 1) { $daysForTrigger += "Sunday" }
            } else {
                $daysForTrigger += [string]$raw
            }
        }
        foreach ($d in $daysForTrigger) {
            if ($d -notin @("Monday", "Wednesday", "Friday")) {
                $Failures += "unexpected trigger day: $d"
            }
            $dayNames[$d] = $true
        }
        if ($t.StartBoundary) {
            try {
                $dt = [datetime]::Parse($t.StartBoundary)
                [void]$times.Add($dt.ToString("HH:mm"))
            } catch {
                $Failures += "unparseable StartBoundary: $($t.StartBoundary)"
            }
        }
    }
    foreach ($need in @("Monday", "Wednesday", "Friday")) {
        if (-not $dayNames.ContainsKey($need)) { $Failures += "missing weekly day: $need" }
    }
    if (-not $times.Contains("10:00")) { $Failures += "missing trigger time: 10:00 (saw: $($times -join ', '))" }
    if ($times.Contains("12:00")) { $Failures += "12:00 backup trigger must not be registered" }
    if ($Task.State -ne "Disabled" -and -not $Info.NextRunTime) { $Failures += "next run time is missing" }
    $legacy = Get-ScheduledTask -TaskName "Krishna Story Factory Daily" -ErrorAction SilentlyContinue
    if ($legacy -and $legacy.State -eq "Ready") {
        $Failures += "legacy Daily task is still enabled; only MWF may be active"
    }
}
if ($Failures) { throw ($Failures -join "; ") }
Write-Output "MWF scheduler validation PASS"
if (-not $StaticOnly) {
    Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State
    Get-ScheduledTaskInfo -TaskName $TaskName | Select-Object TaskName, NextRunTime, LastRunTime, LastTaskResult
}
