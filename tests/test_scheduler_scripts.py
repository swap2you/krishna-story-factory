from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_is_unattended_and_non_overlapping() -> None:
    runner = (ROOT / "scripts" / "run_daily_story_scheduled.ps1").read_text(encoding="utf-8")
    mwf = (ROOT / "scripts" / "install_mwf_story_task.ps1").read_text(encoding="utf-8")
    daily = (ROOT / "scripts" / "install_daily_story_task.ps1").read_text(encoding="utf-8")
    assert ".venv\\Scripts\\python.exe" in runner
    assert "--mode prod" in runner and "--force" not in runner
    assert '$env:WHATSAPP_SEND_ENABLED = "false"' in runner
    assert '$env:TELEGRAM_SEND_ENABLED = "false"' in runner
    assert '$env:GOOGLE_DRIVE_UPLOAD_ENABLED = "true"' in runner
    assert 'PrimaryTime = "10:00"' in mwf
    assert 'BackupTime = "12:00"' in mwf
    assert "StartWhenAvailable = $false" in mwf
    assert "WakeToRun = $false" in mwf
    assert "-DaysOfWeek Monday" in mwf
    assert "-DaysOfWeek Wednesday" in mwf
    assert "-DaysOfWeek Friday" in mwf
    assert "Krishna Story Factory MWF" in mwf
    assert "MultipleInstances IgnoreNew" in mwf
    assert "RestartCount 2" in mwf
    assert "Minutes 30" in mwf
    assert "Disable-ScheduledTask" in daily
    legacy = (ROOT / "scripts" / "create_task_scheduler_job.ps1").read_text(encoding="utf-8")
    assert "install_mwf_story_task.ps1" in legacy
    assert 'PrimaryTime = "10:00"' in legacy
    assert "Register-ScheduledTask" not in legacy
