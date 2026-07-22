param([string]$TaskName = "Krishna Story Factory MWF", [switch]$StaticOnly)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1") -Raw
$Installer = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\install_mwf_story_task.ps1") -Raw
$Failures = @()
if ($Runner -notmatch '\.venv\\Scripts\\python\.exe') { $Failures += "runner does not use venv Python" }
if ($Runner -notmatch '--mode prod' -or $Runner -match '--force') { $Failures += "runner command is not safe production command" }
if ($Runner -notmatch 'WHATSAPP_SEND_ENABLED\s*=\s*"false"') { $Failures += "WhatsApp is not disabled" }
if ($Runner -notmatch 'TELEGRAM_SEND_ENABLED\s*=\s*"false"') { $Failures += "Telegram is not disabled" }
if ($Runner -notmatch 'GOOGLE_DRIVE_UPLOAD_ENABLED\s*=\s*"true"') { $Failures += "Drive upload is not enabled" }
if ($Installer -notmatch 'MultipleInstances IgnoreNew') { $Failures += "overlap prevention is missing" }
if ($Installer -notmatch 'RestartCount 2' -or $Installer -notmatch 'Minutes 30') { $Failures += "retry policy is incorrect" }
if ($Installer -notmatch 'Monday,Wednesday,Friday' -and $Installer -notmatch 'DaysOfWeek Monday') {
    $Failures += "MWF weekly days are missing"
}
if ($Installer -notmatch 'Krishna Story Factory MWF') { $Failures += "MWF task name missing from installer" }
if (-not $StaticOnly) {
    $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
    $Info = Get-ScheduledTaskInfo -TaskName $TaskName
    if ($Task.State -notin @("Disabled", "Ready", "Running")) { $Failures += "unexpected task state: $($Task.State)" }
    if ($Task.Actions.Arguments -match '--force') { $Failures += "registered action uses --force" }
    if ($Task.Settings.MultipleInstances -ne "IgnoreNew") { $Failures += "registered task permits overlap" }
    $days = @()
    foreach ($t in @($Task.Triggers)) {
        $raw = $t.DaysOfWeek
        if ($null -eq $raw) { continue }
        # CIM may return a bitmask (Mon=2,Tue=4,Wed=8,Thu=16,Fri=32) or day names.
        if ($raw -is [int] -or "$raw" -match '^\d+$') {
            $mask = [int]$raw
            if ($mask -band 2) { $days += "Monday" }
            if ($mask -band 4) { $days += "Tuesday" }
            if ($mask -band 8) { $days += "Wednesday" }
            if ($mask -band 16) { $days += "Thursday" }
            if ($mask -band 32) { $days += "Friday" }
            if ($mask -band 64) { $days += "Saturday" }
            if ($mask -band 1) { $days += "Sunday" }
        } else {
            $days += [string]$raw
        }
    }
    $joined = ($days -join " ")
    foreach ($need in @("Monday", "Wednesday", "Friday")) {
        if ($joined -notmatch $need) { $Failures += "missing weekly day: $need (saw: $joined)" }
    }
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
