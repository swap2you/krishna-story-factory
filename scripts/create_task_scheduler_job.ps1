param(
    [string]$TaskName = "Krishna Story Factory MWF",
    [string]$PrimaryTime = "10:00",
    [string]$BackupTime = "12:00",
    [switch]$Enable
)

Write-Warning "Deprecated: use scripts/install_mwf_story_task.ps1. Delegating now."
$Installer = Join-Path $PSScriptRoot "install_mwf_story_task.ps1"
& $Installer -TaskName $TaskName -PrimaryTime $PrimaryTime -BackupTime $BackupTime -Enable:$Enable -RemoveLegacyDaily
exit $LASTEXITCODE
