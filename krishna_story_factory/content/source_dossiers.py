"""Governed source-fact dossiers for Stories 026–035 (Krishna Book Ch.18–27)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import unicodedata

import yaml


@dataclass(frozen=True, slots=True)
class SourceDossier:
    story_no: str
    kb_chapter: int
    title: str
    source_url: str
    required_events: tuple[str, ...]
    prohibited_contradictions: tuple[str, ...]
    required_phrases: tuple[str, ...] = ()
    forbidden_phrases: tuple[str, ...] = ()
    visual_restrictions: tuple[str, ...] = ()
    pronunciation_aliases: dict[str, str] = field(default_factory=dict)
    reviewer_state: str = "pending_owner_content_review"
    adaptation_notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceDossier":
        return cls(
            story_no=str(data["story_no"]).zfill(3),
            kb_chapter=int(data["kb_chapter"]),
            title=str(data["title"]),
            source_url=str(data["source_url"]),
            required_events=tuple(str(x) for x in data.get("required_events") or []),
            prohibited_contradictions=tuple(str(x) for x in data.get("prohibited_contradictions") or []),
            required_phrases=tuple(str(x) for x in data.get("required_phrases") or []),
            forbidden_phrases=tuple(str(x) for x in data.get("forbidden_phrases") or []),
            visual_restrictions=tuple(str(x) for x in data.get("visual_restrictions") or []),
            pronunciation_aliases=dict(data.get("pronunciation_aliases") or {}),
            reviewer_state=str(data.get("reviewer_state") or "pending_owner_content_review"),
            adaptation_notes=str(data.get("adaptation_notes") or ""),
        )


def dossier_root(project_root: Path) -> Path:
    return project_root / "data" / "source_dossiers"


def load_dossier(project_root: Path, story_no: str) -> SourceDossier | None:
    path = dossier_root(project_root) / f"{story_no.zfill(3)}.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid dossier YAML: {path}")
    return SourceDossier.from_dict(data)


def load_dossiers(project_root: Path, story_nos: tuple[str, ...] | None = None) -> dict[str, SourceDossier]:
    root = dossier_root(project_root)
    if not root.is_dir():
        return {}
    out: dict[str, SourceDossier] = {}
    for path in sorted(root.glob("*.yaml")):
        story = path.stem.zfill(3)
        if story_nos and story not in {s.zfill(3) for s in story_nos}:
            continue
        out[story] = load_dossier(project_root, story)
    return out


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text.lower()).strip()


def validate_dossier_text(dossier: SourceDossier, text: str) -> list[str]:
    """Deterministic source-fact checks against governed dossier."""
    errors: list[str] = []
    blob = _norm(text)
    for phrase in dossier.forbidden_phrases:
        if phrase.lower() in blob:
            errors.append(f"Story {dossier.story_no}: forbidden phrase {phrase!r}.")
    for pattern in dossier.prohibited_contradictions:
        if re.search(pattern, blob, re.I):
            errors.append(f"Story {dossier.story_no}: prohibited contradiction matched {pattern!r}.")
    for phrase in dossier.required_phrases:
        if phrase.lower() not in blob:
            errors.append(f"Story {dossier.story_no}: missing required phrase {phrase!r}.")
    for event in dossier.required_events:
        tokens = [t.strip().lower() for t in event.split("|") if t.strip()]
        if tokens and not any(t in blob for t in tokens):
            errors.append(f"Story {dossier.story_no}: missing required event coverage {event!r}.")
    return errors
