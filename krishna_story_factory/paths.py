from __future__ import annotations

import re
from pathlib import Path

from .models import PackagePaths, PlanRow


def safe_slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value or "story"


def assert_path_under_root(path: Path, root: Path, *, label: str = "path") -> Path:
    """Reject path traversal; require resolved path to stay under an approved root."""
    resolved = Path(path).resolve()
    root_resolved = Path(root).resolve()
    if resolved != root_resolved and not resolved.is_relative_to(root_resolved):
        raise ValueError(f"{label} escapes approved root: {resolved} not under {root_resolved}")
    return resolved


def make_package_paths(output_root: Path, plan: PlanRow) -> PackagePaths:
    folder = output_root / f"{plan.chapter_no}_{safe_slug(plan.slug or plan.title)}"
    folder = assert_path_under_root(folder, output_root, label="package folder")
    folder.mkdir(parents=True, exist_ok=True)
    return PackagePaths(
        root=folder,
        story_md=folder / "story.md",
        narration_mp3=folder / "narration.mp3",
        story_poster=folder / "story_poster.png",
        coloring_page=folder / "coloring_page.png",
        simple_coloring_page=folder / "simple_coloring_page.png",
        activity_sheet=folder / "activity_sheet.pdf",
        whatsapp_caption=folder / "whatsapp_caption.txt",
        manifest=folder / "manifest.json",
    )
