from __future__ import annotations

from ..models import PlanRow, StoryContent

_STORY_002_BANNED_PHRASES = (
    "kamsa, the king of mathura",
    "king kamsa",
    "kamsa the king",
)

_UNRELATED_PASTIMES = (
    "gajendra",
    "prahlad",
    "prahlada",
    "damodara",
    "fruit seller",
    "fruit-seller",
)


def run_source_guard(plan: PlanRow, content: StoryContent) -> list[str]:
    errors: list[str] = []
    combined = f"{content.recap}\n{content.main_story}\n{content.audio_script}".lower()

    if plan.chapter_no == "002":
        for phrase in _STORY_002_BANNED_PHRASES:
            if phrase in combined:
                errors.append(
                    f"Story 002 must not call Kamsa king yet (found: {phrase!r}). "
                    "Use 'Devaki's powerful brother' or 'a prince of the royal family'."
                )
        for pastime in _UNRELATED_PASTIMES:
            if pastime in combined:
                errors.append(f"Story 002 must not reference unrelated pastime: {pastime}")

    return errors
