from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .models import ActivityPack, MatchingCard, SequenceCard, component_label

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

_METADATA_EVENT_RE = re.compile(
    r"(?is)^(?:---|\s*(?:title|source_reference|scripture_reference|age_range|story_number|format|greeting)\s*:|"
    r"hare\s+k[rṛ][sṣ][nṇ]a,?\s+dear)",
)
_YAML_MARKER_RE = re.compile(r"(?m)^---\s*$|^\s*[a-z_]+\s*:\s*")
_METADATA_KEYS = (
    "title",
    "source_reference",
    "scripture_reference",
    "age_range",
    "story_number",
    "format",
    "greeting",
)
_METADATA_CONCEPTS = frozenset(
    {
        "title",
        "source reference",
        "scripture reference",
        "scripture range",
        "age range",
        "story number",
        "format",
        "greeting",
    }
)


def normalize_metadata_text(text: str) -> str:
    """Case-fold, drop punctuation, turn underscores into spaces for concept matching.

    Inserts word boundaries for camelCase/PascalCase before lowercasing so
    ``sourceReference`` / ``storyNumber`` normalize to metadata concepts.
    """
    cleaned = text or ""
    # sourceREFERENCE → source REFERENCE; SourceReference → Source Reference
    cleaned = re.sub(r"([a-z])([A-Z]+)", r"\1 \2", cleaned)
    cleaned = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", cleaned)
    cleaned = cleaned.lower().replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def contains_metadata_concept(text: str) -> bool:
    """True when a label carries frontmatter concepts after normalization."""
    normalized = f" {normalize_metadata_text(text)} "
    if not normalized.strip():
        return True
    for concept in _METADATA_CONCEPTS:
        if f" {concept} " in normalized or normalized.strip() == concept:
            return True
    # Token-level key leftovers such as "source"+"reference" pairs already covered;
    # also reject lone metadata key tokens that survive tokenization.
    tokens = set(normalized.split())
    if tokens & {"title", "format", "greeting"} and len(tokens) <= 4:
        # Short labels dominated by metadata keys are not story events.
        if tokens <= {"title", "format", "greeting", "source", "reference", "scripture", "range", "age", "story", "number", "in", "the", "pastime"}:
            return True
    return False


def strip_yaml_frontmatter(text: str) -> str:
    """Remove leading --- YAML --- blocks before event extraction."""
    raw = text or ""
    match = re.match(r"(?s)\A\s*---\s*\n.*?\n---\s*\n?", raw)
    if match:
        return raw[match.end() :]
    return raw


def is_metadata_line(text: str) -> bool:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return True
    lower = cleaned.lower()
    if cleaned.startswith("---") or cleaned.startswith("#"):
        return True
    if any(lower.startswith(f"{key}:") or f"{key}:" in lower for key in _METADATA_KEYS):
        return True
    if lower.startswith("hare kṛṣṇa, dear") or lower.startswith("hare krishna, dear"):
        return True
    return contains_metadata_concept(cleaned)


def is_metadata_event_label(text: str) -> bool:
    """True when a label is frontmatter/YAML/greeting/heading rather than a story event."""
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return True
    lower = cleaned.lower()
    if _METADATA_EVENT_RE.search(cleaned):
        return True
    if cleaned.startswith("#"):
        return True
    if any(key in lower for key in (f"{k}:" for k in _METADATA_KEYS)):
        return True
    if lower.startswith("hare kṛṣṇa, dear") or lower.startswith("hare krishna, dear"):
        return True
    if contains_metadata_concept(cleaned):
        return True
    return False


@dataclass(slots=True)
class MatchingCoverageResult:
    expected_pairs: int = 0
    rendered_pairs: int = 0
    missing_labels: list[str] = field(default_factory=list)
    orphan_labels: list[str] = field(default_factory=list)
    left_count: int = 0
    right_count: int = 0
    pass_: bool = True

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


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
            if is_metadata_event_label(label):
                errors.append(f"Metadata/frontmatter label rejected: {label!r}")

        if page.page_type == "STORY_SEQUENCE_CARDS":
            cards = [item for item in page.components if isinstance(item, SequenceCard)]
            if len(cards) < 4:
                errors.append("STORY_SEQUENCE_CARDS requires at least four SequenceCard events.")
            elif any(
                _is_generic_placeholder(card.event)
                or is_metadata_event_label(card.event)
                or len(card.event.strip()) < 8
                for card in cards
            ):
                errors.append("STORY_SEQUENCE_CARDS require concrete story events, not placeholders or metadata.")
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


