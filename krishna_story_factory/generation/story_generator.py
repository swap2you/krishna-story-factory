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
        return self._from_dict(plan, data)

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
        try:
            return StoryContent(
                title=str(data.get("title") or plan.title),
                recap=str(data["recap"]),
                main_story=str(data["main_story"]),
                moral=str(data["moral"]),
                takeaway=str(data["takeaway"]),
                five_star_challenge=[str(x) for x in data["five_star_challenge"]][:5],
                audio_script=str(data["audio_script"]),
                whatsapp_caption=str(data["whatsapp_caption"]),
                image_prompt=str(data["image_prompt"]),
                line_art_prompt=str(data.get("line_art_prompt") or data.get("coloring_page_prompt") or ""),
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
        main_story = (
            f"Dear children, Hare Krishna. Tonight we hear about {plan.title}. "
            f"{plan.summary_seed} "
            "The devotees remember this pastime with love and trust in Krishna's plan. "
            "Mother Earth felt great burden when cruel kings misused their power. "
            "The demigods prayed with sincere hearts, and Lord Brahma listened carefully. "
            "They sought the Supreme Lord's help because only Krishna can restore dharma. "
            "In a gentle voice filled with compassion, the Lord promised to appear. "
            "This promise brought hope to the whole universe. "
            "For children, the lesson is simple: when the world feels heavy, prayer and devotion bring light. "
            "Krishna never forgets those who call Him with love. "
            "We can remember this story at bedtime and feel peaceful, knowing Krishna cares for everyone. "
            "Let us keep our hearts soft, our words kind, and our actions honest. "
            "When we hear Krishna-katha before sleep, our minds become calm like a quiet river. "
            "Tomorrow we can wake up and serve our parents, teachers, and friends. "
            "That is how we follow the example of the devotees in this sacred story. "
            "Hare Krishna. Sweet dreams."
        )
        audio_script = (
            f"Hare Krishna dear children. [pause] Tonight's Krishna Book story is {plan.title}. [pause] "
            f"{plan.summary_seed} [pause] "
            "Remember that Krishna hears sincere prayer. [pause] "
            "Before sleep, think of one kind action you can do tomorrow. [pause] Hare Krishna."
        )
        caption = (
            "Hare Krishna dear parents 🙏\n\n"
            f"Tonight's Krishna Book bedtime package: *{plan.title}*\n"
            f"Source: {plan.source_reference}\n\n"
            "Please read or play it for the children, complete the activity sheet, "
            "and send a photo/audio/video of their work."
        )
        image_prompt = (
            f"Ultra-realistic devotional painting for children, scene from {plan.title}, "
            f"{plan.summary_seed} Soft Vrindavan or Bhagavatam atmosphere, warm evening light, "
            "reverential mood, child-safe, no modern objects, no gore, 16:9 hero image."
        )
        line_art = (
            f"Simple black line art coloring page for children showing the main scene from {plan.title}, "
            "clean outlines, no shading, devotional, child-safe."
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
            whatsapp_caption=caption,
            image_prompt=image_prompt,
            line_art_prompt=line_art,
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
