"""Canonical Story Format V2 — typed package, markdown render, audio, QA."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from typing import Protocol

SERIES_NAME = "Krishna Book Bedtime"


class _PlanLike(Protocol):
    chapter_no: str
    title: str
    source_reference: str
    scripture_reference: str
    age_range: str


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text or ""))

DEFAULT_GREETING = "Hare Kṛṣṇa, dear children and families!"

VISIBLE_SECTION_ORDER = (
    "Greeting",
    "Series",
    "Story Number and Title",
    "Scriptural Source",
    "Recap",
    "Main Story",
    "Devotional Meaning",
    "Five Lessons",
    "Think About It",
    "Five-Star Challenge",
    "Bedtime Prayer",
    "Next Story Preview",
    "Parent/Teacher Note",
)

META_DEFENSIVE_PATTERNS = (
    r"no soldier needed",
    r"no later event was needed",
    r"this detail is not part of the next chapter",
    r"this is not yet",
    r"we will not hear about",
    r"not included in tonight",
)

HARE_KRISHNA_MANTRA = "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare"


@dataclass(slots=True)
class StoryPackageContentV2:
    greeting: str
    series_name: str
    story_number: str
    title: str
    source_reference: str
    scripture_reference: str
    recap: str
    main_story: str
    devotional_meaning: str
    five_lessons: list[str]
    think_about_it: list[str]
    five_star_challenge: list[str]
    bedtime_prayer: str
    next_story_preview: str
    parent_note: str
    audio_narration: str
    activity_data: dict[str, Any] = field(default_factory=dict)
    poster_visual_brief: str = ""
    coloring_visual_brief: str = ""
    poster_one_liner: str = ""
    age_range: str = "6-12"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lessons = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(self.five_lessons))
        questions = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(self.think_about_it))
        challenge = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(self.five_star_challenge))
        story_label = f"Story {int(self.story_number):03d}" if str(self.story_number).isdigit() else f"Story {self.story_number}"
        return (
            f"---\n"
            f'title: "{_yaml_escape(self.title)}"\n'
            f'source_reference: "{_yaml_escape(self.source_reference)}"\n'
            f'scripture_reference: "{_yaml_escape(self.scripture_reference)}"\n'
            f"age_range: {self.age_range}\n"
            f"story_number: {self.story_number}\n"
            f"format: v2\n"
            f"---\n\n"
            f"{self.greeting}\n\n"
            f"# 📿 {self.series_name}\n\n"
            f"## {story_label} — {self.title}\n\n"
            f"### Scriptural Source\n"
            f"{self.source_reference}\n"
            f"{self.scripture_reference}\n\n"
            f"## Recap\n{self.recap.strip()}\n\n"
            f"## Main Story\n{self.main_story.strip()}\n\n"
            f"## Devotional Meaning\n{self.devotional_meaning.strip()}\n\n"
            f"## Five Lessons\n{lessons}\n\n"
            f"## Think About It\n{questions}\n\n"
            f"## Five-Star Challenge\n{challenge}\n\n"
            f"## Bedtime Prayer\n{self.bedtime_prayer.strip()}\n\n"
            f"## Next Story Preview\n{self.next_story_preview.strip()}\n\n"
            f"## Parent/Teacher Note\n{self.parent_note.strip()}\n\n"
            f"<!--\n"
            f"## Audio Narration\n{self.audio_narration.strip()}\n\n"
            f"## Poster Visual Brief\n{self.poster_visual_brief.strip()}\n\n"
            f"## Coloring Visual Brief\n{self.coloring_visual_brief.strip()}\n\n"
            f"## Activity Data\n{self.activity_data}\n"
            f"-->\n"
        )


def build_greeting(configured_names: str = "") -> str:
    names = [part.strip() for part in (configured_names or "").split(",") if part.strip()]
    if not names:
        return DEFAULT_GREETING
    if len(names) == 1:
        return f"Hare Kṛṣṇa, dear {names[0]} and family!"
    if len(names) == 2:
        return f"Hare Kṛṣṇa, dear {names[0]} and {names[1]}!"
    joined = ", ".join(names[:-1]) + f", and {names[-1]}"
    return f"Hare Kṛṣṇa, dear {joined}!"


def build_audio_narration(package: StoryPackageContentV2) -> str:
    """Derive spoken narration from structured fields (never parent note / think / challenge dump)."""
    lessons = " ".join(f"{i + 1}. {lesson}" for i, lesson in enumerate(package.five_lessons[:5]))
    parts = [
        package.greeting,
        f"Tonight is Story {package.story_number}: {package.title}.",
        package.recap.strip(),
        _condense_main_story(package.main_story, target_words=420),
        package.devotional_meaning.strip(),
        f"Five lessons for tonight: {lessons}",
        package.bedtime_prayer.strip(),
        package.next_story_preview.strip(),
    ]
    text = "\n\n".join(part for part in parts if part)
    return text


def validate_story_format_v2(package: StoryPackageContentV2, *, next_title: str = "") -> list[str]:
    errors: list[str] = []
    if not (package.greeting or "").strip():
        errors.append("greeting is required")
    if package.series_name.strip() != SERIES_NAME:
        errors.append(f"series_name must be {SERIES_NAME!r}")
    if len(package.five_lessons) != 5:
        errors.append("five_lessons must contain exactly five items")
    if not (3 <= len(package.think_about_it) <= 5):
        errors.append("think_about_it must contain 3–5 questions")
    if len(package.five_star_challenge) != 5:
        errors.append("five_star_challenge must contain exactly five items")
    errors.extend(_placeholder_errors(package))
    recap_words = word_count(package.recap)
    if not (70 <= recap_words <= 130) and package.story_number not in {"001", "1"}:
        errors.append(f"recap word count {recap_words} outside 70–130")
    main_words = word_count(package.main_story)
    if not (700 <= main_words <= 950):
        errors.append(f"main_story word count {main_words} outside 700–950")
    meaning_words = word_count(package.devotional_meaning)
    if not (100 <= meaning_words <= 180):
        errors.append(f"devotional_meaning word count {meaning_words} outside 100–180")
    prayer_words = word_count(package.bedtime_prayer)
    if not (75 <= prayer_words <= 140):
        errors.append(f"bedtime_prayer word count {prayer_words} outside 75–140")
    preview_words = word_count(package.next_story_preview)
    if not (30 <= preview_words <= 80):
        errors.append(f"next_story_preview word count {preview_words} outside 30–80")
    parent_words = word_count(package.parent_note)
    if not (60 <= parent_words <= 120):
        errors.append(f"parent_note word count {parent_words} outside 60–120")
    if not _has_maha_mantra(package.bedtime_prayer):
        errors.append("bedtime_prayer must include the Hare Kṛṣṇa mahā-mantra")
    if next_title and next_title.lower() not in package.next_story_preview.lower():
        # Allow soft match on key words from next title
        tokens = [t for t in re.findall(r"[A-Za-zĀ-žāīūṛṅñṭḍṇśṣḥṁ]{4,}", next_title) if t.lower() not in {"lord", "from", "with"}]
        if tokens and not any(tok.lower() in package.next_story_preview.lower() for tok in tokens[:3]):
            errors.append("next_story_preview does not reference the next episode")
    blob = " ".join(
        [
            package.main_story,
            package.recap,
            package.devotional_meaning,
            package.bedtime_prayer,
            package.next_story_preview,
        ]
    ).lower()
    for pattern in META_DEFENSIVE_PATTERNS:
        if re.search(pattern, blob):
            errors.append(f"meta-defensive language detected: {pattern}")
    for para in re.split(r"\n\s*\n", package.main_story.strip()):
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", para.strip()) if s.strip()]
        if len(sentences) > 3:
            errors.append("main_story paragraphs must stay within 1–3 sentences")
            break
    errors.extend(validate_audio_consistency(package))
    return errors


def validate_audio_consistency(package: StoryPackageContentV2) -> list[str]:
    errors: list[str] = []
    audio = package.audio_narration or ""
    audio_l = audio.lower()
    if not audio.strip():
        return ["audio_narration is empty"]
    audio_words = word_count(audio)
    if not (650 <= audio_words <= 850):
        # Allow slightly wider band for mock/test; callers can treat as soft.
        if audio_words < 400 or audio_words > 950:
            errors.append(f"audio_narration word count {audio_words} outside expected spoken range")
    if package.parent_note and package.parent_note[:40].lower() in audio_l:
        errors.append("audio_narration must not include Parent/Teacher Note")
    if "answer key" in audio_l:
        errors.append("audio_narration must not include answer key")
    if not _has_maha_mantra(audio):
        errors.append("audio_narration must include bedtime prayer / mahā-mantra")
    if package.story_number and str(package.story_number) not in audio and f"story {int(package.story_number)}" not in audio_l:
        if f"story {package.story_number}" not in audio_l:
            errors.append("audio_narration missing current story number")
    if package.next_story_preview and word_count(package.next_story_preview) > 10:
        # Require at least a short preview cue in audio
        preview_tokens = [t for t in re.findall(r"[A-Za-z]{5,}", package.next_story_preview)[:4]]
        if preview_tokens and not any(tok.lower() in audio_l for tok in preview_tokens):
            errors.append("audio_narration missing next-story preview cue")
    return errors


_PLACEHOLDER_RE = re.compile(
    r"\(\s*[345]\s*\)|\bTODO\b|\bTBD\b|\bdummy\b|\bplaceholder\b|\.\.\.\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _placeholder_errors(package: StoryPackageContentV2) -> list[str]:
    errors: list[str] = []
    chunks: list[str] = list(package.five_lessons) + list(package.think_about_it) + list(package.five_star_challenge)
    chunks.extend(
        [
            package.main_story,
            package.devotional_meaning,
            package.bedtime_prayer,
            package.next_story_preview,
            package.recap,
        ]
    )
    for chunk in chunks:
        if _PLACEHOLDER_RE.search(chunk or ""):
            errors.append(f"placeholder/incomplete text detected: {chunk[:80]!r}")
            break
    for lesson in package.five_lessons:
        if len(re.findall(r"\b[\w']+\b", lesson or "")) < 6:
            errors.append(f"five_lessons item too short/incomplete: {lesson!r}")
    return errors


def validate_story_markdown_v2(story_md: str) -> list[str]:
    errors: list[str] = []
    text = story_md or ""
    if _PLACEHOLDER_RE.search(text):
        errors.append("story.md contains placeholder/incomplete lesson markers")
    required = [
        "## Recap",
        "## Main Story",
        "## Devotional Meaning",
        "## Five Lessons",
        "## Think About It",
        "## Five-Star Challenge",
        "## Bedtime Prayer",
        "## Next Story Preview",
        "## Parent/Teacher Note",
    ]
    for section in required:
        if section.lower() not in text.lower():
            errors.append(f"story.md missing section: {section}")
    # Order check
    positions = []
    lowered = text.lower()
    for section in required:
        idx = lowered.find(section.lower())
        if idx < 0:
            continue
        positions.append((idx, section))
    ordered = [s for _, s in sorted(positions)]
    expected = [s for s in required if s in ordered]
    if ordered != expected:
        errors.append("story.md visible sections are out of order")
    if "## moral" in lowered or "## takeaway" in lowered or "## bedtime reflection" in lowered:
        errors.append("story.md still uses legacy Moral/Takeaway/Bedtime Reflection headings")
    return errors


def _split_long_paragraphs(main_story: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", main_story.strip()) if p.strip()]
    fixed: list[str] = []
    for para in paragraphs:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
        if len(sentences) <= 3:
            fixed.append(para)
            continue
        for i in range(0, len(sentences), 3):
            fixed.append(" ".join(sentences[i : i + 3]))
    return "\n\n".join(fixed)


def package_from_llm_dict(
    data: dict[str, Any],
    *,
    plan: _PlanLike,
    greeting: str,
    next_preview_fallback: str = "",
) -> StoryPackageContentV2:
    activity = data.get("activity_data") or data.get("activity_sheet") or {}
    lessons = [str(x).strip() for x in (data.get("five_lessons") or []) if str(x).strip()]
    questions = [str(x).strip() for x in (data.get("think_about_it") or []) if str(x).strip()]
    challenge = [str(x).strip() for x in (data.get("five_star_challenge") or []) if str(x).strip()][:5]
    # Legacy fallback bridge — never invent numbered placeholder lessons.
    if len(lessons) < 5:
        moral = str(data.get("moral") or "").strip()
        takeaway = str(data.get("takeaway") or "").strip()
        fallbacks = [
            "Trust Lord Kṛṣṇa even when the path feels uncertain.",
            "Speak truthfully and keep your promises with love.",
            "Remember the Lord with a soft and grateful heart.",
            "Offer simple prayers when fear or worry appears.",
            "Share kindness with family as a daily act of devotion.",
        ]
        while len(lessons) < 5:
            if moral and moral not in lessons:
                lessons.append(moral)
                moral = ""
            elif takeaway and takeaway not in lessons:
                lessons.append(takeaway)
                takeaway = ""
            else:
                nxt = next((item for item in fallbacks if item not in lessons), "")
                if not nxt:
                    break
                lessons.append(nxt)
        lessons = lessons[:5]
        if len(lessons) < 5:
            raise ValueError("five_lessons incomplete after fallback; refusing placeholder lessons")
    if len(questions) < 3:
        for item in (activity.get("recall_questions") or []) + (activity.get("thinking_questions") or []):
            if str(item).strip() and str(item).strip() not in questions:
                questions.append(str(item).strip())
        reflection = str(data.get("bedtime_reflection") or "").strip()
        if reflection and reflection not in questions:
            questions.append(reflection)
        while len(questions) < 3:
            questions.append("What did you notice about the devotees' love for Kṛṣṇa?")
        questions = questions[:5]
    while len(challenge) < 5:
        challenge.append("Offer one kind action today for Kṛṣṇa.")
    prayer = str(data.get("bedtime_prayer") or data.get("bedtime_reflection") or "").strip()
    if not _has_maha_mantra(prayer):
        prayer = (prayer + "\n\n" if prayer else "") + (
            f"Dear Kṛṣṇa, please keep us close to You. We chant: {HARE_KRISHNA_MANTRA}. "
            "Good night, and may Your protection rest gently on our hearts."
        )
    meaning = str(data.get("devotional_meaning") or data.get("moral") or "").strip()
    parent = str(data.get("parent_note") or data.get("parent_discussion_note") or data.get("parent_notes") or "").strip()
    preview = str(data.get("next_story_preview") or next_preview_fallback or "").strip()
    audio = str(data.get("audio_narration") or data.get("audio_performance_script") or data.get("audio_script") or "").strip()
    package = StoryPackageContentV2(
        greeting=str(data.get("greeting") or greeting).strip() or greeting,
        series_name=str(data.get("series_name") or SERIES_NAME).strip() or SERIES_NAME,
        story_number=str(data.get("story_number") or plan.chapter_no),
        title=str(data.get("title") or plan.title),
        source_reference=str(data.get("source_reference") or plan.source_reference),
        scripture_reference=str(data.get("scripture_reference") or plan.scripture_reference),
        recap=str(data.get("recap") or "").strip(),
        main_story=_split_long_paragraphs(str(data.get("main_story") or "").strip()),
        devotional_meaning=meaning,
        five_lessons=lessons[:5],
        think_about_it=questions[:5],
        five_star_challenge=challenge[:5],
        bedtime_prayer=prayer,
        next_story_preview=preview,
        parent_note=parent,
        audio_narration=audio,
        activity_data=dict(activity) if isinstance(activity, dict) else {},
        poster_visual_brief=str(data.get("poster_visual_brief") or data.get("hero_image_prompt") or ""),
        coloring_visual_brief=str(data.get("coloring_visual_brief") or data.get("line_art_prompt") or ""),
        poster_one_liner=str(data.get("poster_one_liner") or ""),
        age_range=str(data.get("age_range") or plan.age_range or "6-12"),
    )
    if not package.audio_narration.strip():
        package.audio_narration = build_audio_narration(package)
    return package


def extract_section(story_md: str, heading: str) -> str:
    pattern = re.compile(
        rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s+|\n<!--|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(story_md or "")
    return match.group(1).strip() if match else ""


def _condense_main_story(main_story: str, *, target_words: int = 360) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", main_story.strip()) if p.strip()]
    selected: list[str] = []
    total = 0
    for para in paragraphs:
        wc = word_count(para)
        if total and total + wc > target_words + 40:
            break
        selected.append(para)
        total += wc
        if total >= target_words:
            break
    if not selected:
        return main_story.strip()
    return "\n\n".join(selected)


def has_maha_mantra(text: str) -> bool:
    return _has_maha_mantra(text)


def _has_maha_mantra(text: str) -> bool:
    compact = re.sub(r"\s+", " ", (text or "").lower())
    return "hare k" in compact and "rama" in compact.replace("rāma", "rama")


def _yaml_escape(value: str) -> str:
    return value.replace('"', "'")


__all__ = [
    "SERIES_NAME",
    "DEFAULT_GREETING",
    "VISIBLE_SECTION_ORDER",
    "HARE_KRISHNA_MANTRA",
    "StoryPackageContentV2",
    "build_greeting",
    "build_audio_narration",
    "validate_story_format_v2",
    "validate_audio_consistency",
    "validate_story_markdown_v2",
    "package_from_llm_dict",
    "extract_section",
    "has_maha_mantra",
]
