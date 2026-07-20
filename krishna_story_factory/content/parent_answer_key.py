"""Structured parent answer keys for activities (manifest + dashboard only)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..activities.models import ActivityPack, MatchingCard, SequenceCard, component_label


OBJECTIVE_PAGE_TYPES = {
    "MATCHING_CARDS",
    "SORTING_CARDS",
    "STORY_SEQUENCE_CARDS",
    "WORD_SEARCH",
    "CROSSWORD",
    "MAZE_OR_PATH",
}

OPEN_ENDED_PAGE_TYPES = {
    "PRAYER_WHEEL",
    "GRATITUDE_GARLAND",
    "DRAW_AND_REFLECT",
    "FAMILY_MISSION",
    "ROLE_PLAY_CARDS",
    "PUPPET_CARDS",
    "EMOTION_MAP",
    "QUICK_DISCUSSION",
    "CUT_AND_BUILD_PARTS",
}


@dataclass(slots=True)
class OpenEndedGuidance:
    prompt: str
    guidance: str
    no_single_correct_answer: bool = True


@dataclass(slots=True)
class ParentAnswerKey:
    matching: list[dict[str, str]] = field(default_factory=list)
    sequence: list[dict[str, Any]] = field(default_factory=list)
    puzzle: dict[str, Any] = field(default_factory=dict)
    open_ended_guidance: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_parent_answer_key(activity: ActivityPack) -> ParentAnswerKey:
    matching: list[dict[str, str]] = []
    sequence: list[dict[str, Any]] = []
    puzzle: dict[str, Any] = {}
    open_ended: list[dict[str, Any]] = []

    for page in activity.pages:
        if page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
            for card in page.components:
                if isinstance(card, MatchingCard):
                    matching.append({"left": card.left, "right": card.right, "pair_id": card.pair_id or ""})
        elif page.page_type == "STORY_SEQUENCE_CARDS":
            cards = [c for c in page.components if isinstance(c, SequenceCard)]
            for card in sorted(cards, key=lambda c: c.source_order):
                sequence.append({"order": card.source_order, "event": card.event})
        elif page.page_type == "WORD_SEARCH":
            words = [component_label(c) for c in page.components]
            puzzle["word_search"] = {"words": words}
        elif page.page_type in OPEN_ENDED_PAGE_TYPES:
            for component in page.components:
                label = component_label(component).strip()
                if not label:
                    continue
                open_ended.append(
                    {
                        "prompt": label,
                        "guidance": (
                            "No single correct answer. Help the child respond in a safe, "
                            "devotional way connected to tonight's pastime."
                        ),
                        "no_single_correct_answer": True,
                    }
                )

    # Prefer chronological answer_key when sequence cards exist but printed order differs.
    if not sequence and activity.answer_key:
        sequence = [{"order": i + 1, "event": event} for i, event in enumerate(activity.answer_key)]

    return ParentAnswerKey(
        matching=matching,
        sequence=sequence,
        puzzle=puzzle,
        open_ended_guidance=open_ended,
    )


def validate_parent_answer_key(activity: ActivityPack, key: ParentAnswerKey | dict[str, Any]) -> list[str]:
    data = key.to_dict() if isinstance(key, ParentAnswerKey) else dict(key or {})
    errors: list[str] = []
    matching_cards = [
        c
        for page in activity.pages
        if page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}
        for c in page.components
        if isinstance(c, MatchingCard)
    ]
    if matching_cards and len(data.get("matching") or []) != len(matching_cards):
        errors.append(
            f"parent_answer_key.matching count {len(data.get('matching') or [])} "
            f"!= rendered matching pairs {len(matching_cards)}"
        )
    sequence_cards = [
        c
        for page in activity.pages
        if page.page_type == "STORY_SEQUENCE_CARDS"
        for c in page.components
        if isinstance(c, SequenceCard)
    ]
    if sequence_cards and len(data.get("sequence") or []) != len(sequence_cards):
        errors.append(
            f"parent_answer_key.sequence count {len(data.get('sequence') or [])} "
            f"!= rendered sequence cards {len(sequence_cards)}"
        )
    open_pages = [p for p in activity.pages if p.page_type in OPEN_ENDED_PAGE_TYPES]
    if open_pages:
        guidance = data.get("open_ended_guidance") or []
        if not guidance:
            errors.append("open-ended activity pages require open_ended_guidance")
        elif any(not item.get("no_single_correct_answer", False) for item in guidance):
            errors.append("open_ended_guidance items must set no_single_correct_answer=true")
    return errors


def render_parent_answer_key_text(key: ParentAnswerKey | dict[str, Any], *, title: str = "") -> str:
    data = key.to_dict() if isinstance(key, ParentAnswerKey) else dict(key or {})
    lines = [f"Parent Answer Key — {title}".strip(" —"), ""]
    matching = data.get("matching") or []
    if matching:
        lines.append("Matching")
        for item in matching:
            lines.append(f"- {item.get('left', '')} → {item.get('right', '')}")
        lines.append("")
    sequence = data.get("sequence") or []
    if sequence:
        lines.append("Sequence (correct order)")
        for item in sequence:
            lines.append(f"{item.get('order', '')}. {item.get('event', '')}")
        lines.append("")
    puzzle = data.get("puzzle") or {}
    if puzzle:
        lines.append("Puzzle")
        lines.append(str(puzzle))
        lines.append("")
    guidance = data.get("open_ended_guidance") or []
    if guidance:
        lines.append("Open-ended guidance")
        for item in guidance:
            lines.append(f"- Prompt: {item.get('prompt', '')}")
            lines.append(f"  Guidance: {item.get('guidance', '')}")
        lines.append("")
    lines.append("This key is for parents/teachers only. It is not part of the child Drive package.")
    return "\n".join(lines).strip() + "\n"


__all__ = [
    "ParentAnswerKey",
    "OpenEndedGuidance",
    "build_parent_answer_key",
    "validate_parent_answer_key",
    "render_parent_answer_key_text",
    "OBJECTIVE_PAGE_TYPES",
    "OPEN_ENDED_PAGE_TYPES",
]
