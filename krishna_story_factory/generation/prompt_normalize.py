from __future__ import annotations

from ..models import PlanRow, StoryContent

_STORY_CARD_STYLE = (
    "Ultra-realistic 3D devotional cinematic illustration, refined child-safe devotional painting quality, "
    "warm sacred lighting, clear focal scene, expressive Indian faces, no modern objects, "
    "no distorted hands or faces, not crowded."
)

_COLORING_STYLE = (
    "Premium children's devotional coloring-book illustration, cute sweet expressive faces, centered composition, "
    "no cropping, full scene inside safe margins, thick confident black outlines, white background, "
    "large colorable spaces, minimal tiny ornaments, no gray shading, no clutter, no stiff adult faces, "
    "simple lotus or flower border where appropriate, ages 6-12, something a child would proudly put on a wall."
)

_CHAPTER_CARD_HINTS: dict[str, str] = {
    "002": (
        "Devaki and Vasudeva seated in a golden wedding chariot, Kamsa driving as charioteer, "
        "heavenly voice suggested by soft divine light from sky, ancient Mathura wedding atmosphere, "
        "flower garlands and petals, mood joy changing into wonder and concern."
    ),
}

_CHAPTER_COLORING_HINTS: dict[str, str] = {
    "002": (
        "Devaki and Vasudeva seated together in a decorated wedding chariot, Kamsa as charioteer in front, "
        "two friendly horses, simple Mathura palace arch in background, soft divine light as simple rays or cloud above, "
        "flower garlands and petals, no weapon, no frightening expressions, no cramped composition."
    ),
}


def normalize_image_prompts(content: StoryContent, plan: PlanRow) -> StoryContent:
    square = _ensure_story_card_square_prompt(
        content.story_card_square_prompt or content.hero_image_prompt or content.image_prompt,
        plan,
    )
    wide = _ensure_story_card_square_prompt(
        content.story_card_wide_prompt or square,
        plan,
    )
    hero = _ensure_story_card_square_prompt(content.hero_image_prompt or content.image_prompt or square, plan)
    line_art = _ensure_coloring_prompt(content.line_art_prompt, plan)
    coloring = _ensure_coloring_prompt(content.coloring_page_prompt or line_art, plan)
    return StoryContent(
        title=content.title,
        recap=content.recap,
        main_story=content.main_story,
        moral=content.moral,
        takeaway=content.takeaway,
        five_star_challenge=content.five_star_challenge,
        audio_script=content.audio_script,
        whatsapp_caption=content.whatsapp_caption,
        image_prompt=hero,
        line_art_prompt=line_art,
        story_card_text=content.story_card_text,
        parent_notes=content.parent_notes,
        hero_image_prompt=hero,
        story_card_square_prompt=square,
        story_card_wide_prompt=wide,
        coloring_page_prompt=coloring,
        recall_questions=content.recall_questions,
        thinking_questions=content.thinking_questions,
        word_search_words=content.word_search_words,
        draw_activity=content.draw_activity,
        family_activity=content.family_activity,
    )


def _ensure_story_card_square_prompt(prompt: str, plan: PlanRow) -> str:
    text = prompt.strip()
    if not text:
        text = f"1080x1080 devotional story card scene from {plan.title}."
    lower = text.lower()
    if "1080" not in lower and "square" not in lower:
        text = f"1080x1080 square card. {text}"
    chapter_hint = _CHAPTER_CARD_HINTS.get(plan.chapter_no, "")
    if chapter_hint and chapter_hint.lower() not in lower:
        text = f"{text} {chapter_hint}"
    style_lower = _STORY_CARD_STYLE.lower()
    for fragment in (
        "ultra-realistic 3d devotional cinematic",
        "refined child-safe devotional painting quality",
        "warm sacred lighting",
        "clear focal scene",
        "expressive indian faces",
        "no modern objects",
        "no distorted hands",
        "not crowded",
    ):
        if fragment not in lower and fragment not in style_lower:
            continue
    if not any(term in lower for term in ("ultra-realistic", "ultra realistic", "3d devotional", "3d")):
        text += " Ultra-realistic 3D devotional cinematic illustration."
    if "devotional" not in lower:
        text += " Refined child-safe devotional painting quality."
    if "cinematic" not in lower:
        text += " Cinematic warm sacred lighting."
    if "no modern objects" not in lower:
        text += " No modern objects."
    if not any(term in lower for term in ("not crowded", "clear focal")):
        text += " Clear focal scene, expressive Indian faces, not crowded."
    if "distorted" not in lower:
        text += " No distorted hands or faces."
    return text.strip()


def _ensure_coloring_prompt(prompt: str, plan: PlanRow) -> str:
    text = prompt.strip()
    if not text:
        text = f"Devotional Krishna coloring page scene from {plan.title}."
    lower = text.lower()
    chapter_hint = _CHAPTER_COLORING_HINTS.get(plan.chapter_no, "")
    if chapter_hint and chapter_hint.lower() not in lower:
        text = f"{text} {chapter_hint}"
    required_fragments = {
        "centered composition": " Centered composition.",
        "no cropping": " No cropping.",
        "large colorable spaces": " Large colorable spaces.",
        "white background": " White background.",
        "thick": " Thick confident black outlines.",
        "outline": " Thick confident black outlines.",
    }
    for key, suffix in required_fragments.items():
        if key not in lower:
            text += suffix
            lower = text.lower()
    if not any(term in lower for term in ("cute", "sweet expressive faces", "sweet")):
        text += " Cute sweet expressive faces."
    if "premium" not in lower and "coloring-book" not in lower:
        text += " Premium children's devotional coloring-book illustration."
    if "no gray" not in lower and "no clutter" not in lower:
        text += " No gray shading, no clutter."
    return text.strip()
