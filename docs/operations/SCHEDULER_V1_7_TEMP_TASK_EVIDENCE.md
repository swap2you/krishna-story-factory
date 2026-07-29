# Temporary Task Scheduler SimulateProduction evidence

## Task

| Field | Value |
|-------|-------|
| Name | `Bhava V1.7 SimulateProduction Probe` |
| Principal | Same InteractiveToken principal as `Krishna Story Factory MWF` |
| WorkingDirectory | repository root |
| Action | `powershell.exe -File ...\run_daily_story_scheduled.ps1 ... -SimulateProduction` |

## Result

| Check | Value |
|-------|-------|
| LastTaskResult | **0** |
| Queue SHA before | `7B6DB5D778E2586DBF4174ECA9B2CC15CF60FCBF5784A36041B7E41A6E48422F` |
| Queue unchanged | **True** |
| Provider calls | 0 |
| Drive actions | none |
| Heartbeat | created under `tracking/scheduler_health.json` |
| Temp task deleted afterward | yes |

This proves the Task Scheduler → wrapper → `.NET Process` → Python simulate path under the same principal/working directory as production.
