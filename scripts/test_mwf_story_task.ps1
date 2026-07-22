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
if ($Installer -notmatch 'PrimaryTime = "10:00"') { $Failures += "primary 10:00 schedule missing" }
if ($Installer -notmatch 'BackupTime = "12:00"') { $Failures += "noon backup schedule missing" }
if ($Installer -notmatch 'StartWhenAvailable = \$false') { $Failures += "StartWhenAvailable must be False" }
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
    if ($Task.Actions.Arguments -match '--force') { $Failures += "registered action uses --force" }
    if ($Task.Settings.MultipleInstances -ne "IgnoreNew") { $Failures += "registered task permits overlap" }
    if ($Task.Settings.StartWhenAvailable -ne $false) { $Failures += "StartWhenAvailable must be False (saw: $($Task.Settings.StartWhenAvailable))" }
    if ($Task.Settings.WakeToRun -eq $true) { $Failures += "WakeToRun must not be True" }

    $triggers = @($Task.Triggers)
    if ($triggers.Count -ne 6) { $Failures += "expected 6 triggers; saw $($triggers.Count)" }

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
    foreach ($needTime in @("10:00", "12:00")) {
        if (-not $times.Contains($needTime)) { $Failures += "missing trigger time: $needTime (saw: $($times -join ', '))" }
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
