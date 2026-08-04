"""Pre-TTS punctuation and sentence-boundary integrity gate."""
from __future__ import annotations

import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF']+")
_TERMINAL_OK = re.compile(r'[.!?…]["”\']?$')
_INVOCATION_OK = re.compile(
    r"(?is)(hare\s+k[rṛ][sṣ][nṇ]a.*hare\s+r[aā]ma|om\s+namo|jay[a]?\s+śr[iī]|good\s+night).*$"
)
_MID_WORD_END = re.compile(r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF]{1,2}$")
_JOINED_SENTENCES = re.compile(r"[.!?…][A-Za-z]")
_SSML_INSIDE_WORD = re.compile(r"[A-Za-z]<[^>]+>[A-Za-z]")


@dataclass(frozen=True)
class PunctuationGateResult:
    status: str
    sentence_count: int
    max_sentence_words: int
    warnings: tuple[str, ...]
    failures: tuple[str, ...]
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


def evaluate_punctuation_gate(
    text: str,
    *,
    warn_sentence_words: int = 55,
    fail_sentence_words: int = 90,
    min_sentences: int = 4,
) -> PunctuationGateResult:
    body = (text or "").strip()
    failures: list[str] = []
    warnings: list[str] = []
    if not body:
        return PunctuationGateResult(
            status="FAIL",
            sentence_count=0,
            max_sentence_words=0,
            warnings=(),
            failures=("empty narration text",),
            detail="Narration empty.",
        )
    if _JOINED_SENTENCES.search(body):
        failures.append("two sentences concatenated without whitespace")
    if _SSML_INSIDE_WORD.search(body):
        failures.append("SSML tag inserted inside a word")

    # Paragraph-level terminal punctuation (allow invocation forms).
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    for idx, para in enumerate(paragraphs, start=1):
        compact = " ".join(para.split())
        if _INVOCATION_OK.search(compact):
            continue
        if not _TERMINAL_OK.search(compact):
            failures.append(f"paragraph {idx} lacks terminal sentence punctuation")

    # Sentence fragments / mid-word endings.
    rough = re.split(r"(?<=[.!?…])\s+", body)
    sentences = [s.strip() for s in rough if s.strip()]
    max_words = 0
    for sent in sentences:
        words = _WORD_RE.findall(sent)
        max_words = max(max_words, len(words))
        if len(words) >= warn_sentence_words:
            warnings.append(f"long sentence ({len(words)} words)")
        if len(words) >= fail_sentence_words:
            failures.append(f"run-on sentence ({len(words)} words) without adequate punctuation")
        # Unfinished quotation / mid-word
        if sent.endswith((" “", ' "', " '")) or re.search(r'\b(let us|don\'t|can\'t)\s*$', sent, re.I):
            if not _TERMINAL_OK.search(sent) and sent.count('"') + sent.count("“") + sent.count("”") == 1:
                failures.append(f"unfinished quotation/fragment: {sent[-40:]!r}")
        token = sent.rstrip('"”\'').split()[-1] if sent.split() else ""
        if token and _MID_WORD_END.fullmatch(token) and not _TERMINAL_OK.search(sent):
            # Single/double letter trailing token often means truncation ("t", "h")
            if len(token) <= 2 and token.lower() not in {"i", "a", "ok"}:
                failures.append(f"possible mid-word ending: {token!r}")

    if len(sentences) < min_sentences:
        failures.append(f"only {len(sentences)} sentence(s); need at least {min_sentences}")

    # Punctuation density: at least one terminator per ~45 words for bedtime prose.
    words = _WORD_RE.findall(body)
    terminators = len(re.findall(r"[.!?…]", body))
    if words and terminators * 45 < len(words):
        failures.append(
            f"punctuation density too low ({terminators} terminators / {len(words)} words)"
        )

    status = "PASS" if not failures else "FAIL"
    return PunctuationGateResult(
        status=status,
        sentence_count=len(sentences),
        max_sentence_words=max_words,
        warnings=tuple(warnings[:20]),
        failures=tuple(failures[:30]),
        detail="; ".join(failures) if failures else "Punctuation and sentence boundaries OK.",
    )


__all__ = ["PunctuationGateResult", "evaluate_punctuation_gate"]
