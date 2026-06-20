param(
    [Parameter(Mandatory = $true)]
    [string]$Story,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [switch]$LineArtOnly,
    [switch]$PosterOnly,
    [switch]$GenerateAll,
    [switch]$UseReferences,
    [switch]$NoReferences,
    [switch]$Force,
    [switch]$DryRun
)

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$Args = @(
    (Join-Path $Root "scripts\generate_story_visuals.py"),
    "--story", $Story,
    "--output", $Output
)

if ($LineArtOnly) { $Args += "--line-art-only" }
if ($PosterOnly) { $Args += "--poster-only" }
if ($GenerateAll) { $Args += "--generate-all" }
if ($UseReferences) { $Args += "--use-references" }
if ($NoReferences) { $Args += "--no-references" }
if ($Force) { $Args += "--force" }
if ($DryRun) { $Args += "--dry-run" }

& $Python @Args
exit $LASTEXITCODE
