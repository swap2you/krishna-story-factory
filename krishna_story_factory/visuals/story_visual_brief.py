from __future__ import annotations

import json
import re
from typing import Any

from ..config import Settings
from ..prompts_loader import load_project_text
from .models import PosterCopy, StoryBeat, StoryCharacter, SupportingCaption, VisualBrief


class VisualBriefError(RuntimeError):
    pass


def parse_story_md(story_md: str) -> dict[str, str]:
    title = ""
    if story_md.lstrip().startswith("#"):
        title = story_md.lstrip().split("\n", 1)[0].lstrip("#").strip()
    sections: dict[str, str] = {}
    current = ""
    buffer: list[str] = []
    for line in story_md.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip().lower()
            buffer = []
        else:
            buffer.append(line)
    if current:
        sections[current] = "\n".join(buffer).strip()
    return {"title": title, **sections}


def visual_brief_from_dict(data: dict[str, Any]) -> VisualBrief:
    characters = [
        StoryCharacter(
            name=str(c.get("name", "")),
            role=str(c.get("role", "")),
            appearance=str(c.get("appearance", "")),
            clothing=str(c.get("clothing", "")),
            expression=str(c.get("expression", "")),
            pose=str(c.get("pose", "")),
            position_in_scene=str(c.get("position_in_scene", "")),
        )
        for c in data.get("main_characters", [])
    ]
    beats = [
        StoryBeat(
            sequence=int(b.get("sequence", idx + 1)),
            scene=str(b.get("scene", "")),
            emotion=str(b.get("emotion", "")),
            visual_action=str(b.get("visual_action", "")),
        )
        for idx, b in enumerate(data.get("story_beats", []))
    ]
    return VisualBrief(
        title=str(data.get("title", "")),
        short_title=str(data.get("short_title", "")),
        source_reference=str(data.get("source_reference", "")),
        age_range=str(data.get("age_range", "6-13")),
        central_scene=str(data.get("central_scene", "")),
        setting=str(data.get("setting", "")),
        time_of_day=str(data.get("time_of_day", "")),
        main_characters=characters,
        key_emotions=[str(x) for x in data.get("key_emotions", [])],
        sacred_mood=str(data.get("sacred_mood", "")),
        important_objects=[str(x) for x in data.get("important_objects", [])],
        environment_details=[str(x) for x in data.get("environment_details", [])],
        symbolic_elements=[str(x) for x in data.get("symbolic_elements", [])],
        story_beats=beats,
        heavenly_message_or_quote=str(data.get("heavenly_message_or_quote", "")),
        poster_one_liner=str(data.get("poster_one_liner", "")),
        poster_supporting_captions=[str(x) for x in data.get("poster_supporting_captions", [])],
        line_art_focus=str(data.get("line_art_focus", "")),
        poster_focus=str(data.get("poster_focus", "")),
        must_include=[str(x) for x in data.get("must_include", [])],
        must_avoid=[str(x) for x in data.get("must_avoid", [])],
    )


def poster_copy_from_dict(data: dict[str, Any]) -> PosterCopy:
    captions = [
        SupportingCaption(label=str(c.get("label", "")), text=str(c.get("text", "")))
        for c in data.get("supporting_captions", [])
    ]
    return PosterCopy(
        title=str(data.get("title", "")),
        subtitle=str(data.get("subtitle", "")),
        heavenly_quote=str(data.get("heavenly_quote", "")),
        one_liner=str(data.get("one_liner", "")),
        supporting_captions=captions[:3],
    )


def _parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise VisualBriefError("Response did not contain JSON.")
        return json.loads(match.group(0))


def generate_visual_brief(settings: Settings, story_md: str, *, repair: bool = False) -> VisualBrief:
    if not settings.openai_text_enabled or not settings.openai_api_key:
        parsed = parse_story_md(story_md)
        title = parsed.get("title") or "Krishna Story"
        main = parsed.get("main story", parsed.get("recap", ""))[:500]
        return VisualBrief(
            title=title,
            short_title=title,
            central_scene=main[:300] or "Central devotional scene from the story.",
            setting="Ancient India, devotional atmosphere.",
            key_emotions=["hope", "faith"],
            sacred_mood="devotional and child-safe",
            must_include=["central characters from the story"],
            must_avoid=["modern objects", "violence", "weapons"],
        )

    from openai import OpenAI

    template = load_project_text(settings.project_root, "prompts/visuals/01_story_visual_brief.md")
    prompt = f"{template}\n\nSTORY.MD:\n{story_md}"
    if repair:
        prompt += "\n\nREPAIR: Return only valid JSON matching the schema. Fix any missing required fields."

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(model=settings.openai_text_model, input=prompt)
    raw = getattr(response, "output_text", "") or ""
    brief = visual_brief_from_dict(_parse_json(raw))
    errors = brief.validate()
    if errors:
        raise VisualBriefError(" | ".join(errors))
    return brief


def generate_poster_copy(settings: Settings, story_md: str, brief: VisualBrief) -> PosterCopy:
    if not settings.openai_text_enabled or not settings.openai_api_key:
        return PosterCopy(
            title=brief.title,
            subtitle=brief.short_title or "Krishna Book Bedtime",
            heavenly_quote=brief.heavenly_message_or_quote,
            one_liner=brief.poster_one_liner or "A gentle Krishna-katha for bedtime reflection.",
        )

    from openai import OpenAI

    template = load_project_text(settings.project_root, "prompts/visuals/04_poster_copy.md")
    prompt = (
        f"{template}\n\nSTORY.MD:\n{story_md}\n\nVISUAL BRIEF:\n"
        f"{json.dumps(brief.to_dict(), ensure_ascii=False)}"
    )
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(model=settings.openai_text_model, input=prompt)
    raw = getattr(response, "output_text", "") or ""
    copy = poster_copy_from_dict(_parse_json(raw))
    errors = copy.validate()
    if errors:
        raise VisualBriefError(" | ".join(errors))
    return copy


def load_visual_brief_json(path) -> VisualBrief:
    data = json.loads(path.read_text(encoding="utf-8"))
    brief = visual_brief_from_dict(data)
    errors = brief.validate()
    if errors:
        raise VisualBriefError(" | ".join(errors))
    return brief


def load_poster_copy_json(path) -> PosterCopy:
    data = json.loads(path.read_text(encoding="utf-8"))
    copy = poster_copy_from_dict(data)
    errors = copy.validate()
    if errors:
        raise VisualBriefError(" | ".join(errors))
    return copy
