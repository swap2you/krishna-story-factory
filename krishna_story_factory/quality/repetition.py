from __future__ import annotations

import re
from dataclasses import dataclass

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "was",
        "are",
        "were",
        "be",
        "been",
        "being",
        "that",
        "this",
        "their",
        "they",
        "them",
        "he",
        "she",
        "it",
        "his",
        "her",
        "our",
        "your",
        "who",
        "which",
        "when",
        "where",
        "while",
        "into",
        "through",
        "before",
        "after",
        "up",
        "down",
        "out",
        "over",
        "under",
        "again",
        "then",
        "once",
        "here",
        "there",
        "all",
        "each",
        "every",
        "one",
        "two",
        "very",
        "so",
        "not",
        "no",
        "yes",
        "do",
        "did",
        "does",
        "have",
        "has",
        "had",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "dear",
        "children",
        "child",
        "tonight",
        "story",
        "stories",
    }
)

_NAME_WORDS = frozenset(
    {
        "krishna",
        "hare",
        "devaki",
        "vasudeva",
        "kamsa",
        "mathura",
        "gokula",
        "brahma",
        "vishnu",
        "nanda",
        "yasoda",
        "yashoda",
        "putana",
        "yamuna",
        "vrindavan",
        "vrindavana",
        "lord",
        "sri",
        "shri",
    }
)

_STORY_FILLER_MARKERS = (
    "the devotees remember this pastime",
    "children can trust that krishna hears sincere prayer",
    "at bedtime we keep our hearts calm",
)

_AUDIO_FILLER_MARKERS = (
    "tonight we heard",
    "listen softly, with wonder, and remember that krishna protects",
    "hare krishna dear children. sweet dreams",
    "before sleep, think of one kind action you can do tomorrow",
)

_BREAK_TAG = re.compile(r"<break\s+time=\"[^\"]+\"\s*/>", re.I)


@dataclass(frozen=True, slots=True)
class RepetitionReport:
    errors: list[str]


def detect_repetition(text: str, *, content_type: str = "story") -> RepetitionReport:
    errors: list[str] = []
    plain = _strip_break_tags(text)
    errors.extend(_check_sentences(plain))
    errors.extend(_check_paragraphs(plain))
    errors.extend(_check_eight_word_phrases(plain))
    errors.extend(_check_tail_repetition(plain))
    if content_type == "story":
        errors.extend(_check_marker_counts(plain, _STORY_FILLER_MARKERS, label="story"))
    else:
        errors.extend(_check_marker_counts(plain, _AUDIO_FILLER_MARKERS, label="audio"))
    return RepetitionReport(errors=errors)


def clean_repetition(text: str, *, content_type: str = "story") -> str:
    cleaned = text.strip()
    cleaned = _remove_consecutive_duplicate_paragraphs(cleaned)
    cleaned = _dedupe_marker_blocks(cleaned, _STORY_FILLER_MARKERS if content_type == "story" else _AUDIO_FILLER_MARKERS)
    cleaned = _remove_consecutive_duplicate_paragraphs(cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _strip_break_tags(text: str) -> str:
    return _BREAK_TAG.sub(" ", text)


def _normalize_sentence(sentence: str) -> str:
    s = sentence.lower().strip()
    s = re.sub(r"[^\w\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def _check_sentences(text: str) -> list[str]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    for sentence in _split_sentences(text):
        key = _normalize_sentence(sentence)
        if len(key.split()) < 4:
            continue
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 2:
            errors.append(f"Sentence repeated more than 2 times: {sentence[:80]}...")
            break
    return errors


def _check_paragraphs(text: str) -> list[str]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    for para in _split_paragraphs(text):
        key = _normalize_sentence(para)
        if len(key.split()) < 6:
            continue
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 1:
            errors.append(f"Paragraph repeated more than once: {para[:80]}...")
            break
    return errors


def _content_words(words: list[str]) -> list[str]:
    return [w for w in words if w not in _STOPWORDS and w not in _NAME_WORDS]


def _check_eight_word_phrases(text: str) -> list[str]:
    errors: list[str] = []
    words = re.findall(r"\b[\w']+\b", text.lower())
    if len(words) < 8:
        return errors
    counts: dict[str, int] = {}
    for i in range(len(words) - 7):
        phrase_words = words[i : i + 8]
        content = _content_words(phrase_words)
        if len(content) < 3:
            continue
        key = " ".join(phrase_words)
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 2:
            errors.append(f"8-word phrase repeated more than 2 times: {' '.join(phrase_words[:8])}")
            break
    return errors


def _check_tail_repetition(text: str) -> list[str]:
    words = re.findall(r"\b[\w']+\b", text.lower())
    if len(words) < 40:
        return []
    split_at = int(len(words) * 0.7)
    head = " ".join(words[:split_at])
    tail = " ".join(words[split_at:])
    tail_chunks = _chunk_words(tail, 12)
    for chunk in tail_chunks:
        content = _content_words(chunk.split())
        if len(content) < 4:
            continue
        if chunk in head:
            return ["Final 30% of content repeats an earlier block."]
    return []


def _chunk_words(text: str, size: int) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + size]) for i in range(0, max(1, len(words) - size + 1), size)]


def _check_marker_counts(text: str, markers: tuple[str, ...], *, label: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for marker in markers:
        if lowered.count(marker) > 1:
            errors.append(f"{label} repeats forbidden closing phrase: {marker!r}")
    return errors


def _remove_consecutive_duplicate_paragraphs(text: str) -> str:
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return text.strip()
    kept: list[str] = []
    prev_key = ""
    for para in paragraphs:
        key = _normalize_sentence(para)
        if key and key == prev_key:
            continue
        kept.append(para)
        prev_key = key
    return "\n\n".join(kept)


def _dedupe_marker_blocks(text: str, markers: tuple[str, ...]) -> str:
    lowered = text.lower()
    result = text
    for marker in markers:
        first = lowered.find(marker)
        if first == -1:
            continue
        second = lowered.find(marker, first + len(marker))
        if second == -1:
            continue
        # Remove second occurrence onward by rebuilding from paragraphs containing marker once
        paragraphs = _split_paragraphs(result)
        seen = False
        filtered: list[str] = []
        for para in paragraphs:
            if marker in para.lower():
                if seen:
                    continue
                seen = True
            filtered.append(para)
        result = "\n\n".join(filtered)
        lowered = result.lower()
    return result
