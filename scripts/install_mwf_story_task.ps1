param(
    [string]$TaskName = "Krishna Story Factory MWF",
    [string]$PrimaryTime = "10:00",
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

# Mon/Wed/Fri at primary (10:00) only — no noon backup retry loop.
# StartWhenAvailable=false so enabling does not immediately catch up a missed window.
# WakeToRun=false: do not wake the PC for generation.
$Triggers = @(
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $PrimaryTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At $PrimaryTime),
    (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At $PrimaryTime)
)

$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4) -RestartCount 0 `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DontStopOnIdleEnd
$Settings.StartWhenAvailable = $false
$Settings.WakeToRun = $false
if ($null -ne $Settings.IdleSettings) {
    $Settings.IdleSettings.StopOnIdleEnd = $false
}

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings `
    -Principal $Principal `
    -Description "Generate and upload the next Krishna Story package Mon/Wed/Fri at $PrimaryTime only; no noon backup; no StartWhenAvailable catch-up; same-day guard; WhatsApp/Telegram disabled; Drive enabled." `
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
Write-Output "Installed $TaskName (Enabled=$Enable; Primary=$PrimaryTime; triggers=3 Mon/Wed/Fri; RestartCount=0; StartWhenAvailable=false; ExecutionTimeLimit=PT4H)"
