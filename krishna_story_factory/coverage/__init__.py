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

# Required major event IDs for Chapters 7–8 after V1.7.3.
REQUIRED_CH7_MAJOR_IDS = frozenset(
    {"kb7-utthana-cart", "kb7-trinavarta", "kb7-yawn-universal-mouth"}
)
REQUIRED_CH8_MAJOR_IDS = frozenset(
    {
        "kb8-garga-name-giving",
        "kb8-crawling-adventures",
        "kb8-butter-complaints",
        "kb8-dirt-universal-form",
    }
)
UNIVERSAL_FORM_EVENT_IDS = frozenset(
    {"kb7-yawn-universal-mouth", "kb8-dirt-universal-form"}
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


def clear_coverage_cache() -> None:
    load_coverage_ledger.cache_clear()


def major_events_for_story(story_no: str) -> list[dict[str, Any]]:
    ledger = load_coverage_ledger()
    out: list[dict[str, Any]] = []
    for chapter in ledger.get("chapters") or []:
        for event in chapter.get("events") or []:
            if story_no in (event.get("mapped_stories") or []) and event.get("significance") == "major":
                out.append({**event, "chapter": chapter.get("chapter"), "chapter_title": chapter.get("title")})
    return out


def _chapter_events(ledger: dict[str, Any], chapter_no: int) -> list[dict[str, Any]]:
    for item in ledger.get("chapters") or []:
        if int(item.get("chapter") or 0) == chapter_no:
            return list(item.get("events") or [])
    return []


def _major_ids(events: list[dict[str, Any]]) -> set[str]:
    return {
        str(event.get("id"))
        for event in events
        if event.get("significance") == "major" and event.get("id")
    }


def evaluate_ledger_integrity(ledger: dict[str, Any] | None = None) -> CoverageGateResult:
    """Validate that major Chapter 7–8 events are not skipped or collapsed."""
    errors: list[str] = []
    data = ledger if ledger is not None else load_coverage_ledger()
    if not data:
        return CoverageGateResult(ok=False, errors=["Coverage ledger missing."])

    ch7 = _chapter_events(data, 7)
    ch8 = _chapter_events(data, 8)
    ch7_ids = _major_ids(ch7)
    ch8_ids = _major_ids(ch8)

    if ch7_ids == {"kb7-trinavarta"} or (
        "kb7-trinavarta" in ch7_ids and "kb7-utthana-cart" not in ch7_ids
    ):
        errors.append("Chapter 7 must not be mapped only to Tṛṇāvarta; cart-breaking is required.")
    missing7 = REQUIRED_CH7_MAJOR_IDS - ch7_ids
    if missing7:
        errors.append(f"Chapter 7 missing required major events: {sorted(missing7)}")
    if "kb7-yawn-universal-mouth" not in ch7_ids:
        errors.append("First universal-mouth event (kb7-yawn-universal-mouth) is absent from Chapter 7.")

    if ch8_ids == {"kb8-universal-mouth"} or ch8_ids == {"kb8-dirt-universal-form"}:
        # Single universal-mouth mapping without Garga/crawling/butter is incomplete.
        if not REQUIRED_CH8_MAJOR_IDS.issubset(ch8_ids):
            errors.append("Chapter 8 must not be mapped only to a universal-mouth event.")
    missing8 = REQUIRED_CH8_MAJOR_IDS - ch8_ids
    if missing8:
        errors.append(f"Chapter 8 missing required major events: {sorted(missing8)}")
    if "kb8-garga-name-giving" not in ch8_ids:
        errors.append("Garga Muni / name-giving major event is absent.")

    # Butter + dirt collapsed into one summary event.
    for event in ch8:
        summary = f"{event.get('id', '')} {event.get('summary', '')} {event.get('title', '')}".lower()
        if "butter" in summary and ("dirt" in summary or "universal" in summary):
            if event.get("id") not in {"kb8-butter-complaints", "kb8-dirt-universal-form"}:
                errors.append("Butter-stealing and dirt-eating must not be collapsed into one summary event.")

    # Story 010 must be cart, not Tṛṇāvarta.
    cart = next((e for e in ch7 if e.get("id") == "kb7-utthana-cart"), None)
    trin = next((e for e in ch7 if e.get("id") == "kb7-trinavarta"), None)
    if cart and "010" not in (cart.get("mapped_stories") or []):
        errors.append("Cart-breaking major event must map to Story 010.")
    if trin and "010" in (trin.get("mapped_stories") or []):
        errors.append("Story 010 must not be Tṛṇāvarta while cart-breaking remains a separate uncovered major.")
    if trin and "011" not in (trin.get("mapped_stories") or []):
        errors.append("Tṛṇāvarta must map to Story 011 (after cart-breaking).")

    # Two universal forms cannot share one mapped story as sole coverage.
    yawn = next((e for e in ch7 if e.get("id") == "kb7-yawn-universal-mouth"), None)
    dirt = next((e for e in ch8 if e.get("id") == "kb8-dirt-universal-form"), None)
    if yawn and dirt:
        y_stories = set(yawn.get("mapped_stories") or [])
        d_stories = set(dirt.get("mapped_stories") or [])
        if y_stories and d_stories and y_stories == d_stories and len(y_stories) == 1:
            errors.append(
                "One universal-form story cannot satisfy both Chapter 7 and Chapter 8 manifestations."
            )
        if not y_stories.isdisjoint(d_stories):
            # overlapping multi-story maps still wrong if identical singleton already caught
            shared = y_stories & d_stories
            if shared and y_stories == d_stories:
                errors.append(
                    "Chapter 7 and Chapter 8 universal-form events must remain separately mapped."
                )

    # Every major event needs mapping + reviewer (event or chapter).
    for chapter in data.get("chapters") or []:
        chapter_reviewer = chapter.get("reviewer")
        for event in chapter.get("events") or []:
            if event.get("significance") != "major":
                continue
            mapped = event.get("mapped_stories") or []
            if not mapped:
                errors.append(f"Major event {event.get('id')} has no mapped story.")
            if not event.get("reviewer") and not chapter_reviewer:
                errors.append(f"Major event {event.get('id')} missing reviewer approval.")
            # Combined stories require explicit notes marker.
            if len(mapped) > 1 and "combined" not in str(event.get("notes", "")).lower():
                errors.append(
                    f"Major event {event.get('id')} maps to multiple stories without a "
                    "reviewer-approved combined-story note."
                )

    return CoverageGateResult(ok=not errors, errors=errors)


def earliest_pending_major_story(queue_by_chapter: dict[str, str]) -> str | None:
    """Return the earliest story number that still covers an uncovered major event."""
    ledger = load_coverage_ledger()
    candidates: list[str] = []
    for chapter in ledger.get("chapters") or []:
        for event in chapter.get("events") or []:
            if event.get("significance") != "major":
                continue
            if event.get("lifecycle") not in {"pending", "planned", None, ""}:
                # published majors are covered
                if str(event.get("lifecycle")).lower() == "published":
                    continue
            for story in event.get("mapped_stories") or []:
                story_no = str(story).zfill(3)
                status = (queue_by_chapter.get(story_no) or "pending").lower()
                if status != "done":
                    candidates.append(story_no)
    if not candidates:
        return None
    return sorted(candidates, key=lambda value: int(value))[0]


def evaluate_queue_advancement(
    next_story_no: str,
    queue_by_chapter: dict[str, str],
) -> CoverageGateResult:
    """Block selecting a later story while an earlier major event remains uncovered."""
    errors: list[str] = []
    earliest = earliest_pending_major_story(queue_by_chapter)
    nxt = str(next_story_no).zfill(3)
    if earliest and int(nxt) > int(earliest):
        errors.append(
            f"Queue must not advance to Story {nxt} while uncovered major event story "
            f"{earliest} remains pending."
        )
    # Explicit: 010 cannot be Tṛṇāvarta while cart is uncovered — ledger integrity covers mapping;
    # also ensure next pending for empty done-prefix is cart.
    if nxt == "010":
        mapped = major_events_for_story("010")
        ids = {event.get("id") for event in mapped}
        if "kb7-trinavarta" in ids and "kb7-utthana-cart" not in ids:
            errors.append("Story 010 selection is Tṛṇāvarta while cart-breaking is uncovered.")
        if "kb7-utthana-cart" not in ids:
            errors.append("Next production story 010 must map to cart-breaking (kb7-utthana-cart).")
    return CoverageGateResult(ok=not errors, errors=errors)


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

    ledger = load_coverage_ledger()
    if not ledger:
        errors.append("Coverage ledger missing; cannot publish without mapping approval.")
        return CoverageGateResult(ok=False, errors=errors)

    integrity = evaluate_ledger_integrity(ledger)
    if not integrity.ok:
        errors.extend(integrity.errors)

    mapped = major_events_for_story(story_no)
    if not mapped and story_no <= "016":
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

    if story_no == "010":
        if "cart" not in plan.slug and "cart" not in plan.title.lower():
            errors.append("Story 010 must be the cart-breaking pastime, not Tṛṇāvarta.")
        for pat in TRINAVARTA_MAIN:
            if re.search(pat, main, re.I):
                errors.append("Story 010 main content must not narrate Tṛṇāvarta before cart coverage.")

    # Chapter title alone is not coverage.
    if re.fullmatch(r"\s*(complete\s+)?krishna\s+book\s+chapter\s+\d+\s*", (content.main_story or ""), re.I):
        errors.append("A chapter title alone is not sufficient narrative coverage.")

    # Generic: later-chapter leakage heuristics for 001–016 from must_avoid.
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
        # Title/metadata-only: if tokens appear only in title fields, not main.
        title_blob = f"{plan.title} {plan.summary_seed}".lower()
        if hits_main == 0 and any(t in title_blob for t in tokens[:4]):
            errors.append(
                f"Major event {event.get('id')} appears only in title/metadata, not full coverage."
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
        if re.search(TRINAVARTA_MAIN[0], text, re.I) and "next" not in text[
            max(0, text.find("tṛṇāvarta") - 40) : text.find("tṛṇāvarta") + 1
        ]:
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
