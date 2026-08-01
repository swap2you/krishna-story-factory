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
    5. TTS sample QA          ← FAIL-CLOSED (AUDIO_SAMPLE_FIRST_REQUIRED=1 forced)
                               Durable pass: work/.../audio_sample_pass.json bound to
                               provider/model/voice/settings_hash/narration_source_sha.
                               Full narration is blocked without a valid PASS.
                               See krishna_story_factory/audio/sample_first_gate.py
    6. full narration once
    7. audio QA
    8. visual brief → poster / coloring QA
    9. activity / PDF QA
   10. exact-eight package
   11. derived web assets + package-to-tabs UI contract
       ← FAIL-CLOSED inside pipeline before Drive upload / queue advance
         (BHAVA_WEB_ASSETS_UI_GATE=1; requires PYTHONPATH=apps/api)
   12. atomic promote
   13. Drive upload / readback
   14. queue advance
   15. evidence report

  This script processes exactly ONE pending story (run_daily_story.py --mode prod).
  It does not generate a second story. Partial failure leaves the queue pending.

  Sample-first opt-out (AUDIO_SAMPLE_FIRST_REQUIRED=0) is for legacy rebuild tools
  only — this create-next script always forces sample-first ON.

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

# Phase 9: force fail-closed sample-first TTS (not optional on create-next).
$env:AUDIO_SAMPLE_FIRST_REQUIRED = "1"
# Phase 9: force web-assets/UI contract before Drive upload / queue advance.
$env:BHAVA_WEB_ASSETS_UI_GATE = "1"
# Builder import path for in-pipeline web-assets gate.
$env:PYTHONPATH = (Join-Path $ProjectRoot "apps\api")
Write-Output "AUDIO_SAMPLE_FIRST_REQUIRED=$($env:AUDIO_SAMPLE_FIRST_REQUIRED) (forced ON — sample PASS required before full TTS)."
Write-Output "BHAVA_WEB_ASSETS_UI_GATE=$($env:BHAVA_WEB_ASSETS_UI_GATE) (forced ON — UI contract before Drive/queue)."
Write-Output "PYTHONPATH=$($env:PYTHONPATH)"

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
    Write-Output "Drive upload and queue advance are blocked when package, sample-first, or web-assets/UI gates fail."
    exit $exitCode
}

Write-Output "Production path returned success (exit=0)."

# Post-success verify: rebuild derived web-assets for the story that just completed
# (idempotent; pipeline already gated the UI contract before Drive/queue).
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
    Write-Output "Post-success web-assets verify/rebuild for story $storyNo (build_bhava_web_assets)."
    $env:PYTHONPATH = (Join-Path $ProjectRoot "apps\api")
    & $Python $BuildWebAssets --story-no $storyNo
    if ($LASTEXITCODE -ne 0) {
        Write-Output "FAIL: web-assets rebuild failed for $storyNo (exit=$LASTEXITCODE)."
        Write-Output "Package/Drive may already be committed; investigate before the next create-next run."
        Write-Output "Re-run: PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py --story-no $storyNo"
        exit $LASTEXITCODE
    }
    Write-Output "Web-assets verified for story $storyNo."
} else {
    Write-Output "NOTE: Could not infer completed chapter_no for web-assets verify; skip rebuild."
    Write-Output "Run manually: PYTHONPATH=apps/api python scripts/build_bhava_web_assets.py --story-no NNN"
}

Write-Output "Optional follow-up: pytest tests/portal/test_package_to_tabs_contract.py"
Write-Output "=== create-next-bhava-story complete ==="
exit 0
