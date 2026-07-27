"""Hard non-skipping publication gates for Krishna Book coverage fidelity."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..models import PlanRow, StoryContent

ROOT = Path(__file__).resolve().parents[2]
COVERAGE_PATH = ROOT / "data" / "series" / "krishna_book_coverage.yaml"

# Patterns that prove the defective V1.7 Story 009 class of error.
_APOS = r"['\u2019]"
DEFECT_009_PATTERNS = (
    rf"after\s+p[uū]tan[aā]{_APOS}?s\s+defeat",
    rf"p[uū]tan[aā]\s+was\s+already",
    r"already\s+defeated",
    r"universe\s+(?:in|within|inside).{0,40}mouth",
    r"mouth.{0,80}universe",
    r"whole\s+universe\s+was\s+shining",
    r"universal\s+form",
    r"yawning\s+showed",
    r"goblins?\s+circled|spirits?\s+and\s+roaming\s+goblins|circled\s+the\s+border\s+of\s+gokula",
)

TRINAVARTA_MAIN = (
    r"t[rṛ][nṇ][aā]varta",
    r"whirlwind\s+demon",
    r"demon\s+of\s+the\s+(?:wind|storm|whirlwind)",
)


@dataclass
class CoverageGateResult:
    ok: bool
    errors: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok


@lru_cache(maxsize=1)
def load_coverage_ledger() -> dict[str, Any]:
    if not COVERAGE_PATH.is_file():
        return {}
    return yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8")) or {}


def major_events_for_story(story_no: str) -> list[dict[str, Any]]:
    ledger = load_coverage_ledger()
    out: list[dict[str, Any]] = []
    for chapter in ledger.get("chapters") or []:
        for event in chapter.get("events") or []:
            if story_no in (event.get("mapped_stories") or []) and event.get("significance") == "major":
                out.append({**event, "chapter": chapter.get("chapter"), "chapter_title": chapter.get("title")})
    return out


def evaluate_story_coverage(plan: PlanRow, content: StoryContent) -> CoverageGateResult:
    """Block publication when major pastimes are skipped, recap-only, or replaced."""
    errors: list[str] = []
    story_no = str(plan.chapter_no).zfill(3)
    preview = (content.next_story_preview or "").lower()
    # Audio/main must be judged without the next-preview paragraph (preview may name the next major pastime).
    main_story = (content.main_story or "").lower()
    audio = (content.audio_script or "").lower()
    if preview:
        audio = audio.replace(preview, " ")
        main_story = main_story.replace(preview, " ")
    main = f"{main_story}\n{audio}"
    recap = (content.recap or "").lower()
    full = f"{recap}\n{main}\n{preview}\n{(content.devotional_meaning or '').lower()}"

    ledger = load_coverage_ledger()
    if not ledger:
        errors.append("Coverage ledger missing; cannot publish without mapping approval.")
        return CoverageGateResult(ok=False, errors=errors)

    mapped = major_events_for_story(story_no)
    if not mapped and story_no <= "010":
        errors.append(f"Story {story_no} has no major-event mapping in the coverage ledger.")

    for event in mapped:
        if not event.get("reviewer") and not _chapter_reviewer(ledger, event.get("chapter")):
            errors.append(f"Coverage event {event.get('id')} missing reviewer approval.")

    # Title/source must align with declared chapter for early episodes.
    src = f"{plan.source_reference} {plan.scripture_reference} {plan.title}".lower()
    if story_no == "009":
        if "6" not in plan.source_reference and "chapter 6" not in plan.source_reference.lower():
            errors.append("Story 009 source_reference must be Krishna Book Chapter 6.")
        if "pūtanā" not in plan.title.lower() and "putana" not in plan.title.lower():
            errors.append("Story 009 title must identify Pūtanā.")
        if not any(x in main for x in ("putana", "pūtanā", "putanā")):
            errors.append("Story 009 main narration omits Pūtanā — major pastime skipped.")
        # Recap-only is not coverage.
        if "putana" in recap and "putana" not in main and "pūtanā" not in main:
            errors.append("Major Pūtanā pastime appears only in recap, not full coverage.")
        for pat in DEFECT_009_PATTERNS:
            if re.search(pat, main, re.I):
                errors.append(f"Story 009 contains forbidden later/skipped-chapter pattern: {pat}")
        for pat in TRINAVARTA_MAIN:
            if re.search(pat, main, re.I):
                errors.append("Story 009 main content must not narrate Tṛṇāvarta (Chapter 7).")
        # Preview may mention Trinavarta, but must not jump over uncovered major of Ch.6.
        if "complete chapter 6" in src or "chapter 6" in src:
            required_needles = ("poison", "breast", "fragrant")
            for needle in required_needles:
                if needle not in main:
                    errors.append(
                        f"'Complete Chapter 6' claim without required Pūtanā unit covering {needle!r}."
                    )

    # Generic: later-chapter leakage heuristics for 001–010 from must_avoid.
    for phrase in _split(plan.must_avoid):
        low = phrase.lower()
        if low in main:
            errors.append(f"Later/unrelated event leaked into main coverage: {phrase!r}")

    # Preview must not be the only place a mapped major for THIS story appears.
    for event in mapped:
        summary = (event.get("summary") or "").lower()
        tokens = [t for t in re.findall(r"[a-zāīūṛṅñṭḍṇśṣḥ]{4,}", summary) if t not in {"krishna", "kṛṣṇa", "lord"}]
        if not tokens:
            continue
        hits_main = sum(1 for t in tokens[:6] if t in main)
        hits_preview = sum(1 for t in tokens[:6] if t in preview)
        hits_recap = sum(1 for t in tokens[:6] if t in recap)
        if hits_main == 0 and (hits_preview > 0 or hits_recap > 0):
            errors.append(
                f"Major event {event.get('id')} appears only in recap/preview, not full coverage."
            )

    return CoverageGateResult(ok=not errors, errors=errors)


def evaluate_package_text(story_no: str, story_md: str, plan: PlanRow | None = None) -> CoverageGateResult:
    """Regression helper for raw story.md text (including defective historical packages)."""
    errors: list[str] = []
    text = story_md.lower()
    if story_no.zfill(3) == "009":
        for pat in DEFECT_009_PATTERNS:
            if re.search(pat, text, re.I):
                errors.append(f"Defective Story 009 pattern present: {pat}")
        if re.search(r"complete\s+krishna\s+book\s+chapter\s+6", text, re.I) and not any(
            x in text for x in ("poison", "pūtanā", "putana")
        ):
            errors.append("Complete Chapter 6 claim without Pūtanā poison coverage.")
        if re.search(TRINAVARTA_MAIN[0], text, re.I) and "next" not in text[max(0, text.find("tṛṇāvarta") - 40) : text.find("tṛṇāvarta") + 1]:
            # Soft: flag Trinavarta outside next-preview headings
            if "## next" not in text and "next story" not in text:
                errors.append("Tṛṇāvarta material appears outside a next-story preview context.")
    if plan is not None:
        # Build a minimal StoryContent-like check via evaluate when structured content exists.
        pass
    return CoverageGateResult(ok=not errors, errors=errors)


def _chapter_reviewer(ledger: dict[str, Any], chapter: Any) -> str | None:
    for item in ledger.get("chapters") or []:
        if item.get("chapter") == chapter:
            return item.get("reviewer")
    return None


def _split(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]
