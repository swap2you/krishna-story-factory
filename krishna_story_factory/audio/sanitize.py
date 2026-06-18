from __future__ import annotations

import re

_V3_ALLOWED_TAGS = frozenset(
    {
        "softly",
        "gently",
        "with wonder",
        "with concern",
        "with relief",
        "gentle pause",
        "warmly",
        "reverently",
    }
)

_PAUSE_PATTERN = re.compile(r"\[\s*pause\s*\]", re.IGNORECASE)
_BRACKET_TAG_PATTERN = re.compile(r"\[([^\]]+)\]")
_STANDALONE_PAUSE_WORD = re.compile(r"(?<![a-zA-Z])pause(?![a-zA-Z])", re.IGNORECASE)


def is_v3_model(model_id: str) -> bool:
    return "v3" in (model_id or "").lower()


def sanitize_audio_script(text: str, *, model_id: str) -> str:
    """Prepare narration text for ElevenLabs without spoken pause directions."""
    cleaned = text.strip()
    cleaned = _PAUSE_PATTERN.sub('<break time="1.2s" />', cleaned)

    if is_v3_model(model_id):
        cleaned = _sanitize_v3_tags(cleaned)
    else:
        cleaned = _strip_unsupported_bracket_tags(cleaned)

    cleaned = _remove_standalone_pause_word(cleaned)
    return cleaned.strip()


def _sanitize_v3_tags(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        inner = match.group(1).strip().lower()
        if inner in _V3_ALLOWED_TAGS:
            return match.group(0)
        if inner == "pause":
            return '<break time="1.2s" />'
        return ""

    return _BRACKET_TAG_PATTERN.sub(repl, text)


def _strip_unsupported_bracket_tags(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        inner = match.group(1).strip().lower()
        if inner == "pause":
            return '<break time="1.2s" />'
        return ""

    return _BRACKET_TAG_PATTERN.sub(repl, text)


def _remove_standalone_pause_word(text: str) -> str:
    return _STANDALONE_PAUSE_WORD.sub("", text)
