param([string]$TaskName = "Krishna Story Factory Daily", [string]$DailyTime = "05:30")

Write-Warning "Deprecated: delegating to install_daily_story_task.ps1."
$Installer = Join-Path $PSScriptRoot "install_daily_story_task.ps1"
& $Installer -TaskName $TaskName -DailyTime $DailyTime
exit $LASTEXITCODE
