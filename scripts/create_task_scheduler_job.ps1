param([string]$TaskName = "Krishna Story Factory MWF", [string]$DailyTime = "06:00", [switch]$Enable)

Write-Warning "Deprecated: use scripts/install_mwf_story_task.ps1. Delegating now."
$Installer = Join-Path $PSScriptRoot "install_mwf_story_task.ps1"
& $Installer -TaskName $TaskName -DailyTime $DailyTime -Enable:$Enable -RemoveLegacyDaily
exit $LASTEXITCODE
