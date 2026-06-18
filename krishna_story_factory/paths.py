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
        audio_script=folder / "audio_script.txt",
        whatsapp_caption=folder / "whatsapp_caption.txt",
        activity_sheet=folder / "activity_sheet.pdf",
        story_card=folder / "story_card.png",
        story_card_square=folder / "story_card_square.png",
        story_card_wide=folder / "story_card_wide.png",
        coloring_page=folder / "coloring_page.png",
        image_prompt=folder / "image_prompt.txt",
        hero_image_prompt=folder / "hero_image_prompt.txt",
        story_card_square_prompt=folder / "story_card_square_prompt.txt",
        story_card_wide_prompt=folder / "story_card_wide_prompt.txt",
        line_art_prompt=folder / "line_art_prompt.txt",
        coloring_page_prompt=folder / "coloring_page_prompt.txt",
        ambient_prompt=folder / "ambient_prompt.txt",
        parent_notes=folder / "parent_notes.md",
        manifest=folder / "manifest.json",
        narration_mp3=folder / "narration.mp3",
    )
