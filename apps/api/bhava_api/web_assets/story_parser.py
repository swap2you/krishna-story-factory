"""Parse raw story.md and separate public reader content from internal production blocks.

Internal blocks live inside HTML comments (<!-- ... -->) and contain:
Audio Narration, Poster Visual Brief, Coloring Visual Brief, Activity Data, SSML tags.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

_INTERNAL_HEADING_PATTERNS: tuple[str, ...] = (
    r"^#+\s*Audio\s+Narration",
    r"^#+\s*Poster\s+Visual\s+Brief",
    r"^#+\s*Coloring\s+Visual\s+Brief",
    r"^#+\s*Simple\s+Coloring\s+Visual\s+Brief",
    r"^#+\s*Activity\s+Data",
    r"^#+\s*SSML",
)

_INTERNAL_HEADING_RE = re.compile(
    "|".join(_INTERNAL_HEADING_PATTERNS), re.IGNORECASE | re.MULTILINE
)

_LEAK_MARKERS: tuple[str, ...] = (
    "Audio Narration",
    "Poster Visual Brief",
    "Coloring Visual Brief",
    "Activity Data",
    "<break time=",
    "&lt;break",
)

_SSML_BREAK_RE = re.compile(r"<break\s+time=[^>]*>", re.IGNORECASE)


@dataclass
class ParsedStory:
    reader_md: str
    reader_txt: str
    narration_txt: str
    has_internal_leak_markers: bool


def _extract_narration(raw: str) -> str:
    """Pull the Audio Narration block from inside HTML comments, stripping SSML."""
    for match in _COMMENT_RE.finditer(raw):
        block = match.group(0)
        if re.search(r"#+\s*Audio\s+Narration", block, re.IGNORECASE):
            lines = block.splitlines()
            narration_lines: list[str] = []
            capture = False
            for line in lines:
                if re.match(r"#+\s*Audio\s+Narration", line.strip(), re.IGNORECASE):
                    capture = True
                    continue
                if capture and re.match(r"#+\s+", line.strip()):
                    break
                if capture:
                    narration_lines.append(line)
            text = "\n".join(narration_lines).strip()
            text = _SSML_BREAK_RE.sub("", text)
            text = text.replace("<!--", "").replace("-->", "").strip()
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text
    return ""


def _strip_internal_heading_sections(md: str) -> str:
    """Remove any internal-heading sections that leaked outside HTML comments."""
    lines = md.splitlines(keepends=True)
    result: list[str] = []
    skipping = False
    skip_level = 0

    for line in lines:
        stripped = line.strip()
        heading_match = re.match(r"^(#+)\s+", stripped)

        if _INTERNAL_HEADING_RE.match(stripped):
            skipping = True
            skip_level = len(heading_match.group(1)) if heading_match else 1
            continue

        if skipping:
            if heading_match and len(heading_match.group(1)) <= skip_level:
                skipping = False
            else:
                continue

        result.append(line)

    return "".join(result)


def _md_to_plain(md: str) -> str:
    """Minimal markdown-to-plaintext: strip heading markers, keep structure."""
    lines: list[str] = []
    for line in md.splitlines():
        cleaned = re.sub(r"^#+\s+", "", line)
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)
        lines.append(cleaned)
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def parse_story_markdown(raw: str) -> ParsedStory:
    """Parse raw story.md, returning clean reader content and extracted narration.

    Returns a ParsedStory with:
    - reader_md:  public-safe markdown (no HTML comments, no internal headings)
    - reader_txt: plain-text version of reader_md
    - narration_txt: extracted Audio Narration text (SSML stripped)
    - has_internal_leak_markers: True if reader_md still contains leak indicators
    """
    narration_txt = _extract_narration(raw)

    cleaned = _COMMENT_RE.sub("", raw)
    cleaned = _strip_internal_heading_sections(cleaned)
    cleaned = _SSML_BREAK_RE.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    has_leak = any(marker in cleaned for marker in _LEAK_MARKERS)

    reader_txt = _md_to_plain(cleaned)

    return ParsedStory(
        reader_md=cleaned,
        reader_txt=reader_txt,
        narration_txt=narration_txt,
        has_internal_leak_markers=has_leak,
    )
