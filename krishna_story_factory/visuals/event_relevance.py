"""Event-relevance keyword checks for visual briefs (Phase 8 scaffolding).

A beautiful generic image is a failure when it misses the episode's central event.
Story-specific overrides catch known failure modes without regenerating assets here.
"""
from __future__ import annotations

from typing import Iterable

# Story 009 — Pūtanā nurse/visitor disguise with baby Kṛṣṇa (not garden-only / not horror corpse).
STORY_009_EVENT_KEYWORDS: tuple[str, ...] = (
    "pūtanā",
    "putana",
    "putanā",
    "nurse",
    "visitor",
    "krishna",
    "kṛṣṇa",
    "krsna",
)

# Story 011 — must visibly depict Tṛṇāvarta / whirlwind with Kṛṣṇa (not only Yaśodā + baby).
STORY_011_EVENT_KEYWORDS: tuple[str, ...] = (
    "trinavarta",
    "tṛṇāvarta",
    "trnavarta",
    "whirlwind",
    "krishna",
    "kṛṣṇa",
    "krsna",
)

# Story 020 — Aghāsura serpent/cave danger + Kṛṣṇa's protection (child-safe).
STORY_020_EVENT_KEYWORDS: tuple[str, ...] = (
    "aghasura",
    "aghāsura",
    "serpent",
    "snake",
    "cave",
    "protect",
    "krishna",
    "kṛṣṇa",
    "krsna",
)

STORY_EVENT_RELEVANCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "009": STORY_009_EVENT_KEYWORDS,
    "011": STORY_011_EVENT_KEYWORDS,
    "020": STORY_020_EVENT_KEYWORDS,
}


def _normalize(text: str) -> str:
    return (
        (text or "")
        .lower()
        .replace("\u2019", "'")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )


def _corpus_from_brief_fields(
    *,
    must_include: Iterable[str],
    central_scene: str = "",
    must_avoid: Iterable[str] | None = None,
    extra_text: str = "",
) -> str:
    parts = [central_scene, extra_text, *list(must_include)]
    if must_avoid:
        parts.extend(list(must_avoid))
    return _normalize(" ".join(str(p) for p in parts if p))


def validate_event_relevance_keywords(
    story_no: str,
    *,
    must_include: Iterable[str],
    central_scene: str = "",
    must_avoid: Iterable[str] | None = None,
    extra_text: str = "",
) -> list[str]:
    """Return errors when story-specific event keywords are absent from the brief.

    Only stories with named overrides (009, 011, 020) are checked. Other stories
    return an empty error list from this helper.
    """
    padded = (story_no or "").strip().zfill(3)
    required = STORY_EVENT_RELEVANCE_KEYWORDS.get(padded)
    if not required:
        return []

    corpus = _corpus_from_brief_fields(
        must_include=must_include,
        central_scene=central_scene,
        must_avoid=must_avoid,
        extra_text=extra_text,
    )
    # Group aliases: at least one token from each semantic group must appear.
    # For 009: (Putana) AND (nurse|visitor) AND (Krishna)
    # For 011: (Trinavarta|whirlwind) AND (Krishna|Kṛṣṇa)
    # For 020: (Aghasura) AND (serpent|snake|cave) AND (protect) AND (Krishna)
    if padded == "009":
        groups = (
            ("pūtanā", "putana", "putanā"),
            ("nurse", "visitor", "disguise"),
            ("krishna", "kṛṣṇa", "krsna"),
        )
    elif padded == "011":
        groups = (
            ("trinavarta", "tṛṇāvarta", "trnavarta", "whirlwind"),
            ("krishna", "kṛṣṇa", "krsna"),
        )
    elif padded == "020":
        groups = (
            ("aghasura", "aghāsura"),
            ("serpent", "snake", "cave"),
            ("protect", "protection", "protects", "protected"),
            ("krishna", "kṛṣṇa", "krsna"),
        )
    else:
        groups = (required,)

    errors: list[str] = []
    for group in groups:
        if not any(token in corpus for token in group):
            errors.append(
                f"Story {padded} visual brief missing event-relevance keyword group "
                f"{group!r} in must_include/central_scene (Phase 8)."
            )
    return errors
