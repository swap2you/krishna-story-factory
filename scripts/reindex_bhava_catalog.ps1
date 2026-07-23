param(
  [string]$ProjectRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$env:PYTHONPATH = Join-Path $ProjectRoot "apps\api"
& $Python -c @"
from bhava_api.db import SessionLocal, Base, engine
from bhava_api.catalog.indexer import index_packages
Base.metadata.create_all(bind=engine)
with SessionLocal() as session:
    result = index_packages(session)
print(f'Reindexed {result.indexed} packages into data/catalog/bhava.sqlite')
"@
