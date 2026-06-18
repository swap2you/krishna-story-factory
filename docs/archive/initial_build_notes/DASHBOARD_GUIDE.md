# Dashboard Guide

## Run the dashboard

Preferred (avoids broken `streamlit.exe` launcher paths after moving the project):

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run dashboard.py
```

Or use the helper script:

```powershell
.\scripts\run_dashboard.ps1
```

Legacy command (works only when the venv was created in the current folder):

```powershell
streamlit run dashboard.py
```

## If you see "Unable to create process" / old buildpack path

The virtualenv was created before the project was moved to the repo root. The `streamlit.exe` launcher still points at the old Python path.

**Fix:** close this terminal, open a new PowerShell window in the project folder, then:

```powershell
deactivate   # if (.venv) is active
.\scripts\repair_venv.ps1
python -m streamlit run dashboard.py
```

## Dashboard features

- next pending story
- queue table
- editable `series_plan.csv`
- story log
- run test package
- run prod package after confirmation
- generated output folder list

The dashboard is intentionally simple. It does not own business logic. It calls the CLI.
