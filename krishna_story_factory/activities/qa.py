from __future__ import annotations

from .models import ActivityPack, SequenceCard, component_label

GENERIC_PLACEHOLDERS = frozenset(
    {
        "story begins",
        "a problem appears",
        "a helpful choice",
        "the turning point",
        "the result",
        "the lesson",
        "event 1",
        "event 2",
        "main character",
        "helper",
        "important object",
        "before",
        "after",
    }
)


def semantic_activity_errors(pack: ActivityPack) -> list[str]:
    """Hard-reject generic / incomplete ActivityPack designs before vision QA."""
    errors: list[str] = []
    if not pack.age_variants.get("ages_6_8") or not pack.age_variants.get("ages_9_13"):
        errors.append("age_variants must include ages_6_8 and ages_9_13.")

    for page in pack.pages:
        if not (page.story_connection or "").strip():
            errors.append(f"Page '{page.page_title}' missing story_connection.")
        for component in page.components:
            label = component_label(component).strip()
            if _is_generic_placeholder(label):
                errors.append(f"Generic placeholder label rejected: {label!r}")

        if page.page_type == "STORY_SEQUENCE_CARDS":
            cards = [item for item in page.components if isinstance(item, SequenceCard)]
            if len(cards) < 4:
                errors.append("STORY_SEQUENCE_CARDS requires at least four SequenceCard events.")
            elif any(_is_generic_placeholder(card.event) or len(card.event.strip()) < 8 for card in cards):
                errors.append("STORY_SEQUENCE_CARDS require concrete story events, not placeholders.")
            else:
                printed = [card.event for card in cards]
                chronological = [card.event for card in sorted(cards, key=lambda c: c.source_order)]
                if printed == chronological:
                    errors.append(
                        "STORY_SEQUENCE_CARDS must be shuffled (printed order != chronological source_order)."
                    )
                if len({card.source_order for card in cards}) != len(cards):
                    errors.append("STORY_SEQUENCE_CARDS source_order values must be unique.")

    printed_labels = list(pack.printable_components)
    if pack.answer_key and printed_labels and pack.answer_key == printed_labels:
        errors.append("answer_key must not equal the printed component order labels.")

    return errors


def pdf_text_has_generic_placeholders(text: str) -> list[str]:
    import re

    blob = " ".join((text or "").lower().split())
    # Only multi-word phrases for PDF text — single tokens like "before"/"helper"
    # appear in ordinary instructions and are handled by semantic component checks.
    hits: list[str] = []
    for label in sorted(p for p in GENERIC_PLACEHOLDERS if " " in p):
        pattern = r"(?<![a-z0-9])" + re.escape(label) + r"(?![a-z0-9])"
        if re.search(pattern, blob):
            hits.append(label)
    return hits


def _is_generic_placeholder(label: str) -> bool:
    normalized = " ".join((label or "").strip().lower().split())
    return (not normalized) or normalized in GENERIC_PLACEHOLDERS


__all__ = ["GENERIC_PLACEHOLDERS", "semantic_activity_errors", "pdf_text_has_generic_placeholders"]
