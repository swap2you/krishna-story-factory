from __future__ import annotations

import re
from pathlib import Path

MASTER_PROMPT = "prompts/DAILY_STORY_MASTER.md"
_SECTION_RE = re.compile(r"^##\s+([A-Z_]+)\s*$", re.MULTILINE)


def load_project_text(project_root: Path, relative_path: str) -> str:
    path = project_root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def load_master_sections(project_root: Path) -> dict[str, str]:
    text = load_project_text(project_root, MASTER_PROMPT)
    if not text:
        return {}
    matches = list(_SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()
    return sections


def load_master_section(project_root: Path, section: str) -> str:
    return load_master_sections(project_root).get(section.upper(), "")
