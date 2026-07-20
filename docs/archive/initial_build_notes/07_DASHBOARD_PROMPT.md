# 07 Dashboard Prompt

Build or validate the Streamlit dashboard.

Dashboard command:
`streamlit run dashboard.py`

Features:
- Show next pending story.
- Show pending queue.
- Show story log.
- Allow editing `series_plan.csv`.
- Allow adding new story rows.
- Trigger `.\scripts\run_test.ps1 --force`.
- Trigger prod only after confirmation checkbox.
- Show generated output folder list.

Rules:
- Do not move business logic into Streamlit.
- CLI remains source of truth.
- Dashboard only reads/writes CSVs and calls CLI.

Deliverable: dashboard starts locally without import errors.
