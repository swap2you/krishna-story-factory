<#
.SYNOPSIS
  Create exactly one next pending Bhāva story via the canonical production path.

.DESCRIPTION
  Permanent "Create next story" orchestration (Phase 9).

  Governed sequence (PERMANENT_STORY_CREATION_STANDARD / release Phase 9):
    1. source boundary
    2. story V2 generation
    3. copyright / content QA
    4. pronunciation scan
    5. TTS sample QA          ← gated when AUDIO_SAMPLE_FIRST_REQUIRED=true
                               (see krishna_story_factory/audio/sample_first_gate.py)
    6. full narration once
    7. audio QA
    8. visual brief → poster / coloring QA
    9. activity / PDF QA
   10. exact-eight package
   11. derived web assets     ← post-success hook below
   12. package-to-tabs tests  ← run separately: pytest tests/portal/test_package_to_tabs_contract.py
   13. atomic promote
   14. Drive upload / readback
   15. queue advance
   16. evidence report

  This script processes exactly ONE pending story (run_daily_story.py --mode prod).
  It does not generate a second story. Partial failure leaves the queue pending.

  Pipeline lock: acquired inside krishna_story_factory.pipeline.run_daily_story
  via acquire_pipeline_lock (.pipeline.lock). This wrapper refuses to start if a
  live lock file is already present (stale reclaim is handled by the pipeline).
#>
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$RunProd = Join-Path $ProjectRoot "scripts\run_prod.ps1"
$LockPath = Join-Path $ProjectRoot ".pipeline.lock"
$BuildWebAssets = Join-Path $ProjectRoot "scripts\build_bhava_web_assets.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Project venv Python not found: $Python — run scripts/bootstrap.ps1 first."
}
if (-not (Test-Path -LiteralPath $RunProd)) {
    throw "Missing canonical prod wrapper: $RunProd"
}

Write-Output "=== create-next-bhava-story ==="
Write-Output "Processes exactly one pending story via run_daily_story.py --mode prod."
Write-Output "ProjectRoot=$ProjectRoot"

# Document / soft-gate existing pipeline lock (pipeline also acquires exclusively).
if (Test-Path -LiteralPath $LockPath) {
    Write-Output "WARNING: .pipeline.lock already present — another run may be active."
    Write-Output "Lock contents:"
    Get-Content -LiteralPath $LockPath -ErrorAction SilentlyContinue | ForEach-Object { Write-Output "  $_" }
    throw "Refusing to start while .pipeline.lock exists. Wait for the other run or reclaim a stale lock via the pipeline."
}

Write-Output "Invoking canonical production path: scripts/run_prod.ps1"
& $RunProd @RemainingArgs
$exitCode = $LASTEXITCODE
if ($null -eq $exitCode) { $exitCode = 1 }

if ($exitCode -ne 0) {
    Write-Output "Production path FAILED (exit=$exitCode). Queue must remain pending on partial failure."
    exit $exitCode
}

Write-Output "Production path returned success (exit=0)."

# Post-success hook: rebuild derived web-assets for the story that just completed,
# when chapter_no can be inferred from the latest run history / queue.
$storyNo = $null
try {
    $storyNo = & $Python -c @"
from pathlib import Path
import csv, json
root = Path(r'$ProjectRoot')
history = root / 'tracking' / 'run_history.csv'
if history.is_file():
    rows = list(csv.DictReader(history.open(encoding='utf-8-sig')))
    for row in reversed(rows):
        status = (row.get('status') or '').strip().upper()
        chapter = (row.get('chapter_no') or '').strip().zfill(3)
        if status == 'SUCCESS' and chapter and chapter != '000':
            print(chapter)
            break
"@
    if ($LASTEXITCODE -ne 0) { $storyNo = $null }
    $storyNo = ("$storyNo").Trim()
    if (-not $storyNo) { $storyNo = $null }
} catch {
    $storyNo = $null
}

if ($storyNo) {
    Write-Output "Post-success web-assets hook for story $storyNo (build_bhava_web_assets)."
    $env:PYTHONPATH = (Join-Path $ProjectRoot "apps\api")
    & $Python $BuildWebAssets --story-no $storyNo
    if ($LASTEXITCODE -ne 0) {
        Write-Output "WARNING: web-assets build failed for $storyNo (exit=$LASTEXITCODE)."
        Write-Output "Package may exist; re-run: PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py --story-no $storyNo"
        exit $LASTEXITCODE
    }
    Write-Output "Web-assets built for story $storyNo."
} else {
    Write-Output "NOTE: Could not infer completed chapter_no for web-assets hook; skip build."
    Write-Output "Run manually: PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py --story-no NNN"
}

# Thin stubs for gates not yet fully wired into the prod path:
# - package-to-tabs contract: pytest tests/portal/test_package_to_tabs_contract.py
# - sample-first TTS: AUDIO_SAMPLE_FIRST_REQUIRED (default off)
Write-Output "Optional follow-ups: package-to-tabs pytest; sample-first gate when AUDIO_SAMPLE_FIRST_REQUIRED=true."
Write-Output "=== create-next-bhava-story complete ==="
exit 0
