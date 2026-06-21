from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PlanRow:
    chapter_no: str
    slug: str
    title: str
    project: str
    library_id: str
    source_reference: str
    scripture_reference: str
    summary_seed: str
    age_range: str
    package_type: str
    send_date: str
    status: str
    created_at: str = ""
    updated_at: str = ""
    notes: str = ""
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
    whatsapp_caption: str = ""
    image_prompt: str = ""
    line_art_prompt: str = ""
    story_card_text: str = ""
    parent_notes: str = ""
    hero_image_prompt: str = ""
    story_card_square_prompt: str = ""
    story_card_wide_prompt: str = ""
    coloring_page_prompt: str = ""
    recall_questions: list[str] = field(default_factory=list)
    thinking_questions: list[str] = field(default_factory=list)
    word_search_words: list[str] = field(default_factory=list)
    draw_activity: str = ""
    family_activity: str = ""
    parent_discussion_note: str = ""
    bedtime_reflection: str = ""
    poster_visual_brief: str = ""
    coloring_visual_brief: str = ""
    poster_one_liner: str = ""
    scripture_reference: str = ""
    age_range: str = "6-12"
    source_reference: str = ""

    def to_markdown(self) -> str:
        challenge = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(self.five_star_challenge))
        parent = self.parent_discussion_note or self.parent_notes
        return (
            f"---\n"
            f'title: "{_yaml_escape(self.title)}"\n'
            f'source_reference: "{_yaml_escape(self.source_reference)}"\n'
            f'scripture_reference: "{_yaml_escape(self.scripture_reference)}"\n'
            f"age_range: {self.age_range}\n"
            f"---\n\n"
            f"# {self.title}\n\n"
            f"## Recap\n{self.recap}\n\n"
            f"## Main Story\n{self.main_story}\n\n"
            f"## Moral\n{self.moral}\n\n"
            f"## Takeaway\n{self.takeaway}\n\n"
            f"## Five-Star Challenge\n{challenge}\n\n"
            f"## Parent Discussion Note\n{parent}\n\n"
            f"## Bedtime Reflection\n{self.bedtime_reflection}\n\n"
            f"<!--\n"
            f"## Audio Performance Script\n{self.audio_script}\n\n"
            f"## Poster Visual Brief\n{self.poster_visual_brief or self.hero_image_prompt}\n\n"
            f"## Coloring Visual Brief\n{self.coloring_visual_brief or self.line_art_prompt or self.coloring_page_prompt}\n\n"
            f"## Activity Data\n"
            f"recall: {self.recall_questions}\n"
            f"thinking: {self.thinking_questions}\n"
            f"words: {self.word_search_words}\n"
            f"draw: {self.draw_activity}\n"
            f"family: {self.family_activity}\n"
            f"-->\n"
        )


def _yaml_escape(value: str) -> str:
    return value.replace('"', "'")


def extract_main_story(story_md: str) -> str:
    lowered = story_md.lower()
    marker = "## main story"
    if marker not in lowered:
        return ""
    start = lowered.index(marker) + len(marker)
    tail = story_md[start:].lstrip(":\n ")
    end = len(tail)
    tail_lower = tail.lower()
    for end_marker in ("## moral", "## takeaway", "## five-star challenge", "## parent discussion"):
        if end_marker in tail_lower:
            end = min(end, tail_lower.index(end_marker))
    return tail[:end].strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


@dataclass(slots=True)
class PackagePaths:
    root: Path
    story_md: Path
    narration_mp3: Path
    story_poster: Path
    coloring_page: Path
    activity_sheet: Path
    whatsapp_caption: Path
    manifest: Path


@dataclass(slots=True)
class PipelineResult:
    status: str
    output_dir: str = ""
    quality_status: str = "UNKNOWN"
    whatsapp_status: str = "SKIPPED_DISABLED"
    package_link: str = ""
    drive_status: str = ""
    poster_score: int = 0
    coloring_score: int = 0
    reference_used: bool = False
    errors: str = ""
    detail: str = ""


@dataclass(slots=True)
class SendResult:
    status: str
    detail: str = ""
    failure_reason: str = ""
    provider_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
