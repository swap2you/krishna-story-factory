param([string]$TaskName = "Krishna Story Factory Daily", [switch]$StaticOnly)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\run_daily_story_scheduled.ps1") -Raw
$Installer = Get-Content -LiteralPath (Join-Path $ProjectRoot "scripts\install_daily_story_task.ps1") -Raw
$Failures = @()
if ($Runner -notmatch '\.venv\\Scripts\\python\.exe') { $Failures += "runner does not use venv Python" }
if ($Runner -notmatch '--mode prod' -or $Runner -match '--force') { $Failures += "runner command is not safe production command" }
if ($Runner -notmatch 'WHATSAPP_SEND_ENABLED\s*=\s*"false"') { $Failures += "WhatsApp is not disabled" }
if ($Runner -notmatch 'TELEGRAM_SEND_ENABLED\s*=\s*"false"') { $Failures += "Telegram is not disabled" }
if ($Runner -notmatch 'GOOGLE_DRIVE_UPLOAD_ENABLED\s*=\s*"true"') { $Failures += "Drive upload is not enabled" }
if ($Installer -notmatch 'MultipleInstances IgnoreNew') { $Failures += "overlap prevention is missing" }
if ($Installer -notmatch 'RestartCount 2' -or $Installer -notmatch 'Minutes 30') { $Failures += "retry policy is incorrect" }
if (-not $StaticOnly) {
    $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
    $Info = Get-ScheduledTaskInfo -TaskName $TaskName
    if ($Task.State -eq "Disabled") { $Failures += "task is disabled" }
    if ($Task.Actions.Arguments -match '--force') { $Failures += "registered action uses --force" }
    if ($Task.Settings.MultipleInstances -ne "IgnoreNew") { $Failures += "registered task permits overlap" }
    if (-not $Info.NextRunTime) { $Failures += "next run time is missing" }
}
if ($Failures) { throw ($Failures -join "; ") }
Write-Output "Scheduler validation PASS"
if (-not $StaticOnly) { Get-ScheduledTaskInfo -TaskName $TaskName | Select-Object TaskName,NextRunTime,LastRunTime,LastTaskResult }

