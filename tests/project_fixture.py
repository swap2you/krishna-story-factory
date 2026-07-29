"""Shared project copy helpers for factory tests (avoid Windows MAX_PATH)."""
from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

_HEAVY_NAMES = (
    ".git",
    ".venv",
    "venv",
    ".env",
    "output",
    ".work",
    ".codex_validation_tmp",
    ".pytest_cache",
    "__pycache__",
    ".cursor",
    "node_modules",
    "MyPilotDropbox",
    ".next",
    "playwright-report",
    "test-results",
    ".bhava",
    ".local_release_archive",
    "data",
)


def project_copy_ignore(*extra: str) -> Callable[[str, list[str]], set[str]]:
    return shutil.ignore_patterns(*_HEAVY_NAMES, *extra)


def copy_project_fixture(source: Path, dest: Path, *, also_ignore: tuple[str, ...] = ()) -> Path:
    shutil.copytree(source, dest, ignore=project_copy_ignore(*also_ignore))
    return dest
