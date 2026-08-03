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
