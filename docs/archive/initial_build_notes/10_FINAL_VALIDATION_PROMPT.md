# 10 Final Validation Prompt

Run final validation.

Commands:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
```

Optional dashboard smoke test:
```powershell
streamlit run dashboard.py
```

Create:
- `BUILD_REPORT.md`
- `VALIDATION_ARTIFACTS.md`

Report:
- commands run
- test result
- generated package path
- files generated
- sender status
- known limitations
- next live API setup steps

Do not fabricate passing results. If something fails, state the failure and fix it if possible.
