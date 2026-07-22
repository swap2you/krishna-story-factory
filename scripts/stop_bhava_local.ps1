param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
)

$ErrorActionPreference = "Stop"
$PidDir = Join-Path $ProjectRoot ".bhava"
foreach ($name in @("api", "web")) {
  $pidFile = Join-Path $PidDir "$name.pid"
  if (-not (Test-Path $pidFile)) { continue }
  $procId = [int](Get-Content $pidFile)
  $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
  if ($proc) {
    Stop-Process -Id $procId -Force
    Write-Output "Stopped $name PID $procId"
  }
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}
Write-Output "Bhāva local processes stopped."
