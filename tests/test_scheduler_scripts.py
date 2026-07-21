from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_is_unattended_and_non_overlapping() -> None:
    runner = (ROOT / "scripts" / "run_daily_story_scheduled.ps1").read_text(encoding="utf-8")
    installer = (ROOT / "scripts" / "install_daily_story_task.ps1").read_text(encoding="utf-8")
    assert ".venv\\Scripts\\python.exe" in runner
    assert "--mode prod" in runner and "--force" not in runner
    assert '$env:WHATSAPP_SEND_ENABLED = "false"' in runner
    assert '$env:TELEGRAM_SEND_ENABLED = "false"' in runner
    assert 'DailyTime = "06:00"' in installer
    assert "Disable-ScheduledTask" in installer
    assert "MultipleInstances IgnoreNew" in installer
    assert "RestartCount 2" in installer
    assert "Minutes 30" in installer
    legacy = (ROOT / "scripts" / "create_task_scheduler_job.ps1").read_text(encoding="utf-8")
    assert "install_daily_story_task.ps1" in legacy
    assert 'DailyTime = "06:00"' in legacy
    assert "Register-ScheduledTask" not in legacy
