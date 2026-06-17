from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PlanRow:
    chapter_no: str
    slug: str
    title: str
    source_reference: str
    scripture_reference: str
    summary_seed: str
    status: str
    created_at: str = ""
    notes: str = ""
    library_id: str = "krishna_book"
    age_range: str = "7-11"
    package_type: str = "bedtime_story"
    send_date: str = ""
    devotional_focus: str = ""
    activity_type: str = "auto"
    row_index: int | None = None


@dataclass(slots=True)
class StoryContent:
    title: str
    recap: str
    main_story: str
    moral: str
    takeaway: str
    five_star_challenge: list[str]
    audio_script: str
    whatsapp_caption: str
    image_prompt: str
    parent_notes: str
    activity_questions: list[str] = field(default_factory=list)
    vocabulary_words: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        challenge = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(self.five_star_challenge))
        return (
            f"# {self.title}\n\n"
            f"## Recap\n{self.recap}\n\n"
            f"## Main Story\n{self.main_story}\n\n"
            f"## Moral\n{self.moral}\n\n"
            f"## Takeaway\n{self.takeaway}\n\n"
            f"## Five-Star Challenge\n{challenge}\n"
        )


@dataclass(slots=True)
class PackagePaths:
    root: Path
    story_md: Path
    audio_script: Path
    whatsapp_caption: Path
    activity_sheet: Path
    story_card: Path
    image_prompt: Path
    parent_notes: Path
    manifest: Path
    narration_mp3: Path


@dataclass(slots=True)
class SendResult:
    status: str
    detail: str = ""
    provider_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
