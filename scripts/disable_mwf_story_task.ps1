param([string]$TaskName = "Krishna Story Factory MWF")

# Disable the MWF scheduler. Safe default for this release: keep Disabled after install/test.
# Do not enable for real production runs until explicit human approval.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Disable-ScheduledTask -TaskName $TaskName | Out-Null
Write-Output "Disabled scheduled task: $TaskName"
& (Join-Path $ProjectRoot "scripts\show_mwf_story_task.ps1") -TaskName $TaskName
