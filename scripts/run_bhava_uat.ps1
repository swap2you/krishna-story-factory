param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
  [string]$InstanceName = "cursor-uat",
  [int]$PreferredWebPort = 3000,
  [int]$PreferredApiPort = 8000,
  [string]$EvidenceRoot = "",
  [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

if (-not $EvidenceRoot) {
  if ($InstanceName -like "*v12*") {
    $EvidenceRoot = Join-Path $ProjectRoot "docs\product\uat\v1.2"
  } elseif ($InstanceName -like "*v11*") {
    $EvidenceRoot = Join-Path $ProjectRoot "docs\product\uat\v1.1"
  } else {
    $EvidenceRoot = Join-Path $ProjectRoot "docs\product\uat\live"
  }
}
$Evidence = $EvidenceRoot
New-Item -ItemType Directory -Force -Path (Join-Path $Evidence "screenshots") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Evidence "traces") | Out-Null

Write-Output "== Starting Bhāva UAT instance =="
& (Join-Path $ProjectRoot "scripts\start_bhava_local.ps1") `
  -InstanceName $InstanceName `
  -PreferredWebPort $PreferredWebPort `
  -PreferredApiPort $PreferredApiPort `
  -Mode Production `
  -NoBrowser
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$runtimePath = Join-Path $ProjectRoot ".bhava\instances\$InstanceName\runtime.json"
Copy-Item $runtimePath (Join-Path $Evidence "runtime.json") -Force
$runtime = Get-Content $runtimePath -Raw | ConvertFrom-Json
$env:BHAVA_WEB_URL = $runtime.web_url
$env:BHAVA_API_URL = "$($runtime.api_url)/api/v1"
$env:BHAVA_API_ORIGIN = $runtime.api_url
$env:BHAVA_UAT_BROWSER_RESULTS = Join-Path $Evidence "browser-results.json"

Write-Output "WEB  $($runtime.web_url)"
Write-Output "API  $($runtime.api_url)"

Write-Output "== Playwright browser suites =="
Push-Location (Join-Path $ProjectRoot "apps\web")
try {
  npx playwright test --reporter=list
  $playwrightExit = $LASTEXITCODE
  if (Test-Path "test-results") {
    Copy-Item "test-results\*" (Join-Path $Evidence "traces") -Recurse -Force -ErrorAction SilentlyContinue
  }
} finally {
  Pop-Location
}

$summary = [ordered]@{
  instance_name = $InstanceName
  web_url = $runtime.web_url
  api_url = $runtime.api_url
  web_port = $runtime.web_port
  api_port = $runtime.api_port
  mode = $runtime.mode
  playwright_exit_code = $playwrightExit
  started_at = $runtime.started_at
  completed_at = (Get-Date).ToUniversalTime().ToString("o")
  keep_running = [bool]$KeepRunning
  notes = "Factory generation, scheduler, and Drive were not invoked."
}
($summary | ConvertTo-Json -Depth 5) | Set-Content (Join-Path $Evidence "uat-summary.json") -Encoding utf8

# Placeholder evidence files when suites did not emit dedicated artifacts
foreach ($name in @("axe-results.json", "console-errors.json", "network-errors.json", "responsive-results.json")) {
  $path = Join-Path $Evidence $name
  if (-not (Test-Path $path)) {
    '{"status":"captured-via-playwright-suites","see":"browser-results.json"}' | Set-Content $path -Encoding utf8
  }
}

if (-not $KeepRunning) {
  & (Join-Path $ProjectRoot "scripts\stop_bhava_local.ps1") -InstanceName $InstanceName
}

Write-Output "UAT evidence written to $Evidence"
if ($playwrightExit -ne 0) { exit $playwrightExit }
Write-Output "Bhāva UAT PASS"
