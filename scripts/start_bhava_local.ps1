param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
  [string]$InstanceName = "cursor",
  [int]$PreferredWebPort = -1,
  [int]$PreferredApiPort = -1,
  [ValidateSet("Development", "Production")]
  [string]$Mode = "Development",
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Missing .venv. Run scripts/bootstrap.ps1 first." }
$nextOk = (Test-Path (Join-Path $ProjectRoot "node_modules\next")) -or (Test-Path (Join-Path $ProjectRoot "apps\web\node_modules\next"))
if (-not $nextOk) { throw "Missing npm install. Run: npm ci" }

$RuntimePy = Join-Path $ProjectRoot "scripts\bhava_runtime.py"
$running = & $Python $RuntimePy running --instance $InstanceName
if ($running -eq "1") {
  $existing = Get-Content (Join-Path $ProjectRoot ".bhava\instances\$InstanceName\runtime.json") -Raw | ConvertFrom-Json
  Write-Output "Instance '$InstanceName' already running."
  Write-Output "WEB $($existing.web_url)"
  Write-Output "API $($existing.api_url)"
  if (-not $NoBrowser) { Start-Process $existing.web_url }
  exit 0
}

$allocArgs = @($RuntimePy, "allocate", "--instance", $InstanceName)
if ($PreferredWebPort -gt 0) { $allocArgs += @("--preferred-web", "$PreferredWebPort") }
if ($PreferredApiPort -gt 0) { $allocArgs += @("--preferred-api", "$PreferredApiPort") }
$allocJson = & $Python @allocArgs
if ($LASTEXITCODE -ne 0) {
  Write-Error $allocJson
  exit $LASTEXITCODE
}
$alloc = $allocJson | ConvertFrom-Json
$webPort = [int]$alloc.web_port
$apiPort = [int]$alloc.api_port
$webUrl = [string]$alloc.web_url
$apiUrl = [string]$alloc.api_url

$instDir = Join-Path $ProjectRoot ".bhava\instances\$InstanceName"
New-Item -ItemType Directory -Force -Path $instDir | Out-Null
$catalogDb = Join-Path $instDir "bhava.sqlite"

# Prefer Start-Process with env vars set in current session, then restore.
$saved = @{
  BHAVA_API_URL = $env:BHAVA_API_URL
  BHAVA_API_ORIGIN = $env:BHAVA_API_ORIGIN
  BHAVA_WEB_URL = $env:BHAVA_WEB_URL
  BHAVA_WEB_ORIGINS = $env:BHAVA_WEB_ORIGINS
  BHAVA_CATALOG_DB = $env:BHAVA_CATALOG_DB
  PORT = $env:PORT
  BHAVA_INSTANCE = $env:BHAVA_INSTANCE
}

$env:BHAVA_API_ORIGIN = $apiUrl
$env:BHAVA_API_URL = "$apiUrl/api/v1"
$env:BHAVA_WEB_URL = $webUrl
$env:BHAVA_WEB_ORIGINS = "http://127.0.0.1:$webPort,http://localhost:$webPort"
$env:BHAVA_CATALOG_DB = $catalogDb
$env:BHAVA_INSTANCE = $InstanceName
$env:PORT = "$webPort"

$apiOut = Join-Path $instDir "api.out.log"
$apiErr = Join-Path $instDir "api.err.log"
$webOut = Join-Path $instDir "web.out.log"
$webErr = Join-Path $instDir "web.err.log"

$apiProc = Start-Process -FilePath $Python -ArgumentList @(
  "-m", "uvicorn", "bhava_api.main:app",
  "--host", "127.0.0.1",
  "--port", "$apiPort",
  "--app-dir", "apps/api"
) -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput $apiOut -RedirectStandardError $apiErr

if ($Mode -eq "Production") {
  Write-Output "Building Next.js for production..."
  npm run build:web
  if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    throw "next build failed"
  }
  $webProc = Start-Process -FilePath "npm.cmd" -ArgumentList @(
    "run", "start", "-w", "@bhava/web", "--", "-p", "$webPort", "-H", "127.0.0.1"
  ) -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput $webOut -RedirectStandardError $webErr
} else {
  $webProc = Start-Process -FilePath "npm.cmd" -ArgumentList @(
    "run", "dev", "-w", "@bhava/web", "--", "-p", "$webPort", "-H", "127.0.0.1"
  ) -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput $webOut -RedirectStandardError $webErr
}

$runtime = [ordered]@{
  instance_name = $InstanceName
  web_port = $webPort
  api_port = $apiPort
  web_url = $webUrl
  api_url = $apiUrl
  web_pid = $webProc.Id
  api_pid = $apiProc.Id
  mode = $Mode.ToLowerInvariant()
  started_at = (Get-Date).ToUniversalTime().ToString("o")
  preferred_web_port = $alloc.preferred_web_port
  preferred_api_port = $alloc.preferred_api_port
  collision = [bool]$alloc.collision
  catalog_db = $catalogDb
}
$runtimePath = Join-Path $instDir "runtime.json"
($runtime | ConvertTo-Json -Depth 5) | Set-Content -Path $runtimePath -Encoding utf8

& $Python $RuntimePy wait --url "$apiUrl/api/v1/health" --timeout 180
if ($LASTEXITCODE -ne 0) { throw "API health check failed for $apiUrl" }
& $Python $RuntimePy wait --url $webUrl --timeout 240
if ($LASTEXITCODE -ne 0) { throw "Web health check failed for $webUrl" }

# Restore prior env
foreach ($key in $saved.Keys) {
  if ($null -eq $saved[$key]) { Remove-Item "Env:$key" -ErrorAction SilentlyContinue }
  else { Set-Item "Env:$key" $saved[$key] }
}

Write-Output ""
Write-Output "Bhāva instance '$InstanceName' is ready."
Write-Output "WEB  $webUrl"
Write-Output "API  $apiUrl"
Write-Output "Runtime file: $runtimePath"
if ($alloc.collision) {
  Write-Output "Note: preferred ports were occupied; selected free ports above without killing other processes."
}
if (-not $NoBrowser) { Start-Process $webUrl }
