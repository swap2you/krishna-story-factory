from __future__ import annotations

import json
import re
from typing import Any


from ..config import Settings
from ..models import PlanRow, StoryContent


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
        return f"""
You are creating a Krishna-conscious bedtime story package for children ages 7 to 11.
Write in a warm, simple, devotional, ISKCON-friendly tone. Avoid fear-heavy, graphic, sectarian, or adult material.
Keep the language age-appropriate for 7-11 year olds. Include light vocabulary support.

Source reference: {plan.source_reference}
Scripture reference: {plan.scripture_reference}
Story seed: {plan.summary_seed}
Title: {plan.title}

Return only valid JSON with exactly these keys:
- title: string
- recap: string, 2-3 short sentences
- main_story: string, 900-1300 words, bedtime style, no markdown heading inside
- moral: string, 2-3 sentences
- takeaway: string, 1-2 practical sentences
- five_star_challenge: array of exactly 5 short child-friendly actions
- audio_script: string, natural narration script including short pauses in brackets, no markdown
- whatsapp_caption: string, concise parent-facing WhatsApp caption with Hare Krishna greeting and ask parents to send photo/audio/video after activity
- image_prompt: string, safe devotional story-card image prompt, no copyrighted style names
- parent_notes: string, markdown-style notes for parents with reading tip, devotional focus, and discussion question
- activity_questions: array of exactly 5 questions
- vocabulary_words: array of exactly 5 child-friendly devotional words from the story
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
                parent_notes=str(data["parent_notes"]),
                activity_questions=[str(x) for x in data.get("activity_questions", [])][:5],
                vocabulary_words=[str(x) for x in data.get("vocabulary_words", [])][:5],
            )
        except KeyError as exc:
            raise StoryGenerationError(f"Generated story is missing required key: {exc}") from exc

    def _mock_story(self, plan: PlanRow) -> StoryContent:
        challenge = [
            "Listen to the story without interrupting.",
            "Say one thing Mother Yasoda teaches us about love.",
            "Chant the Hare Krishna maha-mantra one time with attention.",
            "Draw Krishna smiling with Mother Yasoda.",
            "Do one small service for your parent before bedtime.",
        ]
        questions = [
            "Why did Mother Yasoda want to bind Krishna?",
            "What was strange about the rope?",
            "What made Krishna agree to be bound?",
            "What does this story teach about love?",
            "What service can you do at home today?",
        ]
        vocab = ["bhakti", "prasadam", "Yasoda", "Damodara", "service"]
        main_story = (
            "One evening in beautiful Vrindavana, Mother Yasoda was busy making butter for Krishna. "
            "The house smelled sweet, and the soft sound of churning filled the room. Krishna came near His mother, "
            "His eyes bright like lotus petals, and He wanted her full attention. Mother Yasoda loved Krishna more than her own life, "
            "so she stopped her work and held Him close. But soon the milk on the stove began to boil over. Mother Yasoda gently placed Krishna down "
            "and ran to save the milk. Krishna was small, but He was not ordinary. He became upset, thinking, 'Mother left Me for milk!' "
            "With His tiny hand, He broke a butter pot and shared the butter with the monkeys. When Mother Yasoda returned, she saw the broken pot, "
            "the butter trail, and the little footprints of her beloved child. She followed the marks and found Krishna sitting like a clever prince, "
            "feeding butter to the monkeys. Krishna saw His mother coming with a small stick, and He ran. Mother Yasoda ran after Him. The Supreme Lord, "
            "who cannot be caught by great yogis, allowed Himself to be chased by His mother. At last, Mother Yasoda caught Him. Krishna cried softly, "
            "rubbing His eyes, and Mother Yasoda's heart melted. She did not want to hurt Him. She only wanted to teach Him not to make mischief. "
            "She decided to tie Him to a wooden grinding mortar so He would stay in one place. She brought a rope, but when she tried to tie it, "
            "it was two fingers too short. She added another rope. Still two fingers too short. She added more ropes from the house. Still two fingers too short. "
            "All the village mothers laughed with affection. How could so much rope not fit around one small child? Mother Yasoda kept trying. "
            "Her hair became loose, and drops of effort appeared on her face. Krishna saw her love and hard work. Then He agreed. Suddenly, the rope fit. "
            "The Lord who holds all universes became bound by the love of His devotee. That is why Krishna is called Damodara, the one whose belly was bound by rope. "
            "The lesson is not that Krishna was defeated by rope. He was conquered by love. For children, this means our small acts of service matter. "
            "When we listen, help, chant, and remember Krishna with sincerity, Krishna notices. He may be the Supreme Lord, but He becomes very close to a heart filled with bhakti. "
            "So at bedtime, we can remember Mother Yasoda's patience and Krishna's sweet smile. We can ask, 'How can I serve Krishna and my family tomorrow?' "
            "Then sleep becomes peaceful, because the heart is tied gently to Krishna."
        )
        audio_script = (
            f"Hare Krishna dear children. [pause] Tonight's story is called {plan.title}. [pause] "
            "In Vrindavana, Mother Yasoda tried to bind little Krishna with rope, but every rope was two fingers too short. [pause] "
            "She kept trying with love, and Krishna finally allowed Himself to be bound. [pause] "
            "This teaches us that Krishna is not conquered by strength. He is conquered by sincere love and service. [pause] "
            "Before sleeping, think of one small service you can do tomorrow. Hare Krishna."
        )
        caption = (
            "Hare Krishna dear parents 🙏\n\n"
            f"Today’s bedtime story package: *{plan.title}*\n"
            "Please read or play it for the kids, help them complete the activity sheet, and send a photo/audio/video of their completed work. "
            "This keeps them encouraged while learning Krishna-katha."
        )
        image_prompt = (
            "A gentle devotional bedtime story card showing child Krishna in Vrindavana beside Mother Yasoda, "
            "a wooden grinding mortar, soft evening light, butter pot nearby, warm village home setting, child-friendly, peaceful, reverential, no text."
        )
        parent_notes = (
            f"# Parent Notes\n\n"
            f"Source: {plan.source_reference}\n\n"
            "Read slowly and keep the mood sweet, not disciplinary. The focus is Mother Yasoda's loving effort and Krishna's willingness to be bound by bhakti.\n\n"
            "Discussion question: What small service can we do for Krishna and family tomorrow?\n"
        )
        return StoryContent(
            title=plan.title,
            recap="Yesterday we remembered that Krishna protects and loves His devotees. Today we hear how Mother Yasoda's love became stronger than any rope.",
            main_story=main_story,
            moral="Krishna is the Supreme Lord, yet He becomes controlled by pure love. Real bhakti means sincere effort, patience, and service.",
            takeaway="Do one small service with love today. Krishna sees sincerity more than size.",
            five_star_challenge=challenge,
            audio_script=audio_script,
            whatsapp_caption=caption,
            image_prompt=image_prompt,
            parent_notes=parent_notes,
            activity_questions=questions,
            vocabulary_words=vocab,
        )
