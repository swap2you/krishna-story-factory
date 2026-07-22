$ErrorActionPreference = "Stop"
$required = @(
  ".\specs\01_PRODUCT_UX_ARCHITECTURE_BLUEPRINT.md",
  ".\specs\03_TECH_STACK_AND_REPOSITORY_ARCHITECTURE.md",
  ".\cursor\CURSOR_MASTER_BUILD_PROMPT.md",
  ".\ux-prototype\index.html",
  ".\config\contact.example.json"
)
foreach ($path in $required) {
  if (-not (Test-Path $path)) { throw "Missing bootstrap file: $path" }
}
Write-Host "Bhava portal bootstrap package verified." -ForegroundColor Green
