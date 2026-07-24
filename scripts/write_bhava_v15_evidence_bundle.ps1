param(
  [int]$PlaywrightExitCode = 0,
  [string]$Notes = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$sha = (git rev-parse HEAD).Trim()
$short = $sha.Substring(0, 7)
$dirty = (git status --porcelain)
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
$dir = Join-Path $Root "docs\product\uat\v1.5\runs\$stamp-$short"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$meta = [ordered]@{
  sha = $sha
  short_sha = $short
  dirty_tree = [bool]$dirty
  captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  os = [System.Environment]::OSVersion.VersionString
  node = (node -v)
  python = (& .\.venv\Scripts\python.exe -c "import sys; print(sys.version.split()[0])")
  playwright_exit_code = $PlaywrightExitCode
  notes = $Notes
}
$meta | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dir "run-metadata.json") -Encoding utf8
Write-Output $dir
