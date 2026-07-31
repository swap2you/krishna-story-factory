<#
.SYNOPSIS
  Safe Bhāva release operator entry point (staging gates before production).

.DESCRIPTION
  Never force-pushes, never enables the scheduler, never runs paid generation,
  never prints secrets, and never publishes Story 010 unless the content tag
  and public max are explicitly approved elsewhere.

.EXAMPLE
  .\scripts\release-bhava.ps1 -Status

.EXAMPLE
  .\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-009-v1 -DryRun

.EXAMPLE
  .\scripts\release-bhava.ps1 -Rollback -Environment staging -ConfirmRollback
#>
[CmdletBinding(DefaultParameterSetName = "Release")]
param(
  [Parameter(ParameterSetName = "Release")]
  [string]$ContentReleaseTag = "bhava-content-001-009-v1",

  [Parameter(ParameterSetName = "Release")]
  [int]$PublicStoryMax = 9,

  [Parameter(ParameterSetName = "Release")]
  [switch]$DryRun,

  [Parameter(ParameterSetName = "Release")]
  [switch]$PromoteToProduction,

  [Parameter(ParameterSetName = "Status")]
  [switch]$Status,

  [Parameter(ParameterSetName = "Rollback")]
  [switch]$Rollback,

  [Parameter(ParameterSetName = "Rollback")]
  [ValidateSet("staging", "production")]
  [string]$Environment = "staging",

  [Parameter(ParameterSetName = "Rollback")]
  [switch]$ConfirmRollback,

  [string]$RepoRoot = ""
)

if (-not $RepoRoot) {
  if ($PSScriptRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
  } else {
    $RepoRoot = (Resolve-Path (Join-Path $PWD ".")).Path
  }
}

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
  Write-Host "==> $Message"
}

function Assert-NoSecretsInOutput([string]$Text) {
  if ($Text -match "(?i)(BEGIN (RSA |OPENSSH )?PRIVATE KEY|OPENAI_API_KEY|ELEVENLABS_API_KEY|STAGING_BASIC_AUTH_HASH=)") {
    throw "Refusing to continue: secret-like material detected in command output."
  }
}

function Get-Git([string[]]$GitArgs) {
  Push-Location $RepoRoot
  try {
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) { throw "git $($GitArgs -join ' ') failed ($LASTEXITCODE)" }
  } finally {
    Pop-Location
  }
}

function Show-Status {
  Write-Step "Repository status"
  Get-Git @("fetch", "--all", "--prune") | Out-Null
  $branch = (Get-Git @("branch", "--show-current") | Out-String).Trim()
  $main = (Get-Git @("rev-parse", "origin/main") | Out-String).Trim()
  $develop = (Get-Git @("rev-parse", "origin/develop") | Out-String).Trim()
  Write-Host "branch=$branch"
  Write-Host "origin/main=$main"
  Write-Host "origin/develop=$develop"
  Write-Host "content_default=$ContentReleaseTag public_story_max_default=$PublicStoryMax"
  Write-Host "scheduler=must remain Disabled"
  Write-Host "story_010=not part of this release path"
  try {
    $ver = (Invoke-RestMethod -Uri "https://bhava.me/api/v1/version" -TimeoutSec 20 | ConvertTo-Json -Compress)
    Assert-NoSecretsInOutput $ver
    Write-Host "production_version=$ver"
  } catch {
    Write-Host "production_version=unreachable"
  }
}

function Assert-CleanTree {
  $status = (Get-Git @("status", "--porcelain") | Out-String).Trim()
  if ($status) {
    throw "Working tree is not clean. Commit or stash before release.`n$status"
  }
}

function Assert-ContentPolicy {
  if ($PublicStoryMax -ge 10) {
    throw "PublicStoryMax=$PublicStoryMax would expose Story 010+. Refusing."
  }
  if ($ContentReleaseTag -notmatch "^bhava-content-001-009-") {
    Write-Warning "Content tag '$ContentReleaseTag' is not the 001-009 series. Confirm intentionally before promote."
  }
  $pin = Join-Path $RepoRoot "deploy/content/RELEASE_CONTENT.json"
  if (Test-Path $pin) {
    $json = Get-Content $pin -Raw | ConvertFrom-Json
    if ([int]$json.public_story_max -ne $PublicStoryMax) {
      throw "RELEASE_CONTENT.json public_story_max=$($json.public_story_max) != requested $PublicStoryMax"
    }
    if ($json.tag -ne $ContentReleaseTag) {
      throw "RELEASE_CONTENT.json tag=$($json.tag) != requested $ContentReleaseTag"
    }
  }
}

