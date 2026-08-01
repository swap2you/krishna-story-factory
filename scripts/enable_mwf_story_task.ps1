param([string]$TaskName = "Krishna Story Factory MWF")

# Operator enable for the approved MWF scheduler (Mon/Wed/Fri).
# Do not call this during quality-completion releases unless explicitly approved.
# After any install/test, prefer scripts/disable_mwf_story_task.ps1 so the task stays Disabled.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Enable-ScheduledTask -TaskName $TaskName | Out-Null
Write-Output "Enabled scheduled task: $TaskName"
& (Join-Path $ProjectRoot "scripts\show_mwf_story_task.ps1") -TaskName $TaskName
