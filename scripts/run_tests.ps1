$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python run_daily_story.py --mode test --force
