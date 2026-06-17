# Dashboard Guide

Run:

```powershell
streamlit run dashboard.py
```

Dashboard features:

- next pending story
- queue table
- editable `series_plan.csv`
- story log
- run test package
- run prod package after confirmation
- generated output folder list

The dashboard is intentionally simple. It does not own business logic. It calls the CLI.

If dashboard fails to start, run:

```powershell
pip install -r requirements.txt
streamlit run dashboard.py
```
