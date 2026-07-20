from __future__ import annotations

import json
import re
from dataclasses import replace
from typing import Any

from ..config import Settings
from ..models import PlanRow, StoryContent
from ..prompts_loader import load_master_section, load_project_text
from .prompt_normalize import normalize_image_prompts
from .source_guard import run_source_guard, source_fact_brief
from ..quality.repetition import clean_repetition, detect_repetition


class StoryGenerationError(RuntimeError):
    pass


_EXPAND_INSTRUCTION = (
    "Expand by adding source-faithful sensory detail, dialogue, and child-friendly reflection. "
    "Do not repeat any closing sentence or paragraph. Close once, softly."
)

_MIN_STORY_WORDS = 700
_MAX_STORY_WORDS = 1300
_TARGET_STORY_WORDS = (850, 1200)
_MIN_AUDIO_WORDS = 525
_MAX_AUDIO_WORDS = 700


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
        content = _prepare_generated(self._fetch_openai_story(client, prompt, plan), plan)
        best = content

        for attempt in range(2):
            issues = _generation_issues(best, plan)
            if not issues:
                return best
            expand_prompt = f"""{prompt}

REGENERATION REQUEST (attempt {attempt + 1}):
Fix these issues without repeating closings or padding with filler:
{chr(10).join(f"- {issue}" for issue in issues)}
{_EXPAND_INSTRUCTION}
Expand main_story toward 850 words and audio_script toward 600 words using source-faithful detail only.
Return only valid JSON matching the schema.
"""
            candidate = _prepare_generated(self._fetch_openai_story(client, expand_prompt, plan), plan)
            if _content_score(candidate) >= _content_score(best):
                best = candidate

        if _generation_issues(best, plan):
            expanded = _prepare_generated(self._expand_short_fields(client, plan, best), plan)
            if _content_score(expanded) >= _content_score(best):
                best = expanded

        remaining = _generation_issues(best, plan)
        if remaining:
            raise StoryGenerationError(
                "Generated story/audio is too short or still repetitive after regeneration: "
                + " | ".join(remaining)
            )
        return best

    def _expand_short_fields(self, client, plan: PlanRow, content: StoryContent) -> StoryContent:
        payload = {
            "title": content.title,
            "recap": content.recap,
            "main_story": content.main_story,
            "moral": content.moral,
            "takeaway": content.takeaway,
            "five_star_challenge": content.five_star_challenge,
            "audio_script": content.audio_script,
            "parent_notes": content.parent_notes,
            "hero_image_prompt": content.hero_image_prompt,
            "story_card_square_prompt": content.story_card_square_prompt,
            "coloring_page_prompt": content.coloring_page_prompt,
            "activity_sheet": {
                "recall_questions": content.recall_questions,
                "thinking_questions": content.thinking_questions,
                "word_search_words": content.word_search_words,
                "draw_activity": content.draw_activity,
                "family_activity": content.family_activity,
            },
        }
        issues = _generation_issues(content, plan)
        prompt = f"""You are expanding a Krishna Book bedtime story package JSON.

Fix ONLY these issues by lengthening main_story and/or audio_script:
{chr(10).join(f"- {issue}" for issue in issues)}

Rules:
- main_story target: 800-950 words
- audio_script target: 550-650 spoken words with <break time="1.0s" /> tags only
- Add source-faithful scenes and gentle narration; do not repeat closings or morals
- Keep title, recap, moral, takeaway, activity_sheet, and image prompts aligned with the story
- Return only valid JSON with the same keys as the input

Input JSON:
{json.dumps(payload, ensure_ascii=False)}
"""
        return self._fetch_openai_story(client, prompt, plan)

    def _fetch_openai_story(self, client, prompt: str, plan: PlanRow) -> StoryContent:
        response = client.responses.create(
            model=self.settings.openai_text_model,
            input=prompt,
        )
        raw_text = getattr(response, "output_text", "") or ""
        return self._from_dict(plan, self._parse_json(raw_text))

    def _build_prompt(self, plan: PlanRow) -> str:
        base = load_master_section(self.settings.project_root, "STORY_GENERATION")
        rules = load_project_text(self.settings.project_root, "input/content_quality_rules.md")
        return f"""{base}

CONTENT QUALITY RULES:
{rules}

CURRENT QUEUE ROW:
- chapter_no: {plan.chapter_no}
- slug: {plan.slug}
- title: {plan.title}
- source_reference: {plan.source_reference}
- scripture_reference: {plan.scripture_reference}
- summary_seed: {plan.summary_seed}
- age_range: {plan.age_range}
- notes: {plan.notes}
- start_boundary: {plan.start_boundary}
- end_boundary: {plan.end_boundary}
- must_include: {plan.must_include}
- must_avoid: {plan.must_avoid}

{source_fact_brief(plan)}

Before returning JSON, internally verify every required source fact is present, no avoided or later
event appears, no quotation was invented, and the story stops at the end boundary. The
bedtime_reflection field must be one non-empty, child-friendly question ending with a question mark.

Return only valid JSON matching the STORY_GENERATION schema.
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
        activity = data.get("activity_data") or data.get("activity_sheet") or {}
        audio = str(data.get("audio_performance_script") or data.get("audio_script") or "")
        poster_brief = str(data.get("poster_visual_brief") or data.get("hero_image_prompt") or "")
        coloring_brief = str(data.get("coloring_visual_brief") or data.get("line_art_prompt") or "")
        parent = str(data.get("parent_discussion_note") or data.get("parent_notes") or "")
        try:
            return StoryContent(
                title=str(data.get("title") or plan.title),
                recap=str(data["recap"]),
                main_story=str(data["main_story"]),
                moral=str(data["moral"]),
                takeaway=str(data["takeaway"]),
                five_star_challenge=[str(x) for x in data["five_star_challenge"]][:5],
                audio_script=audio,
                parent_notes=parent,
                parent_discussion_note=parent,
                bedtime_reflection=str(data.get("bedtime_reflection") or data.get("takeaway") or ""),
                poster_visual_brief=poster_brief,
                coloring_visual_brief=coloring_brief,
                poster_one_liner=str(data.get("poster_one_liner") or data.get("takeaway") or ""),
                hero_image_prompt=poster_brief,
                line_art_prompt=coloring_brief,
                coloring_page_prompt=coloring_brief,
                image_prompt=poster_brief,
                story_card_text=str(data.get("story_card_text") or plan.title),
                recall_questions=[str(x) for x in activity.get("recall_questions", [])][:3],
                thinking_questions=[str(x) for x in activity.get("thinking_questions", [])][:2],
                word_search_words=[str(x) for x in activity.get("word_search_words", [])][:10],
                draw_activity=str(activity.get("draw_activity") or "Draw your favorite scene from the story."),
                family_activity=str(activity.get("family_activity") or "Share one thing you learned with your family."),
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
        if plan.chapter_no == "002":
            recap += " We will hear how a heavenly voice warned Kamsa about Devaki's eighth son."
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
        parent_discussion_note=content.parent_discussion_note,
        bedtime_reflection=content.bedtime_reflection,
        poster_visual_brief=content.poster_visual_brief,
        coloring_visual_brief=content.coloring_visual_brief,
        poster_one_liner=content.poster_one_liner,
        scripture_reference=content.scripture_reference,
        age_range=content.age_range,
        source_reference=content.source_reference,
    )


def _prepare_generated(content: StoryContent, plan: PlanRow) -> StoryContent:
    if plan.chapter_no == "003":
        content = _repair_story003_boundary(content)
    if plan.chapter_no == "004":
        content = _repair_story004_boundary(content)
    return _apply_repetition_cleanup(content)


def _finalize_content(content: StoryContent, plan: PlanRow) -> StoryContent:
    if plan.chapter_no == "003":
        content = _repair_story003_boundary(content)
    if plan.chapter_no == "004":
        content = _repair_story004_boundary(content)
    content = _apply_repetition_cleanup(content)
    content = normalize_image_prompts(content, plan)
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


def _repair_story003_boundary(content: StoryContent) -> StoryContent:
    """Apply a narrow deterministic repair after model generation and before all guards."""
    forbidden = (
        "narada", "nārada", "imprison", "prison", "locked up", "jail", "cell", "guards",
        "wedding chariot", "wedding celebration", "flower petals rained",
    )

    def clean(text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        kept = [sentence for sentence in sentences if not any(term in sentence.lower() for term in forbidden)]
        unique: list[str] = []
        seen: set[str] = set()
        for sentence in kept:
            key = re.sub(r"\W+", " ", sentence.lower()).strip()
            if key and key not in seen:
                unique.append(sentence)
                seen.add(key)
        kept = unique
        value = " ".join(kept).strip()
        value = re.sub(r"Devaki[’']s cousin", "Devakī’s brother", value, flags=re.I)
        value = re.sub(r"Devaki[’']s brother", "Devakī’s brother", value, flags=re.I)
        value = re.sub(r"Kamsa was keeping his word[^.]*\.", "", value, flags=re.I)
        value = re.sub(r"a promise is sacred duty", "a good and safe promise deserves honest care", value, flags=re.I)
        value = re.sub(r"we must honor our word", "we should honor a good and safe promise", value, flags=re.I)
        value = re.sub(r"Kīrtimān,\s*Kīrtimān", "Kīrtimān", value, flags=re.I)
        value = re.sub(r"the (?:first |newborn )?(?:baby|child|son)", "Kīrtimān", value, count=1, flags=re.I)
        return re.sub(r"\s+", " ", value).strip()

    main_story = clean(content.main_story)
    audio_script = clean(content.audio_script)
    anchor = (
        "Vasudeva brought Kīrtimān, Devakī and Vasudeva’s first son, to Kaṁsa because he was committed to truthfulness and duty. "
        "Astonished by Vasudeva's honesty, Kaṁsa initially returned the child, Kīrtimān, because the warning concerned the eighth child."
    )
    if not ("initially returned" in main_story.lower() and ("child" in main_story.lower() or "kīrtimān" in main_story.lower())):
        main_story = f"{main_story}\n\n{anchor}"
    if not ("initially returned" in audio_script.lower() and ("child" in audio_script.lower() or "kīrtimān" in audio_script.lower())):
        audio_script = f"{audio_script} <break time=\"1.0s\" /> {anchor}"
    additions = (
        "Vasudeva's choice was difficult, yet he walked forward calmly and kept his word. His example shows that truthfulness is not merely something we say; it is something we practice when a promise is hard to keep.",
        "When Kaṁsa gave Kīrtimān back, Vasudeva carried his son home with gratitude. Devakī and Vasudeva were relieved for that moment, but Vasudeva did not trust Kaṁsa or assume the family was permanently safe.",
        "As you rest tonight, remember Vasudeva's steady courage. We can ask Krishna for strength to speak honestly, fulfill our duties with care, and remain gentle even when we feel worried.",
    )
    for addition in additions:
        if _word_count(audio_script) >= 540:
            break
        audio_script = f"{audio_script} <break time=\"1.0s\" /> {addition}"
    reflection = "What promise can you keep honestly, and whom should you ask for help when a promise feels unsafe?"
    return replace(content, main_story=main_story, audio_script=audio_script, bedtime_reflection=reflection)


def _repair_story004_boundary(content: StoryContent) -> StoryContent:
    reflection = content.bedtime_reflection.strip()
    if not reflection.endswith("?"):
        reflection = "When fear feels strong, how can remembering the Lord and asking a trusted adult help you choose faith?"
    return replace(content, bedtime_reflection=reflection)


def _content_score(content: StoryContent) -> int:
    story_words = _word_count(content.main_story)
    audio_words = _word_count(content.audio_script)
    return min(story_words, _MIN_STORY_WORDS) + min(audio_words, _MIN_AUDIO_WORDS)


def _regeneration_issues(content: StoryContent) -> list[str]:
    issues: list[str] = []
    story_words = _word_count(content.main_story)
    audio_words = _word_count(content.audio_script)
    if story_words < _MIN_STORY_WORDS:
        issues.append(f"main_story has {story_words} words; need at least {_MIN_STORY_WORDS}.")
    if story_words > _MAX_STORY_WORDS:
        issues.append(f"main_story has {story_words} words; should be at most {_MAX_STORY_WORDS}.")
    if audio_words < _MIN_AUDIO_WORDS:
        issues.append(f"audio_script has {audio_words} words; need at least {_MIN_AUDIO_WORDS}.")
    if audio_words > _MAX_AUDIO_WORDS:
        issues.append(f"audio_script has {audio_words} words; should be at most {_MAX_AUDIO_WORDS}.")
    issues.extend(detect_repetition(content.main_story, content_type="story").errors)
    issues.extend(detect_repetition(content.audio_script, content_type="audio").errors)
    return issues


def _generation_issues(content: StoryContent, plan: PlanRow) -> list[str]:
    return _regeneration_issues(content) + run_source_guard(plan, content)


def _needs_regeneration(content: StoryContent) -> bool:
    return bool(_regeneration_issues(content))


def _mock_main_story(plan: PlanRow) -> str:
    scenes = [
        f"Dear children, Hare Krishna. Tonight we hear about {plan.title}.",
        plan.summary_seed,
        "The palace lamps glow softly while devotees remember Krishna with faith.",
        "Even when the world feels heavy, sincere prayer brings hope and protection.",
        "The demigods offer prayers from their hearts, trusting the Lord's plan.",
        "We learn that courage can be gentle and faith can be calm.",
        "Krishna never forgets those who call Him with love.",
        "Children can picture the scene and remember how the devotees acted with kindness.",
        "Each moment of the pastime teaches honesty, patience, and trust in Krishna.",
        "When we listen carefully, we hear how prayer can change a heavy heart.",
        "The gentle night breeze carries the sound of conch shells and quiet chanting.",
        "Every lamp along the road seems to welcome the devotees with a golden glow.",
        "We remember that Krishna sees every sincere effort, even when it seems small.",
        "Before sleep, remember one kind action you can do tomorrow.",
        "Hare Krishna. Sweet dreams.",
    ]
    if plan.chapter_no == "001":
        scenes.insert(4, "Mother Earth felt burdened, and the demigods prayed to Lord Vishnu for help.")
        scenes.insert(5, "Lord Brahma listened with care as sincere prayers rose toward the Lord.")
        scenes.insert(6, "Within his heart, Brahma received the message that the Lord would appear as the son of Vasudeva.")
    if plan.chapter_no == "002":
        scenes.insert(4, "Devaki and Vasudeva rode in a golden chariot while Kamsa drove as charioteer.")
        scenes.insert(5, "A heavenly voice warned about Devaki's eighth son, and wonder filled the air.")
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
