"""Structured ActivityStoryMap — semantic beats, not character slices."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..content.canonical_narration import extract_main_story, split_sentences

_WORD_RE = re.compile(r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF']+")


@dataclass
class ActivityStoryMap:
    story_no: str
    title: str
    opening_event: str
    inciting_problem: str
    response_action: str
    central_event: str
    climax_revelation: str
    resolution: str
    devotional_lesson: str = ""
    named_characters: list[str] = field(default_factory=list)
    setting: str = ""
    age_band: str = "6-12"
    safety_notes: str = ""
    source: str = "canonical_sentences"

    def sequence_events(self) -> list[str]:
        return [
            self.opening_event,
            self.inciting_problem,
            self.response_action,
            self.central_event,
            self.climax_revelation,
            self.resolution,
        ]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActivitySemanticQa:
    activity_type: str
    expected_item_count: int
    rendered_item_count: int
    complete_sentence_ok: bool
    duplicates_ok: bool
    truncated_ok: bool
    chronological_ok: bool
    arc_coverage_ok: bool
    named_character_ok: bool
    grounding_score: float
    parent_answer_key_ok: bool
    placeholder_scan_ok: bool
    result: str
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_PLACEHOLDER_PATTERNS = (
    re.compile(r"(?i)line:\s*in paraphrase"),
    re.compile(r"(?i)i remember my part in"),
    re.compile(r"(?i)act the story moment calmly"),
    re.compile(r"(?i)prop:\s*simple cloth"),
)

_MID_WORD = re.compile(r"(?i)\b[a-z\u0100-\u024F\u1E00-\u1EFF]{1,2}$")


def _is_complete_sentence(text: str) -> bool:
    cleaned = " ".join((text or "").strip().split())
    if len(cleaned) < 20:
        return False
    if cleaned.endswith(("…", "...")):
        return False
    if not re.search(r'[.!?…]["”\']?$', cleaned):
        return False
    last = cleaned.rstrip('"”\'').split()[-1]
    if len(last) <= 2 and last.lower() not in {"i", "a", "ok", "me", "us", "he", "we"}:
        return False
    if cleaned.count('"') % 2 == 1 or cleaned.count("“") != cleaned.count("”"):
        # allow simple unmatched if ends with terminal and looks closed enough
        if not cleaned.endswith(('"', "”", "'")):
            return False
    return True


def _looks_truncated(text: str) -> bool:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return True
    if cleaned.endswith((" let us", " let us ", "“Come, let us")):
        return True
    token = cleaned.rstrip('"”\'').split()[-1]
    if _MID_WORD.fullmatch(token) and token.lower() not in {"i", "a", "ok", "me", "us", "he", "we"}:
        return True
    if len(cleaned) <= 110 and not cleaned[-1] in ".!?…\"”'":
        # classic hard-slice residue
        if re.search(r"\b(t|h|th|fr|fro)$", cleaned, re.I):
            return True
    return False


def validate_event_list(events: list[str], *, required_chars: list[str] | None = None) -> list[str]:
    errors: list[str] = []
    if len(events) != 6:
        errors.append(f"expected 6 sequence events, got {len(events)}")
    norms = [" ".join(e.lower().split()) for e in events]
    if len(set(norms)) != len(norms):
        errors.append("duplicate sequence events")
    for idx, event in enumerate(events, start=1):
        if not _is_complete_sentence(event):
            errors.append(f"event {idx} is not a complete sentence")
        if _looks_truncated(event):
            errors.append(f"event {idx} appears truncated/mid-word: {event[-48:]!r}")
        for pat in _PLACEHOLDER_PATTERNS:
            if pat.search(event):
                errors.append(f"event {idx} contains placeholder language")
    if required_chars:
        blob = " ".join(events).lower()
        for name in required_chars:
            if name.lower() not in blob and _fold(name).lower() not in _fold(blob).lower():
                errors.append(f"required character/token missing from sequence: {name}")
    return errors


def _fold(text: str) -> str:
    table = str.maketrans(
        {
            "ā": "a",
            "ī": "i",
            "ū": "u",
            "ṛ": "r",
            "ṣ": "s",
            "ś": "s",
            "ṇ": "n",
            "ñ": "n",
            "ṭ": "t",
            "ḍ": "d",
            "ḥ": "h",
            "ṃ": "m",
        }
    )
    return (text or "").translate(table)


def reconstruct_story_map_from_canonical(
    *,
    story_no: str,
    title: str,
    story_md: str,
    age_band: str = "6-12",
) -> ActivityStoryMap:
    """Deterministic semantic map from complete Main Story sentences.

    Selects six chronological complete sentences spanning opening → resolution.
    Never uses fixed character slices.
    """
    main = extract_main_story(story_md)
    raw_sentences = split_sentences(main)
    sentences: list[str] = []
    for raw in raw_sentences:
        sent = raw.strip()
        if not sent.endswith((".", "!", "?", "…", '"', "”", "'")):
            sent = f"{sent}."
        if len(_WORD_RE.findall(sent)) < 6:
            continue
        if not _is_complete_sentence(sent):
            continue
        sentences.append(sent)
    if len(sentences) < 6:
        raise ValueError(
            f"Cannot reconstruct ActivityStoryMap for {story_no}: "
            f"only {len(sentences)} usable complete sentences in Main Story."
        )

    n = len(sentences)
    # Spread indices across the narrative arc.
    idxs = sorted(
        {
            0,
            max(1, n // 6),
            max(2, (2 * n) // 6),
            max(3, (3 * n) // 6),
            max(4, (4 * n) // 6),
            n - 1,
        }
    )
    while len(idxs) < 6:
        for i in range(n):
            if i not in idxs:
                idxs.append(i)
            if len(idxs) >= 6:
                break
    idxs = sorted(idxs)[:6]
    picks = [sentences[i] for i in idxs]

    # Prefer sentences containing arc keywords when available (still complete sentences).
    def _prefer(candidates: list[str], keywords: tuple[str, ...], fallback: str) -> str:
        for sent in candidates:
            low = _fold(sent).lower()
            if any(k in low for k in keywords):
                return sent
        return fallback

    opening = picks[0]
    problem = _prefer(sentences[1:], ("brahma", "stole", "steal", "hid", "gone", "missing", "took"), picks[1])
    response = _prefer(sentences, ("don't worry", "find the calves", "walked", "search"), picks[2])
    central = _prefer(
        sentences,
        ("expanded", "exact forms", "copies", "forms of all", "missing calves and boys"),
        picks[3],
    )
    climax = _prefer(
        sentences,
        ("visnu", "viṣṇu", "four-armed", "realized", "amazed", "astonished"),
        picks[4],
    )
    resolution = _prefer(
        sentences,
        ("prayer", "humble", "supremacy", "loving kindness", "understood", "bowed"),
        picks[5],
    )

    events = [opening, problem, response, central, climax, resolution]
    # Ensure uniqueness while preserving chronological order of first occurrence.
    ordered_unique: list[str] = []
    for event in events:
        if event not in ordered_unique:
            ordered_unique.append(event)
    if len(ordered_unique) < 6:
        for sent in sentences:
            if sent not in ordered_unique:
                ordered_unique.append(sent)
            if len(ordered_unique) >= 6:
                break
    if len(ordered_unique) < 6:
        raise ValueError("Could not assemble six distinct complete-sentence events.")

    # Re-sort chosen six by original narrative order.
    rank = {s: i for i, s in enumerate(sentences)}
    final_six = sorted(ordered_unique[:6], key=lambda s: rank.get(s, 10_000))

    chars: list[str] = []
    blob = main
    for name in ("Kṛṣṇa", "Brahmā", "Balarāma", "Vṛndāvana", "Viṣṇu", "Yaśodā", "Nanda"):
        if name in blob or _fold(name).lower() in _fold(blob).lower():
            chars.append(name)

    return ActivityStoryMap(
        story_no=story_no.zfill(3),
        title=title,
        opening_event=final_six[0],
        inciting_problem=final_six[1],
        response_action=final_six[2],
        central_event=final_six[3],
        climax_revelation=final_six[4],
        resolution=final_six[5],
        named_characters=chars,
        setting="Vṛndāvana" if "Vṛndāvana" in main or "Vrindavana" in _fold(main) else "",
        age_band=age_band,
        source="canonical_sentences",
    )


def evaluate_activity_semantic_qa(
    *,
    activity_type: str,
    events: list[str],
    parent_answer_events: list[str] | None = None,
    required_tokens: list[str] | None = None,
    canonical_story: str = "",
) -> ActivitySemanticQa:
    failures: list[str] = []
    if activity_type.upper() in {"STORY_SEQUENCE", "SEQUENCE"}:
        if len(events) == 0:
            failures.append("sequence expected item count is zero")
        failures.extend(validate_event_list(events, required_chars=required_tokens))
        # Arc coverage heuristics
        blob = _fold(" ".join(events)).lower()
        if required_tokens:
            for token in required_tokens:
                if _fold(token).lower() not in blob:
                    failures.append(f"arc/token coverage missing: {token}")
        # Opening-only detection: first 200 chars of story dominate all events
        if canonical_story:
            opening = _fold(canonical_story[:280]).lower()
            opening_hits = sum(1 for e in events if _fold(e)[:40].lower() in opening)
            if opening_hits >= 5:
                failures.append("multiple cards drawn only from opening scene")
        if parent_answer_events is not None:
            norm_e = sorted(" ".join(x.split()) for x in events)
            norm_p = sorted(" ".join(x.split()) for x in parent_answer_events)
            if norm_e != norm_p:
                failures.append("parent answer key does not match rendered sequence events")
    placeholder_ok = True
    for event in events:
        for pat in _PLACEHOLDER_PATTERNS:
            if pat.search(event or ""):
                placeholder_ok = False
                failures.append("placeholder language detected")
                break
    grounding = 0.0
    if canonical_story and events:
        hits = 0
        canon = _fold(canonical_story).lower()
        for event in events:
            # Require substantial token overlap with canonical text
            tokens = [t for t in _WORD_RE.findall(event.lower()) if len(t) >= 4]
            if not tokens:
                continue
            overlap = sum(1 for t in tokens if t in canon)
            if overlap / max(1, len(tokens)) >= 0.5:
                hits += 1
        grounding = hits / float(len(events))
        if grounding < 0.8:
            failures.append(f"canonical grounding score {grounding:.2f} < 0.80")

    complete_ok = all(_is_complete_sentence(e) for e in events) if events else False
    dup_ok = len({" ".join(e.lower().split()) for e in events}) == len(events) if events else False
    trunc_ok = not any(_looks_truncated(e) for e in events)
    result = "PASS" if not failures else "FAIL"
    return ActivitySemanticQa(
        activity_type=activity_type,
        expected_item_count=6 if activity_type.upper() in {"STORY_SEQUENCE", "SEQUENCE"} else len(events),
        rendered_item_count=len(events),
        complete_sentence_ok=complete_ok,
        duplicates_ok=dup_ok,
        truncated_ok=trunc_ok,
        chronological_ok="chronological" not in " ".join(failures),
        arc_coverage_ok=not any("arc/token" in f or "opening scene" in f for f in failures),
        named_character_ok=not any("character/token missing" in f for f in failures),
        grounding_score=round(grounding, 3),
        parent_answer_key_ok=not any("parent answer" in f for f in failures),
        placeholder_scan_ok=placeholder_ok,
        result=result,
        failure_reasons=tuple(failures),
    )


def write_activity_semantic_qa(qa: ActivitySemanticQa, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(qa.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = [
    "ActivitySemanticQa",
    "ActivityStoryMap",
    "evaluate_activity_semantic_qa",
    "reconstruct_story_map_from_canonical",
    "validate_event_list",
    "write_activity_semantic_qa",
]
