# Manual story rebuild wrapper — uses repository venv; never silently adds --force.
[CmdletBinding()]
param(
    [string]$Chapters = "",
    [string]$Chapter = "",
    [string]$Components = "",
    [switch]$DryRun,
    [switch]$LocalOnly,
    [switch]$UploadDrive,
    [switch]$ValidateOnly,
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$script = Join-Path $ProjectRoot "scripts\rebuild_story_packages.py"

if (-not (Test-Path $python)) {
    throw "Repository venv not found at $python"
}
if (-not (Test-Path $script)) {
    throw "Missing rebuild script at $script"
}

$chapterArg = $Chapters
if (-not $chapterArg -and $Chapter) {
    $chapterArg = $Chapter
}
if (-not $chapterArg) {
    throw "Provide -Chapters or -Chapter (e.g. -Chapters 001,002,003,004,005)"
}

$modeCount = @($DryRun.IsPresent, $LocalOnly.IsPresent, $UploadDrive.IsPresent) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
if ($modeCount -ne 1 -and -not $ValidateOnly) {
    throw "Choose exactly one mode: -DryRun, -LocalOnly, or -UploadDrive (or use -ValidateOnly with one mode)."
}
if ($ValidateOnly -and $modeCount -eq 0) {
    $DryRun = $true
}

$argList = @(
    $script,
    "--chapters", $chapterArg
)
if ($Components) {
    $argList += @("--components", $Components)
}
if ($DryRun) { $argList += "--dry-run" }
if ($LocalOnly) { $argList += "--local-only" }
if ($UploadDrive) { $argList += "--upload-drive" }
if ($ValidateOnly) { $argList += "--validate-only" }

# Intentionally never append --force.
Write-Host "Running: $python $($argList -join ' ')"
& $python @argList
exit $LASTEXITCODE
