from __future__ import annotations

import json
import re
from typing import Any

from ..config import Settings
from ..models import PlanRow, StoryContent
from ..prompts_loader import load_project_text
from ..quality.repetition import clean_repetition, detect_repetition


class StoryGenerationError(RuntimeError):
    pass


_EXPAND_INSTRUCTION = (
    "Expand by adding source-faithful sensory detail, dialogue, and child-friendly reflection. "
    "Do not repeat any closing sentence or paragraph. Close once, softly."
)

_MIN_STORY_WORDS = 750
_MAX_STORY_WORDS = 1050
_MIN_AUDIO_WORDS = 500
_MAX_AUDIO_WORDS = 750


class StoryGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode

    def generate(self, plan: PlanRow) -> StoryContent:
        if self.mode == "test" or not self.settings.openai_text_enabled:
            return _finalize_content(self._mock_story(plan), plan)
        return _finalize_content(self._openai_story(plan), plan)

    def _openai_story(self, plan: PlanRow) -> StoryContent:
        if not self.settings.openai_api_key:
            raise StoryGenerationError("OPENAI_API_KEY is required when OPENAI_TEXT_ENABLED=true.")

        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        prompt = self._build_prompt(plan)
        response = client.responses.create(
            model=self.settings.openai_text_model,
            input=prompt,
        )
        raw_text = getattr(response, "output_text", "") or ""
        content = self._from_dict(plan, self._parse_json(raw_text))
        content = _apply_repetition_cleanup(content)

        if _needs_regeneration(content):
            expand_prompt = f"""{prompt}

REGENERATION REQUEST:
The first draft was too short or repetitive. {_EXPAND_INSTRUCTION}
Return only valid JSON matching the schema.
"""
            response = client.responses.create(
                model=self.settings.openai_text_model,
                input=expand_prompt,
            )
            raw_text = getattr(response, "output_text", "") or ""
            content = self._from_dict(plan, self._parse_json(raw_text))
            content = _apply_repetition_cleanup(content)

        if _needs_regeneration(content):
            raise StoryGenerationError(
                "Generated story/audio is too short or still repetitive after regeneration."
            )
        return content

    def _build_prompt(self, plan: PlanRow) -> str:
        base = load_project_text(self.settings.project_root, "prompts/story_generation_prompt.md")
        rules = load_project_text(self.settings.project_root, "input/content_quality_rules.md")
        return f"""{base}

CONTENT QUALITY RULES:
{rules}

CURRENT QUEUE ROW (generate ONLY for this row; do not mix other pastimes):
- chapter_no: {plan.chapter_no}
- slug: {plan.slug}
- title: {plan.title}
- project: {plan.project}
- library_id: {plan.library_id}
- source_reference: {plan.source_reference}
- scripture_reference: {plan.scripture_reference}
- summary_seed: {plan.summary_seed}
- age_range: {plan.age_range}
- notes: {plan.notes}

Return only valid JSON matching the schema described above.
""".strip()

    def _parse_json(self, text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise StoryGenerationError("OpenAI response did not contain JSON.")
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise StoryGenerationError(f"OpenAI JSON parse failed: {exc}") from exc

    def _from_dict(self, plan: PlanRow, data: dict[str, Any]) -> StoryContent:
        activity = data.get("activity_sheet") or {}
        image_prompt = str(data.get("image_prompt") or data.get("hero_image_prompt") or "")
        line_art = str(data.get("line_art_prompt") or data.get("coloring_page_prompt") or "")
        try:
            return StoryContent(
                title=str(data.get("title") or plan.title),
                recap=str(data["recap"]),
                main_story=str(data["main_story"]),
                moral=str(data["moral"]),
                takeaway=str(data["takeaway"]),
                five_star_challenge=[str(x) for x in data["five_star_challenge"]][:5],
                audio_script=str(data["audio_script"]),
                whatsapp_caption=str(data.get("whatsapp_caption") or ""),
                image_prompt=image_prompt,
                line_art_prompt=line_art,
                hero_image_prompt=str(data.get("hero_image_prompt") or image_prompt),
                story_card_square_prompt=str(data.get("story_card_square_prompt") or image_prompt),
                story_card_wide_prompt=str(
                    data.get("story_card_wide_prompt") or data.get("story_card_square_prompt") or image_prompt
                ),
                coloring_page_prompt=str(data.get("coloring_page_prompt") or line_art),
                story_card_text=str(data.get("story_card_text") or plan.title),
                parent_notes=str(data["parent_notes"]),
                recall_questions=[str(x) for x in activity.get("recall_questions", data.get("recall_questions", []))][:3],
                thinking_questions=[str(x) for x in activity.get("thinking_questions", data.get("thinking_questions", []))][:2],
                word_search_words=[str(x) for x in activity.get("word_search_words", data.get("word_search_words", []))][:10],
                draw_activity=str(activity.get("draw_activity") or data.get("draw_activity") or "Draw your favorite scene from the story."),
                family_activity=str(activity.get("family_activity") or data.get("family_activity") or "Share one thing you learned with your family."),
            )
        except KeyError as exc:
            raise StoryGenerationError(f"Generated story is missing required key: {exc}") from exc

    def _mock_story(self, plan: PlanRow) -> StoryContent:
        challenge = [
            "Listen quietly to the full story.",
            "Name one character from tonight's Krishna-katha.",
            "Chant Hare Krishna once with attention.",
            f"Draw one scene from {plan.title}.",
            "Do one small loving service before bed.",
        ]
        recap = (
            f"Tonight we continue the Krishna Book in order. Our story is {plan.title}, "
            f"from {plan.source_reference}."
        )
        main_story = _mock_main_story(plan)
        audio_script = _mock_audio_script(plan)
        image_prompt = (
            f"Ultra-realistic 3D devotional cinematic painting for children, scene from {plan.title}. "
            f"{plan.summary_seed} Soft volumetric golden light, one clear focal point, expressive faces, "
            "child-safe, no modern objects, no violence."
        )
        square_prompt = (
            f"1080x1080 ultra-realistic 3D devotional cinematic painting, single clear focal scene from {plan.title}. "
            "Warm golden light, child-safe, not crowded, reverential bedtime mood."
        )
        line_art = (
            f"Cute devotional coloring book illustration for children, main scene from {plan.title}. "
            "Thick clean confident black outlines, white background, large colorable spaces, sweet expressive faces, no weapons."
        )
        parent_notes = (
            f"# Parent Notes\n\n"
            f"**Source:** {plan.source_reference}\n"
            f"**Scripture:** {plan.scripture_reference}\n\n"
            "Read slowly in a warm bedtime voice. Keep the mood hopeful and devotional.\n\n"
            "**Discussion:** What does this pastime teach us about trusting Krishna?\n"
        )
        return StoryContent(
            title=plan.title,
            recap=recap,
            main_story=main_story,
            moral="Krishna protects devotees who pray with sincerity. We can trust Him in every situation.",
            takeaway="Before sleep, remember Krishna and plan one small act of kindness for tomorrow.",
            five_star_challenge=challenge,
            audio_script=audio_script,
            whatsapp_caption="",
            image_prompt=image_prompt,
            line_art_prompt=line_art,
            hero_image_prompt=image_prompt,
            story_card_square_prompt=square_prompt,
            story_card_wide_prompt=square_prompt,
            coloring_page_prompt=line_art,
            story_card_text=plan.title,
            parent_notes=parent_notes,
            recall_questions=[
                f"What is tonight's story called?",
                "Who prayed for help in this pastime?",
                "What promise brought hope to the devotees?",
            ],
            thinking_questions=[
                "Why is prayer important when things feel difficult?",
                "How can we show trust in Krishna at home?",
            ],
            word_search_words=[
                "Krishna",
                "prayer",
                "devotee",
                "Earth",
                "Brahma",
                "dharma",
                "hope",
                "love",
                "Vishnu",
                "bhakti",
            ],
            draw_activity=f"Draw the main scene from {plan.title}.",
            family_activity="Together, chant Hare Krishna once and share one thing you are grateful for.",
        )


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def _apply_repetition_cleanup(content: StoryContent) -> StoryContent:
    main_story = clean_repetition(content.main_story, content_type="story")
    audio_script = clean_repetition(content.audio_script, content_type="audio")
    return StoryContent(
        title=content.title,
        recap=content.recap,
        main_story=main_story,
        moral=content.moral,
        takeaway=content.takeaway,
        five_star_challenge=content.five_star_challenge,
        audio_script=audio_script,
        whatsapp_caption=content.whatsapp_caption,
        image_prompt=content.image_prompt,
        line_art_prompt=content.line_art_prompt,
        story_card_text=content.story_card_text,
        parent_notes=content.parent_notes,
        hero_image_prompt=content.hero_image_prompt,
        story_card_square_prompt=content.story_card_square_prompt,
        story_card_wide_prompt=content.story_card_wide_prompt,
        coloring_page_prompt=content.coloring_page_prompt,
        recall_questions=content.recall_questions,
        thinking_questions=content.thinking_questions,
        word_search_words=content.word_search_words,
        draw_activity=content.draw_activity,
        family_activity=content.family_activity,
    )


def _finalize_content(content: StoryContent, plan: PlanRow) -> StoryContent:
    content = _apply_repetition_cleanup(content)
    story_report = detect_repetition(content.main_story, content_type="story")
    audio_report = detect_repetition(content.audio_script, content_type="audio")
    if story_report.errors or audio_report.errors:
        raise StoryGenerationError(
            "Repetition detected after cleanup: "
            + " | ".join(story_report.errors + audio_report.errors)
        )
    if _word_count(content.main_story) < 200 and plan:
        pass  # test mode allows shorter mock
    return content


def _needs_regeneration(content: StoryContent) -> bool:
    story_words = _word_count(content.main_story)
    audio_words = _word_count(content.audio_script)
    if story_words < _MIN_STORY_WORDS or audio_words < _MIN_AUDIO_WORDS:
        return True
    if detect_repetition(content.main_story, content_type="story").errors:
        return True
    if detect_repetition(content.audio_script, content_type="audio").errors:
        return True
    return False


def _mock_main_story(plan: PlanRow) -> str:
    scenes = [
        f"Dear children, Hare Krishna. Tonight we hear about {plan.title}.",
        plan.summary_seed,
        "The palace lamps glow softly while devotees remember Krishna with faith.",
        "Even when the world feels heavy, sincere prayer brings hope and protection.",
        "Vasudeva speaks with quiet strength, and Devaki shines with peaceful devotion.",
        "The demigods offer prayers from their hearts, trusting the Lord's plan.",
        "We learn that courage can be gentle and faith can be calm.",
        "Krishna never forgets those who call Him with love.",
        "Children can picture the scene and remember how the devotees acted with kindness.",
        "Each moment of the pastime teaches honesty, patience, and trust in Krishna.",
        "When we listen carefully, we hear how prayer can change a heavy heart.",
        "Before sleep, remember one kind action you can do tomorrow.",
        "Hare Krishna. Sweet dreams.",
    ]
    return "\n\n".join(scenes)


def _mock_audio_script(plan: PlanRow) -> str:
    return (
        f"Hare Krishna dear children. Tonight's Krishna Book story is {plan.title}. "
        f"{plan.summary_seed} "
        "Listen with wonder as the devotees pray with hope in their hearts. "
        "Vasudeva stays calm, and Devaki's gentle face shines with devotion. "
        '<break time="1.5s" /> '
        "Even in difficult moments, Krishna protects those who trust Him. "
        "Think about one brave and kind choice you can make tomorrow. "
        '<break time="1.0s" /> '
        "The story reminds us that prayer can be soft, sincere, and strong. "
        "When we hear Krishna-katha at bedtime, our minds become peaceful. "
        "Remember the characters from tonight's pastime and what they teach us. "
        "Hare Krishna. Sweet dreams."
    )
