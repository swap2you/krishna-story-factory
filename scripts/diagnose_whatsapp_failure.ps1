$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function Read-DotEnvValue([string]$name) {
    $envFile = Join-Path $projectRoot ".env"
    if (-not (Test-Path $envFile)) { return "" }
    $line = Get-Content $envFile | Where-Object { $_ -match "^\s*$name\s*=" } | Select-Object -First 1
    if (-not $line) { return "" }
    return ($line -split "=", 2)[1].Trim()
}

Write-Host "=== WhatsApp Cloud diagnostics ==="
Write-Host "WHATSAPP_GRAPH_API_VERSION: $(Read-DotEnvValue 'WHATSAPP_GRAPH_API_VERSION')"
Write-Host "WHATSAPP_PHONE_NUMBER_ID: $(Read-DotEnvValue 'WHATSAPP_PHONE_NUMBER_ID')"
Write-Host "WHATSAPP_TEMPLATE_NAME: $(Read-DotEnvValue 'WHATSAPP_TEMPLATE_NAME')"
Write-Host "WHATSAPP_TEMPLATE_LANGUAGE: $(Read-DotEnvValue 'WHATSAPP_TEMPLATE_LANGUAGE')"

$recipientsPath = Join-Path $projectRoot "input\whatsapp_recipients.csv"
if (Test-Path $recipientsPath) {
    $rows = Import-Csv $recipientsPath
    $active = @($rows | Where-Object {
        $_.opt_in -match '^(1|true|yes|y|on)$' -and
        $_.status -eq 'active' -and
        $_.phone_e164 -notmatch 'REPLACE'
    })
    Write-Host "Active opted-in recipients: $($active.Count)"
} else {
    Write-Host "Active opted-in recipients: 0 (missing input/whatsapp_recipients.csv)"
}

$sendLog = Join-Path $projectRoot "tracking\send_log.csv"
Write-Host ""
Write-Host "=== send_log tail ==="
if (Test-Path $sendLog) {
    Get-Content $sendLog -Tail 10
} else {
    Write-Host "(no tracking/send_log.csv yet)"
}

Write-Host ""
Write-Host "Token status: WHATSAPP_CLOUD_TOKEN is set locally: $([bool](Read-DotEnvValue 'WHATSAPP_CLOUD_TOKEN'))"
Write-Host "Note: token value is never printed."
