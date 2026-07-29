param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
  [string]$InstanceName = "cursor",
  [switch]$AllInstances
)

$ErrorActionPreference = "Stop"

function Stop-Instance([string]$Name) {
  $runtimeFile = Join-Path $ProjectRoot ".bhava\instances\$Name\runtime.json"
  if (-not (Test-Path $runtimeFile)) {
    Write-Output "No runtime.json for instance '$Name'."
    return
  }
  $runtime = Get-Content $runtimeFile -Raw | ConvertFrom-Json
  foreach ($field in @("web_pid", "api_pid")) {
    $procId = [int]($runtime.$field)
    if ($procId -le 0) { continue }
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      # Also stop child npm/node trees when present
      Get-CimInstance Win32_Process -Filter "ParentProcessId=$procId" -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
      Write-Output "Stopped $field PID $procId for '$Name'"
    }
  }
  Write-Output "Stopped instance '$Name' (did not touch unrelated port holders)."
}

if ($AllInstances) {
  $root = Join-Path $ProjectRoot ".bhava\instances"
  if (Test-Path $root) {
    Get-ChildItem $root -Directory | ForEach-Object { Stop-Instance $_.Name }
  }
  # Legacy single-instance PID files
  $legacy = Join-Path $ProjectRoot ".bhava"
  foreach ($name in @("api", "web")) {
    $pidFile = Join-Path $legacy "$name.pid"
    if (-not (Test-Path $pidFile)) { continue }
    $procId = [int](Get-Content $pidFile)
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      Write-Output "Stopped legacy $name PID $procId"
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
  }
} else {
  Stop-Instance $InstanceName
}

Write-Output "Bhāva stop complete."
