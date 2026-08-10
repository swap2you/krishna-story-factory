"""Pronunciation lexicon coverage scan before paid TTS (Story 021+)."""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .pronunciation import load_pronunciation_aliases


# Common English words that may carry diacritics in other languages — ignore as names.
_IGNORE = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "dear",
    "children",
    "families",
    "story",
    "book",
    "chapter",
    "complete",
}


@dataclass(frozen=True, slots=True)
class PronunciationCoverageResult:
    status: str
    checked_tokens: tuple[str, ...]
    covered: tuple[str, ...]
    missing: tuple[str, ...]
    lexicon_size: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "checked_tokens": list(self.checked_tokens),
            "covered": list(self.covered),
            "missing": list(self.missing),
            "lexicon_size": self.lexicon_size,
            "notes": self.notes,
        }


_DIACRITIC_TOKEN = re.compile(
    r"[A-Za-z]*[\u0100-\u024F\u1E00-\u1EFF][A-Za-z\u0100-\u024F\u1E00-\u1EFF]*"
)


def extract_diacritic_tokens(text: str) -> list[str]:
    # NFC so NFD story text yields the same tokens as lexicon keys.
    found = _DIACRITIC_TOKEN.findall(unicodedata.normalize("NFC", text or ""))
    # Preserve order, unique case-sensitive forms.
    seen: set[str] = set()
    out: list[str] = []
    for token in found:
        token = unicodedata.normalize("NFC", token)
        if token.lower() in _IGNORE:
            continue
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out


def evaluate_pronunciation_coverage(
    text: str,
    *,
    project_root: Path,
) -> PronunciationCoverageResult:
    aliases = load_pronunciation_aliases(project_root)
    keys_lower = {k.lower(): k for k in aliases}
    tokens = extract_diacritic_tokens(text)
    covered: list[str] = []
    missing: list[str] = []
    for token in tokens:
        token_nfc = unicodedata.normalize("NFC", token)
        if token_nfc in aliases or token_nfc.lower() in keys_lower:
            covered.append(token)
        else:
            missing.append(token)
    status = "PASS" if not missing else "FAIL"
    notes = (
        "All diacritic/devotional name tokens covered by input/audio_pronunciations.yaml."
        if status == "PASS"
        else "Missing lexicon entries for: " + ", ".join(missing)
    )
    return PronunciationCoverageResult(
        status=status,
        checked_tokens=tuple(tokens),
        covered=tuple(covered),
        missing=tuple(missing),
        lexicon_size=len(aliases),
        notes=notes,
    )


def write_pronunciation_report(result: PronunciationCoverageResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


__all__ = [
    "PronunciationCoverageResult",
    "evaluate_pronunciation_coverage",
    "extract_diacritic_tokens",
    "write_pronunciation_report",
]
