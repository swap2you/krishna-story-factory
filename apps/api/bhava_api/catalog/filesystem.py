"""Read-only access to the existing exact-eight-file story packages."""
from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path

from ..config import get_settings

REQUIRED_PACKAGE_FILES = frozenset(
    {
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
        "manifest.json",
    }
)


@dataclass(frozen=True)
class Package:
    path: Path
    manifest: dict
    files: frozenset[str]


def discover_packages(output_root: Path | None = None) -> list[Package]:
    root = (output_root or get_settings().output_root).resolve()
    if not root.exists():
        return []
    packages: list[Package] = []
    for manifest_path in sorted(root.glob("*/manifest.json")):
        package_path = manifest_path.parent.resolve()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        files = frozenset(child.name for child in package_path.iterdir() if child.is_file())
        if REQUIRED_PACKAGE_FILES.issubset(files):
            packages.append(Package(package_path, manifest, files))
    return sorted(packages, key=lambda package: str(package.manifest.get("chapter_no", "")))


def asset_media_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def package_file(package_path: str | Path, filename: str) -> Path | None:
    """Return a discovered contract file only; never traverse arbitrary paths."""
    if filename not in REQUIRED_PACKAGE_FILES:
        return None
    root = get_settings().output_root.resolve()
    path = (Path(package_path) / filename).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.is_file() else None
