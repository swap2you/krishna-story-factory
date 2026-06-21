param([string]$TaskName = "Krishna Story Factory Daily")
$ErrorActionPreference = "Stop"
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Output "Removed scheduled task: $TaskName"

