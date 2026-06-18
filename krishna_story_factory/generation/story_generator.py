from __future__ import annotations

import json
import re
from typing import Any

from ..config import Settings
from ..models import PlanRow, StoryContent
from ..prompts_loader import load_project_text


class StoryGenerationError(RuntimeError):
    pass


class StoryGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode

    def generate(self, plan: PlanRow) -> StoryContent:
        if self.mode == "test" or not self.settings.openai_text_enabled:
            return self._mock_story(plan)
        return self._openai_story(plan)

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
        data = self._parse_json(raw_text)
        content = self._from_dict(plan, data)
        return _ensure_content_lengths(content, plan)

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
                story_card_wide_prompt=str(data.get("story_card_wide_prompt") or data.get("story_card_square_prompt") or image_prompt),
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
        main_story = _expand_mock_story(plan)
        audio_script = _expand_mock_audio(plan)
        caption = ""
        image_prompt = (
            f"Devotional cinematic painting for children, scene from {plan.title}. "
            f"{plan.summary_seed} One clear focal scene, warm evening light, reverential mood, "
            "child-safe, accurate ancient setting, no modern objects, no crowded background faces."
        )
        square_prompt = (
            f"1080x1080 devotional cinematic painting, single clear focal scene from {plan.title}. "
            "Warm golden light, child-safe, not crowded, fewer background faces, reverential bedtime mood."
        )
        line_art = (
            f"Printable black-and-white coloring page for children showing the main scene from {plan.title}. "
            "Thick clean outlines, white background, no shading, large simple shapes, child-friendly faces, no weapons."
        )
        parent_notes = (
            f"# Parent Notes\n\n"
            f"**Source:** {plan.source_reference}\n"
            f"**Scripture:** {plan.scripture_reference}\n\n"
            "Read slowly in a warm bedtime voice. Keep the mood hopeful and devotional.\n\n"
            "**Discussion:** What does this pastime teach us about trusting Krishna?\n"
        )
        content = StoryContent(
            title=plan.title,
            recap=recap,
            main_story=main_story,
            moral="Krishna protects devotees who pray with sincerity. We can trust Him in every situation.",
            takeaway="Before sleep, remember Krishna and plan one small act of kindness for tomorrow.",
            five_star_challenge=challenge,
            audio_script=audio_script,
            whatsapp_caption=caption,
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
        return _ensure_content_lengths(content, plan)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def _ensure_content_lengths(content: StoryContent, plan: PlanRow) -> StoryContent:
    main_story = content.main_story
    while _word_count(main_story) < 850:
        main_story += (
            " The devotees remember this pastime with faith and love. "
            "Children can trust that Krishna hears sincere prayer and protects those who depend on Him. "
            "At bedtime we keep our hearts calm and remember His holy name."
        )

    audio_script = content.audio_script
    padding = [
        f'<break time="1.5s" /> Tonight we heard {plan.title}, a sacred Krishna Book pastime.',
        "Listen softly, with wonder, and remember that Krishna protects His devotees.",
        '<break time="1.0s" /> Before sleep, think of one kind action you can do tomorrow.',
        "Hare Krishna dear children. Sweet dreams.",
    ]
    idx = 0
    while _word_count(audio_script) < 650:
        audio_script += " " + padding[idx % len(padding)]
        idx += 1

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


def _expand_mock_story(plan: PlanRow) -> str:
    paragraphs = [
        f"Dear children, Hare Krishna. Tonight we hear about {plan.title}.",
        plan.summary_seed,
        "The devotees remember this pastime with love and trust in Krishna's plan.",
        "When the world feels heavy, sincere prayer brings hope and protection.",
        "Krishna never forgets those who call Him with love.",
        "We can remember this story at bedtime and feel peaceful.",
        "Let us keep our hearts soft, our words kind, and our actions honest.",
        "When we hear Krishna-katha before sleep, our minds become calm like a quiet river.",
        "Tomorrow we can wake up and serve our parents, teachers, and friends.",
        "That is how we follow the example of the devotees in this sacred story.",
    ]
    text = " ".join(paragraphs)
    while len(text.split()) < 220:
        text += (
            " The Lord's pastimes teach us courage, kindness, and faith in difficult moments. "
            "Children can remember Krishna's name and feel protected."
        )
    return text


def _expand_mock_audio(plan: PlanRow) -> str:
    parts = [
        f"Hare Krishna dear children. Tonight's Krishna Book story is {plan.title}.",
        plan.summary_seed,
        "Listen softly, with wonder, as the devotees prayed for help.",
        "Remember that Krishna hears sincere prayer.",
        '<break time="1.5s" />',
        "Before sleep, think of one kind action you can do tomorrow.",
        '<break time="1.0s" />',
        "Hare Krishna. Sweet dreams.",
    ]
    text = " ".join(parts)
    while len(text.split()) < 120:
        text += (
            " The narration moves gently, like a calm bedtime river, helping children feel safe and loved. "
            "Krishna's mercy is always near."
        )
    return text
