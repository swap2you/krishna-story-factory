# Recreate the local virtual environment (fixes broken streamlit/py launcher paths).
# Close other terminals using this venv before running.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "Deactivate any active venv in this terminal first (command: deactivate)."
Write-Host "Close other terminals using $PWD\.venv if delete fails."
Write-Host ""

if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
}

python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Start the dashboard with:"
Write-Host "  python -m streamlit run dashboard.py"
Write-Host "or:"
Write-Host "  .\scripts\run_dashboard.ps1"
