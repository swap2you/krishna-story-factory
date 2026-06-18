from __future__ import annotations

from pathlib import Path


def load_project_text(project_root: Path, relative_path: str) -> str:
    path = project_root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()
