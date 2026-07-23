param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot
$PidDir = Join-Path $ProjectRoot ".bhava"
New-Item -ItemType Directory -Force -Path $PidDir | Out-Null

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Missing .venv. Run scripts/bootstrap.ps1 first." }
$nextOk = (Test-Path (Join-Path $ProjectRoot "node_modules\next")) -or (Test-Path (Join-Path $ProjectRoot "apps\web\node_modules\next"))
if (-not $nextOk) { throw "Missing npm install. Run: npm install" }

function Start-LoggedProcess([string]$Name, [string]$File, [string[]]$ArgumentList) {
  $existing = Get-Content (Join-Path $PidDir "$Name.pid") -ErrorAction SilentlyContinue
  if ($existing) {
    $proc = Get-Process -Id ([int]$existing) -ErrorAction SilentlyContinue
    if ($proc) { Write-Output "$Name already running (PID $existing)"; return }
  }
  $out = Join-Path $PidDir "$Name.out.log"
  $err = Join-Path $PidDir "$Name.err.log"
  $p = Start-Process -FilePath $File -ArgumentList $ArgumentList -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err
  Set-Content -Path (Join-Path $PidDir "$Name.pid") -Value $p.Id
  Write-Output "Started $Name PID $($p.Id)"
}

Start-LoggedProcess -Name "api" -File $Python -ArgumentList @(
  "-m", "uvicorn", "bhava_api.main:app", "--host", "127.0.0.1", "--port", "8000", "--app-dir", "apps/api"
)
Start-LoggedProcess -Name "web" -File "npm.cmd" -ArgumentList @("run", "dev", "-w", "@bhava/web")

$deadline = (Get-Date).AddMinutes(2)
do {
  try {
    $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -UseBasicParsing -TimeoutSec 2
    if ($health.StatusCode -eq 200) { break }
  } catch { Start-Sleep -Seconds 2 }
} while ((Get-Date) -lt $deadline)

$deadline = (Get-Date).AddMinutes(3)
do {
  try {
    $web = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -UseBasicParsing -TimeoutSec 2
    if ($web.StatusCode -eq 200) { break }
  } catch { Start-Sleep -Seconds 2 }
} while ((Get-Date) -lt $deadline)

Write-Output "API http://127.0.0.1:8000"
Write-Output "WEB http://localhost:3000"
if (-not $NoBrowser) { Start-Process "http://localhost:3000" }