def matching_coverage_from_pdf_text(activity: ActivityPack, pdf_text: str) -> MatchingCoverageResult:
    """Compare expected MatchingCard labels to extracted PDF text."""
    pairs: list[MatchingCard] = []
    for page in activity.pages:
        if page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
            pairs.extend(item for item in page.components if isinstance(item, MatchingCard))
    if not pairs:
        return MatchingCoverageResult(pass_=True)

    blob = " ".join((pdf_text or "").lower().split())
    lefts = [p.left.strip() for p in pairs]
    rights = [p.right.strip() for p in pairs]
    missing: list[str] = []
    for label in lefts + rights:
        if not _label_in_blob(label, blob):
            missing.append(label)

    # Orphans: PDF should not invent unmatched stub answers when counts differ after truncation.
    left_present = sum(1 for label in lefts if _label_in_blob(label, blob))
    right_present = sum(1 for label in rights if _label_in_blob(label, blob))
    orphans: list[str] = []
    if left_present != right_present:
        orphans.append(f"left/right rendered count mismatch: {left_present} vs {right_present}")
    if left_present < len(lefts):
        orphans.append("incomplete left-column coverage")
    if right_present < len(rights):
        orphans.append("incomplete right-column coverage")

    result = MatchingCoverageResult(
        expected_pairs=len(pairs),
        rendered_pairs=min(left_present, right_present),
        missing_labels=missing,
        orphan_labels=orphans,
        left_count=left_present,
        right_count=right_present,
        pass_=not missing and not orphans and left_present == len(lefts) and right_present == len(rights),
    )
    return result


def retain_matching_coverage_evidence(
    project_root: Path, *, chapter_no: str, coverage: MatchingCoverageResult, pdf_text: str
) -> Path:
    dest = project_root / ".work" / "qa" / str(chapter_no).zfill(3)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "matching_coverage.json").write_text(json.dumps(coverage.to_dict(), indent=2), encoding="utf-8")
    (dest / "activity_pdf_text.txt").write_text(pdf_text or "", encoding="utf-8")
    return dest


def pdf_text_has_generic_placeholders(text: str) -> list[str]:
    blob = " ".join((text or "").lower().split())
    # Only multi-word phrases for PDF text — single tokens like "before"/"helper"
    # appear in ordinary instructions and are handled by semantic component checks.
    hits: list[str] = []
    for label in sorted(p for p in GENERIC_PLACEHOLDERS if " " in p):
        pattern = r"(?<![a-z0-9])" + re.escape(label) + r"(?![a-z0-9])"
        if re.search(pattern, blob):
            hits.append(label)
    return hits


def _label_in_blob(label: str, blob: str) -> bool:
    normalized = " ".join((label or "").lower().split())
    if not normalized:
        return False
    # Allow soft hyphen / wrapping noise by checking contiguous normalized form.
    return normalized in blob


def _is_generic_placeholder(label: str) -> bool:
    normalized = " ".join((label or "").strip().lower().split())
    return (not normalized) or normalized in GENERIC_PLACEHOLDERS


def activity_presentation_errors(activity: ActivityPack, pdf_text_by_page: list[str]) -> list[str]:
    """Fail on cross-page instruction leakage and duplicated age labels."""
    errors: list[str] = []
    for index, text in enumerate(pdf_text_by_page, start=1):
        blob = " ".join((text or "").lower().split())
        if "younger: younger" in blob or "older: older" in blob:
            errors.append(f"Page {index} has duplicated age labels.")
        page = activity.pages[index - 1] if index - 1 < len(activity.pages) else None
        if page and page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
            if "lotus petal" in blob or "draw inside each lotus" in blob:
                errors.append(f"Page {index} matching footer leaks lotus instructions.")
        if page and page.page_type == "PRAYER_WHEEL":
            if "cut-and-match" in blob or "reason for each match" in blob:
                errors.append(f"Page {index} lotus footer leaks matching instructions.")
            if page.layout_hint == "five_lotus_petals":
                if "my lotus" not in blob and "lotus prayer" not in blob:
                    errors.append(f"Page {index} missing lotus prayer title cues.")
            elif "prayer" not in blob and "petal" not in blob and "gratitude" not in blob:
                errors.append(f"Page {index} missing prayer/petal cues.")
    return errors


__all__ = [
    "GENERIC_PLACEHOLDERS",
    "MatchingCoverageResult",
    "contains_metadata_concept",
    "is_metadata_event_label",
    "is_metadata_line",
    "normalize_metadata_text",
    "strip_yaml_frontmatter",
    "semantic_activity_errors",
    "pdf_text_has_generic_placeholders",
    "matching_coverage_from_pdf_text",
    "retain_matching_coverage_evidence",
    "activity_presentation_errors",
]
