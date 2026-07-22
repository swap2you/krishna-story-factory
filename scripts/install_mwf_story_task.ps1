param(
    [string]$TaskName = "Krishna Story Factory MWF",
    [string]$PrimaryTime = "10:00",
    [string]$BackupTime = "12:00",
    [switch]$Enable,
    [switch]$RemoveLegacyDaily
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1"
$PowerShell = (Get-Command powershell.exe).Source

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute $PowerShell `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$Runner`" -ProjectRoot `"$ProjectRoot`"" `
    -WorkingDirectory $ProjectRoot

# Six weekly triggers: Mon/Wed/Fri at primary (10:00) and noon backup (12:00).
# StartWhenAvailable remains False so a missed day does not fire on next boot.
$Triggers = @(
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $PrimaryTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $BackupTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At $PrimaryTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At $BackupTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At $PrimaryTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At $BackupTime)
)

$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 60) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 30) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$Settings.StartWhenAvailable = $false
$Settings.WakeToRun = $false

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings `
    -Principal $Principal `
    -Description "Generate and upload the next Krishna Story package Mon/Wed/Fri at $PrimaryTime with $BackupTime backup; same-day guard; WhatsApp/Telegram disabled; Drive enabled." `
    -Force | Out-Null

if ($Enable) {
    Enable-ScheduledTask -TaskName $TaskName | Out-Null
} else {
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
}

if ($RemoveLegacyDaily -or $Enable) {
    $legacy = "Krishna Story Factory Daily"
    $existing = Get-ScheduledTask -TaskName $legacy -ErrorAction SilentlyContinue
    if ($existing) {
        Disable-ScheduledTask -TaskName $legacy -ErrorAction SilentlyContinue | Out-Null
        Unregister-ScheduledTask -TaskName $legacy -Confirm:$false -ErrorAction SilentlyContinue
        Write-Output "Removed legacy task: $legacy"
    }
}

& (Join-Path $ProjectRoot "scripts\test_mwf_story_task.ps1") -TaskName $TaskName
Write-Output "Installed $TaskName (Enabled=$Enable; Primary=$PrimaryTime; Backup=$BackupTime; triggers=6)"
