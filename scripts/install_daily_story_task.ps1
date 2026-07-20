param([string]$TaskName = "Krishna Story Factory Daily", [string]$DailyTime = "05:30")

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1"
$PowerShell = (Get-Command powershell.exe).Source

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
$Action = New-ScheduledTaskAction -Execute $PowerShell `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$Runner`" -ProjectRoot `"$ProjectRoot`"" `
    -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $DailyTime
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 60) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 30) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings `
    -Principal $Principal -Description "Generate and upload the next Krishna Story package; delivery senders disabled." -Force | Out-Null
# Leave disabled by default; enable manually after validating a prod run.
Disable-ScheduledTask -TaskName $TaskName | Out-Null
& (Join-Path $ProjectRoot "scripts\test_daily_story_task.ps1") -TaskName $TaskName