function Invoke-ReleaseDryRun {
  Write-Step "Dry-run release plan"
  Assert-CleanTree
  Get-Git @("fetch", "--all", "--prune") | Out-Null
  Assert-ContentPolicy
  $develop = (Get-Git @("rev-parse", "origin/develop") | Out-String).Trim()
  $main = (Get-Git @("rev-parse", "origin/main") | Out-String).Trim()
  Write-Host "Would validate content tag=$ContentReleaseTag public_max=$PublicStoryMax"
  Write-Host "Would run CI on current branch / open PR into develop if needed"
  Write-Host "Would deploy origin/develop SHA=$develop to staging"
  Write-Host "Would run staging smoke + rollback exercise + restore"
  Write-Host "Would require explicit -PromoteToProduction before main merge"
  Write-Host "Would deploy origin/main SHA=$main only after protected environment approval"
  Write-Host "Would NOT enable scheduler, generate Story 011, or publish Story 010"
}

function Invoke-Rollback {
  if ($Environment -eq "production" -and -not $ConfirmRollback) {
    throw "Production rollback requires -ConfirmRollback. Refusing one-click production rollback."
  }
  if (-not $ConfirmRollback -and $Environment -eq "staging") {
    throw "Staging rollback requires -ConfirmRollback."
  }
  Write-Step "Dispatch GitHub rollback workflow for $Environment"
  if ($DryRun) {
    Write-Host "DryRun: would run gh workflow run rollback-$Environment.yml"
    return
  }
  $workflow = if ($Environment -eq "production") { "rollback-production.yml" } else { "rollback-staging.yml" }
  Push-Location $RepoRoot
  try {
    & gh workflow run $workflow
    if ($LASTEXITCODE -ne 0) { throw "Failed to dispatch $workflow" }
  } finally {
    Pop-Location
  }
}

function Invoke-Release {
  Assert-ContentPolicy
  if ($DryRun) {
    Invoke-ReleaseDryRun
    return
  }

  Write-Step "Preflight"
  Assert-CleanTree
  Get-Git @("fetch", "--all", "--prune") | Out-Null
  $developSha = (Get-Git @("rev-parse", "origin/develop") | Out-String).Trim()
  Write-Host "develop_sha=$developSha content=$ContentReleaseTag public_max=$PublicStoryMax"

  Write-Step "Dispatch staging deploy for develop tip"
  Push-Location $RepoRoot
  try {
    & gh workflow run deploy-staging.yml -f "content_release_tag=$ContentReleaseTag"
    if ($LASTEXITCODE -ne 0) { throw "Failed to dispatch deploy-staging.yml" }
  } finally {
    Pop-Location
  }

  Write-Host "Staging deploy dispatched. Monitor Actions, then re-run with -PromoteToProduction after staging PASS."
  if (-not $PromoteToProduction) {
    Write-Host "Stopped before production promotion (explicit gate)."
    return
  }

  Write-Step "Create develop-to-main release PR"
  Push-Location $RepoRoot
  try {
    & gh pr create --base main --head develop --title "release: promote develop to production" --body @"
## Summary
- Promote validated develop to main for production.
- Content release: $ContentReleaseTag
- Public story max: $PublicStoryMax

## Test plan
- [ ] Staging smoke PASS
- [ ] Staging rollback exercised
- [ ] CI green
- [ ] Production deploy after merge + environment approval
"@
    if ($LASTEXITCODE -ne 0) {
      throw "gh pr create failed ($LASTEXITCODE)"
    }
  } finally {
    Pop-Location
  }
}

switch ($PSCmdlet.ParameterSetName) {
  "Status" { Show-Status }
  "Rollback" { Invoke-Rollback }
  default { Invoke-Release }
}
