"""Local preview ceiling vs production public_story_max for Stories 021/022."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhava_api.catalog.publish_gates import is_publicly_publishable
from bhava_api.catalog.filesystem import Package, REQUIRED_PACKAGE_FILES
from bhava_api.config import get_settings


def _within_ceiling(chapter: str, settings) -> bool:
    return int(chapter) <= int(settings.public_story_max)


def _write_pkg(root: Path, chapter: str, *, publishable: bool, quality: str = "PASS") -> Package:
    slug = f"story-{chapter}"
    pkg = root / f"{chapter}_{slug}"
    pkg.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_PACKAGE_FILES:
        if name == "manifest.json":
            continue
        payload = b"x" * 32 if name.endswith((".png", ".mp3", ".pdf")) else b"ok\n"
        (pkg / name).write_bytes(payload)
    manifest = {
        "chapter_no": chapter,
        "slug": slug,
        "title": f"Story {chapter}",
        "publishable": publishable,
        "quality": {"status": quality, "errors": [], "warnings": []},
        "audio": {
            "audio_stale": False,
            "generation_verified": True,
            "provider": "openai",
            "sha256": "ABC",
            "narration_source_sha": "DEF",
        },
    }
    (pkg / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    files = frozenset(child.name for child in pkg.iterdir() if child.is_file())
    return Package(path=pkg, manifest=manifest, files=files)


def test_local_preview_ceiling_22_includes_021_and_022(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "22")
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "0")
    settings = get_settings()
    assert settings.public_story_max == 22
    for n in ("021", "022"):
        assert _within_ceiling(n, settings)
        pkg = _write_pkg(tmp_path, n, publishable=True)
        assert is_publicly_publishable(pkg)


def test_production_ceiling_20_excludes_021_and_022(monkeypatch) -> None:
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "20")
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    settings = get_settings()
    assert settings.public_story_max == 20
    assert not _within_ceiling("021", settings)
    assert not _within_ceiling("022", settings)


def test_incomplete_or_unpublishable_package_excluded(tmp_path: Path) -> None:
    bad = _write_pkg(tmp_path, "022", publishable=False)
    assert not is_publicly_publishable(bad)
    incomplete = _write_pkg(tmp_path, "021", publishable=True)
    (incomplete.path / "narration.mp3").unlink()
    files = frozenset(child.name for child in incomplete.path.iterdir() if child.is_file())
    incomplete = Package(path=incomplete.path, manifest=incomplete.manifest, files=files)
    assert not is_publicly_publishable(incomplete)


def test_recovery_completed_manifest_must_be_publishable() -> None:
    """Contract: recovery-completed private packages ship publishable=true."""
    from krishna_story_factory.manifest import _is_publishable

    audio = {
        "provider": "openai",
        "generation_verified": True,
        "sha256": "ABC",
        "narration_source_sha": "DEF",
        "audio_stale": False,
    }
    assert _is_publishable(
        mode="prod",
        quality_status="PASS",
        quality_errors=[],
        audio_metadata=audio,
        narration_source_sha="DEF",
        audio_source="openai",
        package_dir=None,
    )


def test_production_defaults_do_not_inherit_local_preview_override(monkeypatch) -> None:
    monkeypatch.delenv("BHAVA_PUBLIC_STORY_MAX", raising=False)
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    pin = json.loads(
        (Path(__file__).resolve().parents[1] / "deploy/content/RELEASE_CONTENT.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(pin["public_story_max"]) == 20
    # Production pin file is the release source of truth and must not drift with
    # operator local preview ceilings (22) used only by start_bhava_local.ps1.
    assert int(pin["public_story_max"]) != 22
    settings = get_settings()
    assert settings.public_story_max == 20
