# Run the Streamlit dashboard using the active venv Python module path.
# Prefer this over `streamlit run` if the venv was moved or launchers point to an old path.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Error "Missing .venv. Run: python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

& .\.venv\Scripts\python.exe -m streamlit run dashboard.py @args
