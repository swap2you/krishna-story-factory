from __future__ import annotations

import re
from pathlib import Path

from .models import PackagePaths, PlanRow


def safe_slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value or "story"


def make_package_paths(output_root: Path, plan: PlanRow) -> PackagePaths:
    folder = output_root / f"{plan.chapter_no}_{safe_slug(plan.slug or plan.title)}"
    folder.mkdir(parents=True, exist_ok=True)
    return PackagePaths(
        root=folder,
        story_md=folder / "story.md",
        narration_mp3=folder / "narration.mp3",
        story_poster=folder / "story_poster.png",
        coloring_page=folder / "coloring_page.png",
        activity_sheet=folder / "activity_sheet.pdf",
        whatsapp_caption=folder / "whatsapp_caption.txt",
        manifest=folder / "manifest.json",
    )
