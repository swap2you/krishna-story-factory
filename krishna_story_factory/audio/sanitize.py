from __future__ import annotations

import re

# Conservative Eleven v3 audio-tag allowlist only.
_V3_ALLOWED_TAGS = frozenset(
    {
        "softly",
        "gently",
        "warmly",
        "reassuringly",
    }
)

_PAUSE_PATTERN = re.compile(r"\[\s*pause\s*\]", re.IGNORECASE)
_BRACKET_TAG_PATTERN = re.compile(r"\[([^\]]+)\]")
_STANDALONE_PAUSE_WORD = re.compile(r"(?<![a-zA-Z])pause(?![a-zA-Z])", re.IGNORECASE)
_BREAK_TAG_PATTERN = re.compile(r"<break\b[^>]*/?>", re.IGNORECASE)


def is_v3_model(model_id: str) -> bool:
    return "v3" in (model_id or "").lower()


def sanitize_audio_script(text: str, *, model_id: str) -> str:
    """Prepare narration text for ElevenLabs without spoken pause directions."""
    cleaned = text.strip()
    # Never keep raw [pause] tags (spoken or residual); strip entirely.
    cleaned = _PAUSE_PATTERN.sub("", cleaned)
    cleaned = _BREAK_TAG_PATTERN.sub("", cleaned)

    if is_v3_model(model_id):
        cleaned = _sanitize_v3_tags(cleaned)
    else:
        cleaned = _strip_unsupported_bracket_tags(cleaned)

    cleaned = _remove_standalone_pause_word(cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _sanitize_v3_tags(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        inner = match.group(1).strip().lower()
        if inner in _V3_ALLOWED_TAGS:
            return match.group(0)
        return ""

    return _BRACKET_TAG_PATTERN.sub(repl, text)


def _strip_unsupported_bracket_tags(text: str) -> str:
    return _BRACKET_TAG_PATTERN.sub("", text)


def _remove_standalone_pause_word(text: str) -> str:
    return _STANDALONE_PAUSE_WORD.sub("", text)
