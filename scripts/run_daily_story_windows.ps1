$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "daily_run_$Stamp.log"

"=== Krishna Story Factory Daily Run: $(Get-Date -Format o) ===" | Tee-Object -FilePath $LogFile

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    python -m venv .venv 2>&1 | Tee-Object -Append -FilePath $LogFile
}

. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt 2>&1 | Tee-Object -Append -FilePath $LogFile
python run_daily_story.py --mode prod 2>&1 | Tee-Object -Append -FilePath $LogFile
