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

_STORY_001_BANNED = (
    "devaki and vasudeva",
    "devaki's wedding",
    "kamsa prophecy",
    "kamsa heard",
    "fruit seller",
    "gajendra",
    "prahlad",
    "prahlada",
    "damodara",
    "gokula festival",
    "putana",
    "birth of krishna in the prison",
    "vasudeva crosses",
    "nanda maharaja celebrates",
)

_STORY_001_REQUIRED_THEMES = (
    "earth",
    "brahma",
    "prayer",
    "vishnu",
)


def run_source_guard(plan: PlanRow, content: StoryContent) -> list[str]:
    errors: list[str] = []
    combined = f"{content.recap}\n{content.main_story}\n{content.audio_script}".lower()

    if plan.chapter_no == "001":
        for phrase in _STORY_001_BANNED:
            if phrase in combined:
                errors.append(f"Story 001 must not include unrelated pastime content: {phrase!r}")
        for pastime in _UNRELATED_PASTIMES:
            if pastime in combined:
                errors.append(f"Story 001 must not reference unrelated pastime: {pastime}")
        if not any(theme in combined for theme in _STORY_001_REQUIRED_THEMES):
            errors.append("Story 001 should reference Earth, Brahma, prayer, or Vishnu.")

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
