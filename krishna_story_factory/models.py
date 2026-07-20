from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .content.story_format_v2 import StoryPackageContentV2


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
    must_include: str = ""
    must_avoid: str = ""
    start_boundary: str = ""
    end_boundary: str = ""


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
    # Format V2 fields
    greeting: str = ""
    series_name: str = "Krishna Book Bedtime"
    story_number: str = ""
    devotional_meaning: str = ""
    five_lessons: list[str] = field(default_factory=list)
    think_about_it: list[str] = field(default_factory=list)
    bedtime_prayer: str = ""
    next_story_preview: str = ""
    parent_note: str = ""
    story_format: str = "v2"

    def to_v2_package(self) -> StoryPackageContentV2:
        lessons = list(self.five_lessons) or [self.moral, self.takeaway]
        while len(lessons) < 5:
            lessons.append(f"Remember Kṛṣṇa with love ({len(lessons) + 1}).")
        questions = list(self.think_about_it) or list(self.recall_questions) + list(self.thinking_questions)
        if self.bedtime_reflection and self.bedtime_reflection not in questions:
            questions.append(self.bedtime_reflection)
        while len(questions) < 3:
            questions.append("What touched your heart in tonight's pastime?")
        prayer = self.bedtime_prayer or self.bedtime_reflection
        meaning = self.devotional_meaning or self.moral
        parent = self.parent_note or self.parent_discussion_note or self.parent_notes
        return StoryPackageContentV2(
            greeting=self.greeting or "Hare Kṛṣṇa, dear children and families!",
            series_name=self.series_name or "Krishna Book Bedtime",
            story_number=self.story_number,
            title=self.title,
            source_reference=self.source_reference,
            scripture_reference=self.scripture_reference,
            recap=self.recap,
            main_story=self.main_story,
            devotional_meaning=meaning,
            five_lessons=lessons[:5],
            think_about_it=questions[:5],
            five_star_challenge=list(self.five_star_challenge)[:5],
            bedtime_prayer=prayer,
            next_story_preview=self.next_story_preview,
            parent_note=parent,
            audio_narration=self.audio_script,
            activity_data={
                "recall_questions": self.recall_questions,
                "thinking_questions": self.thinking_questions,
                "word_search_words": self.word_search_words,
                "draw_activity": self.draw_activity,
                "family_activity": self.family_activity,
            },
            poster_visual_brief=self.poster_visual_brief or self.hero_image_prompt,
            coloring_visual_brief=self.coloring_visual_brief or self.line_art_prompt or self.coloring_page_prompt,
            poster_one_liner=self.poster_one_liner or self.takeaway,
            age_range=self.age_range,
        )

    def to_markdown(self) -> str:
        return self.to_v2_package().to_markdown()


def story_content_from_v2(package: StoryPackageContentV2) -> StoryContent:
    activity = package.activity_data or {}
    parent = package.parent_note
    return StoryContent(
        title=package.title,
        recap=package.recap,
        main_story=package.main_story,
        moral=package.devotional_meaning or (package.five_lessons[0] if package.five_lessons else ""),
        takeaway=package.five_lessons[-1] if package.five_lessons else "",
        five_star_challenge=list(package.five_star_challenge)[:5],
        audio_script=package.audio_narration,
        parent_notes=parent,
        parent_discussion_note=parent,
        bedtime_reflection=package.think_about_it[0] if package.think_about_it else "",
        poster_visual_brief=package.poster_visual_brief,
        coloring_visual_brief=package.coloring_visual_brief,
        poster_one_liner=package.poster_one_liner,
        hero_image_prompt=package.poster_visual_brief,
        line_art_prompt=package.coloring_visual_brief,
        coloring_page_prompt=package.coloring_visual_brief,
        image_prompt=package.poster_visual_brief,
        story_card_text=package.title,
        recall_questions=[str(x) for x in activity.get("recall_questions", [])][:3] or list(package.think_about_it)[:3],
        thinking_questions=[str(x) for x in activity.get("thinking_questions", [])][:2] or list(package.think_about_it)[3:5],
        word_search_words=[str(x) for x in activity.get("word_search_words", [])][:10],
        draw_activity=str(activity.get("draw_activity") or ""),
        family_activity=str(activity.get("family_activity") or ""),
        scripture_reference=package.scripture_reference,
        age_range=package.age_range,
        source_reference=package.source_reference,
        greeting=package.greeting,
        series_name=package.series_name,
        story_number=package.story_number,
        devotional_meaning=package.devotional_meaning,
        five_lessons=list(package.five_lessons)[:5],
        think_about_it=list(package.think_about_it)[:5],
        bedtime_prayer=package.bedtime_prayer,
        next_story_preview=package.next_story_preview,
        parent_note=parent,
        story_format="v2",
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
    for end_marker in (
        "## devotional meaning",
        "## five lessons",
        "## moral",
        "## takeaway",
        "## five-star challenge",
        "## parent discussion",
        "## parent/teacher note",
    ):
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
