from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_is_unattended_and_non_overlapping() -> None:
    runner = (ROOT / "scripts" / "run_daily_story_scheduled.ps1").read_text(encoding="utf-8-sig")
    mwf = (ROOT / "scripts" / "install_mwf_story_task.ps1").read_text(encoding="utf-8")
    daily = (ROOT / "scripts" / "install_daily_story_task.ps1").read_text(encoding="utf-8")
    assert ".venv\\Scripts\\python.exe" in runner
    assert ('"--mode", "prod"' in runner or "--mode prod" in runner) and "--force" not in runner
    assert "System.Diagnostics.Process" in runner
    assert "UseShellExecute = $false" in runner
    assert "CreateNoWindow = $true" in runner
    assert "RedirectStandardOutput = $true" in runner
    assert "RedirectStandardError = $true" in runner
    assert "ReadToEndAsync" in runner
    assert "Start-Process" not in runner
    assert "NoNewWindow" not in runner
    assert "Tee-Object" not in runner
    assert '$env:WHATSAPP_SEND_ENABLED = "false"' in runner
    assert '$env:TELEGRAM_SEND_ENABLED = "false"' in runner
    assert '$env:GOOGLE_DRIVE_UPLOAD_ENABLED = "true"' in runner
    assert '$env:AUDIO_SAMPLE_FIRST_REQUIRED = "1"' in runner
    assert '$env:BHAVA_WEB_ASSETS_UI_GATE = "1"' in runner
    assert 'PrimaryTime = "10:00"' in mwf
    assert "BackupTime" not in mwf
    assert "12:00" not in mwf
    assert "Hours 4" in mwf
    assert "StartWhenAvailable = $false" in mwf
    assert "StartWhenAvailable = $true" not in mwf
    assert "WakeToRun = $false" in mwf
    assert ("StopOnIdleEnd = $false" in mwf) or ("DontStopOnIdleEnd" in mwf)
    assert "-DaysOfWeek Monday" in mwf
    assert "-DaysOfWeek Wednesday" in mwf
    assert "-DaysOfWeek Friday" in mwf
    assert "Krishna Story Factory MWF" in mwf
    assert "MultipleInstances IgnoreNew" in mwf
    assert "RestartCount 0" in mwf
    assert "Minutes 60" not in mwf
    assert "Disable-ScheduledTask" in daily
    legacy = (ROOT / "scripts" / "create_task_scheduler_job.ps1").read_text(encoding="utf-8")
    assert "install_mwf_story_task.ps1" in legacy
    assert 'PrimaryTime = "10:00"' in legacy
    assert "Register-ScheduledTask" not in legacy
