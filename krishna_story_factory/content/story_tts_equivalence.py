"""Canonical story ↔ TTS source semantic equivalence helpers (Story 021+).

Does not regenerate Stories 001–020. Operators use this for future packages and
optional audits against archived TTS inputs when available.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


_WS_RE = re.compile(r"\s+")
_PAUSE_MARKERS = re.compile(r"\[pause\]|<break\b[^>]*>", re.IGNORECASE)


@dataclass(frozen=True)
class EquivalenceResult:
    status: str
    canonical_story_text_sha256: str
    tts_source_text_sha256: str
    normalized_semantic_text_sha256: str
    notes: str = ""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_canonical_narrative(story_md: str) -> str:
    """Best-effort narrative body: drop HTML comments and common educational headings."""
    without_comments = re.sub(r"<!--.*?-->", "", story_md, flags=re.DOTALL)
    lines: list[str] = []
    skip_prefixes = (
        "## Devotional meaning",
        "## Lessons",
        "## Questions",
        "## Challenges",
        "## Bedtime prayer",
        "## Parent",
        "## Teacher",
        "## Activity",
        "## Rights",
        "## Audio Narration",
    )
    skipping = False
    for raw in without_comments.splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and not line.startswith("## "):
            # Title headings are metadata for reading chrome, not TTS body.
            continue
        if line.startswith("## "):
            skipping = any(line.startswith(p) for p in skip_prefixes)
            if skipping:
                continue
        if skipping:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def normalize_semantic(text: str) -> str:
    """Approved non-semantic normalization for equivalence comparison."""
    cleaned = _PAUSE_MARKERS.sub(" ", text)
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = _WS_RE.sub(" ", cleaned).strip().lower()
    return cleaned


def compare_canonical_to_tts(*, story_md: str, tts_source: str) -> EquivalenceResult:
    canonical = extract_canonical_narrative(story_md)
    canonical_sha = sha256_text(canonical)
    tts_sha = sha256_text(tts_source)
    norm_canon = normalize_semantic(canonical)
    norm_tts = normalize_semantic(tts_source)
    norm_sha = sha256_text(norm_canon)
    if norm_canon == norm_tts:
        status = "MATCH" if canonical == tts_source else "NON-SEMANTIC DIFFERENCE"
        notes = "Normalized narrative matches TTS source."
    else:
        status = "MATERIAL DIFFERENCE"
        notes = "Normalized narrative diverges from TTS source; manual review required."
    return EquivalenceResult(
        status=status,
        canonical_story_text_sha256=canonical_sha,
        tts_source_text_sha256=tts_sha,
        normalized_semantic_text_sha256=norm_sha,
        notes=notes,
    )


_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "as",
    "at",
    "by",
    "from",
    "his",
    "her",
    "their",
    "they",
    "them",
    "he",
    "she",
    "it",
    "its",
    "was",
    "were",
    "are",
    "is",
    "be",
    "been",
    "that",
    "this",
    "these",
    "those",
    "into",
    "over",
    "under",
    "then",
    "than",
    "when",
    "while",
    "who",
    "whom",
    "which",
    "what",
    "how",
    "so",
    "not",
    "no",
    "yes",
    "all",
    "each",
    "every",
    "our",
    "we",
    "you",
    "your",
    "dear",
    "children",
    "families",
    "story",
    "tonight",
}


def _significant_tokens(text: str) -> set[str]:
    norm = normalize_semantic(text)
    tokens = re.findall(r"[a-z0-9\u0100-\u024f\u1e00-\u1eff']+", norm, flags=re.I)
    return {t for t in tokens if len(t) >= 4 and t not in _STOPWORDS}


def extract_main_story_section(story_md: str) -> str:
    """Extract the visible Main Story section used as the Read-tab narrative body."""
    without_comments = re.sub(r"<!--.*?-->", "", story_md or "", flags=re.DOTALL)
    match = re.search(
        r"##\s+Main Story\s*\n(.*?)(?=\n##\s+|\Z)",
        without_comments,
        flags=re.S | re.I,
    )
    return match.group(1).strip() if match else ""


@dataclass(frozen=True)
class StoryTtsGateResult:
    status: str
    gate: str
    main_story_words: int
    audio_words: int
    token_coverage: float
    notes: str = ""

    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "status": self.status,
            "gate": self.gate,
            "main_story_words": self.main_story_words,
            "audio_words": self.audio_words,
            "token_coverage": self.token_coverage,
            "notes": self.notes,
        }


def evaluate_story_tts_equivalence(
    *,
    story_md: str,
    tts_source: str,
    min_token_coverage: float = 0.58,
    min_audio_word_ratio: float = 0.70,
    max_audio_word_ratio: float = 1.35,
    min_name_coverage: float = 0.70,
    require_exact_canonical: bool = True,
) -> StoryTtsGateResult:
    """Fail-closed gate for Story 021+ create-next.

    Default: Main Story must exactly equal TTS source after approved transforms.
    Fuzzy token-coverage (e.g. 62%) is never a pass path when
    ``require_exact_canonical`` is True (the create-next default).
    """
    from .canonical_narration import evaluate_canonical_narration_exact

    main = extract_main_story_section(story_md)
    audio = (tts_source or "").strip()
    main_words = len(main.split())
    audio_words = len(audio.split())
    if main_words < 100:
        return StoryTtsGateResult(
            status="FAIL",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=0.0,
            notes="Main Story missing or too short for equivalence gate.",
        )
    if audio_words < 100:
        return StoryTtsGateResult(
            status="FAIL",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=0.0,
            notes="Audio Narration missing or too short for equivalence gate.",
        )

    if require_exact_canonical:
        qa = evaluate_canonical_narration_exact(
            story_no="000",
            story_md=story_md if "## Main Story" in (story_md or "") else f"## Main Story\n{main}\n",
            tts_source=audio,
        )
        if qa.result != "PASS":
            return StoryTtsGateResult(
                status="FAIL",
                gate="story_tts_equivalence",
                main_story_words=main_words,
                audio_words=audio_words,
                token_coverage=0.0,
                notes="CANONICAL_EXACT_MATCH_FAIL: " + " | ".join(qa.failure_reasons),
            )
        return StoryTtsGateResult(
            status="PASS",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=1.0,
            notes="Canonical Main Story exactly matches TTS source after approved transforms.",
        )

    # Legacy audit path only (explicit opt-in). Not used by create-next.
    exact = compare_canonical_to_tts(
        story_md=f"## Main Story\n{main}\n",
        tts_source=audio,
    )
    if exact.status in {"MATCH", "NON-SEMANTIC DIFFERENCE"}:
        return StoryTtsGateResult(
            status="PASS",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=1.0,
            notes=exact.notes,
        )

    main_tokens = _significant_tokens(main)
    audio_tokens = _significant_tokens(audio)
    if not main_tokens:
        return StoryTtsGateResult(
            status="FAIL",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=0.0,
            notes="No significant Main Story tokens to compare.",
        )
    coverage = len(main_tokens & audio_tokens) / float(len(main_tokens))
    name_tokens = {
        t
        for t in re.findall(
            r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF]{3,}",
            main,
        )
        if t[0].isupper() or re.search(r"[\u0100-\u024F\u1E00-\u1EFF]", t)
    }
    name_tokens_norm = {normalize_semantic(t) for t in name_tokens if len(t) >= 3}
    audio_norm = normalize_semantic(audio)
    if name_tokens_norm:
        name_hits = sum(1 for n in name_tokens_norm if n and n in audio_norm)
        name_coverage = name_hits / float(len(name_tokens_norm))
    else:
        name_coverage = 1.0
    ratio = audio_words / float(main_words)
    failures: list[str] = []
    if coverage < min_token_coverage:
        failures.append(
            f"significant-token coverage {coverage:.0%} < {min_token_coverage:.0%}"
        )
    if name_coverage < min_name_coverage:
        failures.append(
            f"name/token coverage {name_coverage:.0%} < {min_name_coverage:.0%}"
        )
    if ratio < min_audio_word_ratio:
        failures.append(
            f"audio/main word ratio {ratio:.2f} < {min_audio_word_ratio:.2f} (possible abridgement)"
        )
    if ratio > max_audio_word_ratio:
        failures.append(
            f"audio/main word ratio {ratio:.2f} > {max_audio_word_ratio:.2f} (possible invented expansion)"
        )
    if failures:
        return StoryTtsGateResult(
            status="FAIL",
            gate="story_tts_equivalence",
            main_story_words=main_words,
            audio_words=audio_words,
            token_coverage=round(coverage, 4),
            notes="MATERIAL DIFFERENCE: " + " | ".join(failures),
        )
    return StoryTtsGateResult(
        status="PASS",
        gate="story_tts_equivalence",
        main_story_words=main_words,
        audio_words=audio_words,
        token_coverage=round(coverage, 4),
        notes=(
            "LEGACY_FUZZY_PASS: Main Story and Audio Narration within oral/framing band "
            f"(coverage={coverage:.0%}, name_coverage={name_coverage:.0%}, word_ratio={ratio:.2f})."
        ),
    )
