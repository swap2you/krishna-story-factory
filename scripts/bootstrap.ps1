$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $Python = (Get-Command py.exe -ErrorAction SilentlyContinue)
    if ($Python) {
        & $Python.Source -3.12 -m venv (Join-Path $ProjectRoot ".venv")
    } else {
        $Python = (Get-Command python.exe -ErrorAction Stop)
        & $Python.Source -m venv (Join-Path $ProjectRoot ".venv")
    }
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
