"""Single canonical narration contract (Story 021+).

Canonical source = Main Story body in story.md.
TTS must consume that exact text after only approved deterministic transforms.
Fuzzy similarity (e.g. 62% token coverage) is not a pass path.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_WS_RE = re.compile(r"\s+")
_SSML_RE = re.compile(r"</?(?:break|emphasis|prosody|speak|say-as)\b[^>]*>", re.IGNORECASE)
_MD_EMPHASIS_RE = re.compile(r"[*_`]+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。])\s+")


@dataclass(frozen=True)
class CanonicalNarrationQa:
    story_no: str
    canonical_source_location: str
    canonical_normalized_sha256: str
    tts_normalized_sha256: str
    exact_match: bool
    source_word_count: int
    tts_word_count: int
    omitted_sentences: tuple[str, ...] = ()
    added_sentences: tuple[str, ...] = ()
    reordered_sentences: bool = False
    approved_transformations: tuple[str, ...] = ()
    result: str = "FAIL"
    failure_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["omitted_sentences"] = list(self.omitted_sentences)
        data["added_sentences"] = list(self.added_sentences)
        data["approved_transformations"] = list(self.approved_transformations)
        data["failure_reasons"] = list(self.failure_reasons)
        return data


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def extract_main_story(story_md: str) -> str:
    match = re.search(
        r"(?is)(?:^|\n)#+\s*Main Story\s*\n(.*?)(?=\n#+\s|\Z)",
        story_md or "",
    )
    if not match:
        return ""
    return match.group(1).strip()


def extract_canonical_narration(story_md: str) -> str:
    """Authoritative spoken/read narrative body: Main Story section only."""
    return extract_main_story(story_md)


def split_sentences(text: str) -> list[str]:
    cleaned = _WS_RE.sub(" ", (text or "").strip())
    if not cleaned:
        return []
    parts = _SENTENCE_SPLIT_RE.split(cleaned)
    return [p.strip() for p in parts if p.strip()]


def apply_approved_tts_transforms(
    text: str,
    *,
    pronunciation_aliases: dict[str, str] | None = None,
    strip_markdown: bool = True,
) -> tuple[str, tuple[str, ...]]:
    """Deterministic TTS transforms only — no paraphrase/reorder/omit/add."""
    applied: list[str] = []
    out = unicodedata.normalize("NFC", text or "")
    if out != (text or ""):
        applied.append("unicode_nfc")
    if _SSML_RE.search(out):
        out = _SSML_RE.sub("", out)
        applied.append("strip_ssml_tags")
    if strip_markdown and _MD_EMPHASIS_RE.search(out):
        out = _MD_EMPHASIS_RE.sub("", out)
        applied.append("strip_markdown_emphasis")
    collapsed = _WS_RE.sub(" ", out).strip()
    if collapsed != out.strip():
        applied.append("whitespace_normalize")
    out = collapsed
    if pronunciation_aliases:
        for source, target in sorted(pronunciation_aliases.items(), key=lambda kv: len(kv[0]), reverse=True):
            pattern = re.compile(rf"(?<!\w){re.escape(source)}(?!\w)")
            if pattern.search(out):
                out = pattern.sub(target, out)
                applied.append(f"pronunciation_alias:{source}")
    return out, tuple(dict.fromkeys(applied))


def normalize_for_exact_compare(text: str) -> str:
    """Normalize both sides for exact equality after approved transforms."""
    cleaned, _ = apply_approved_tts_transforms(text, pronunciation_aliases=None, strip_markdown=True)
    return _WS_RE.sub(" ", cleaned).strip()


def evaluate_canonical_narration_exact(
    *,
    story_no: str,
    story_md: str,
    tts_source: str,
    pronunciation_aliases: dict[str, str] | None = None,
) -> CanonicalNarrationQa:
    canonical = extract_canonical_narration(story_md)
    if not canonical:
        return CanonicalNarrationQa(
            story_no=story_no.zfill(3),
            canonical_source_location="## Main Story",
            canonical_normalized_sha256="",
            tts_normalized_sha256="",
            exact_match=False,
            source_word_count=0,
            tts_word_count=0,
            result="FAIL",
            failure_reasons=("Main Story / canonical narration missing.",),
        )

    # Compare speech input to canonical after stripping only TTS-side pronunciation aliases
    # and shared whitespace/SSML/markdown normalization. Display text keeps diacritics.
    canon_norm = normalize_for_exact_compare(canonical)
    tts_transformed, applied = apply_approved_tts_transforms(
        tts_source,
        pronunciation_aliases=pronunciation_aliases,
        strip_markdown=True,
    )
    # Also strip aliases from canonical for equality when aliases are TTS-only substitutions.
    canon_for_tts, canon_applied = apply_approved_tts_transforms(
        canonical,
        pronunciation_aliases=pronunciation_aliases,
        strip_markdown=True,
    )
    approved = tuple(dict.fromkeys((*canon_applied, *applied)))

    canon_sentences = split_sentences(canon_for_tts)
    tts_sentences = split_sentences(tts_transformed)
    omitted = tuple(s for s in canon_sentences if s not in tts_sentences)
    added = tuple(s for s in tts_sentences if s not in canon_sentences)
    reordered = False
    if not omitted and not added and canon_sentences and tts_sentences:
        # Same multiset but different order?
        if sorted(canon_sentences) == sorted(tts_sentences) and canon_sentences != tts_sentences:
            reordered = True
        elif canon_sentences != tts_sentences:
            # Different sentence boundaries with same bag of words still fail via text equality.
            reordered = False

    exact = canon_for_tts == tts_transformed
    failures: list[str] = []
    if not exact:
        failures.append("canonical and TTS text are not exactly equal after approved transforms")
    if omitted:
        failures.append(f"omitted {len(omitted)} sentence(s)")
    if added:
        failures.append(f"added {len(added)} sentence(s)")
    if reordered:
        failures.append("sentences reordered")
        exact = False

    result = "PASS" if exact and not omitted and not added and not reordered else "FAIL"
    return CanonicalNarrationQa(
        story_no=story_no.zfill(3),
        canonical_source_location="## Main Story",
        canonical_normalized_sha256=sha256_text(canon_for_tts),
        tts_normalized_sha256=sha256_text(tts_transformed),
        exact_match=exact and result == "PASS",
        source_word_count=len(canon_norm.split()),
        tts_word_count=len(tts_transformed.split()),
        omitted_sentences=omitted[:20],
        added_sentences=added[:20],
        reordered_sentences=reordered,
        approved_transformations=approved,
        result=result,
        failure_reasons=tuple(failures),
    )


def write_canonical_narration_qa(qa: CanonicalNarrationQa, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(qa.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def sync_audio_narration_from_main_story(story_md: str) -> str:
    """Deterministically set HTML-comment Audio Narration = Main Story (no LLM)."""
    main = extract_main_story(story_md)
    if not main:
        raise ValueError("Cannot sync Audio Narration: Main Story missing.")
    # Replace existing Audio Narration block inside HTML comment, or inject.
    pattern = re.compile(
        r"(<!--.*?## Audio Narration\s*\n)(.*?)(\n\n## |\n## |\n-->)",
        re.IGNORECASE | re.DOTALL,
    )

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{main}{match.group(3)}"

    if pattern.search(story_md):
        return pattern.sub(repl, story_md, count=1)
    # No audio block — insert before closing comment or append comment.
    if "<!--" in story_md and "-->" in story_md:
        return story_md.replace(
            "<!--",
            f"<!--\n## Audio Narration\n{main}\n\n",
            1,
        )
    return story_md.rstrip() + f"\n\n<!--\n## Audio Narration\n{main}\n-->\n"


__all__ = [
    "CanonicalNarrationQa",
    "apply_approved_tts_transforms",
    "evaluate_canonical_narration_exact",
    "extract_canonical_narration",
    "extract_main_story",
    "normalize_for_exact_compare",
    "sha256_text",
    "split_sentences",
    "sync_audio_narration_from_main_story",
    "write_canonical_narration_qa",
]
