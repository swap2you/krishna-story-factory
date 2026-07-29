"""Resumable stage checkpoints for atomic story production."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

STAGE_ORDER = (
    "story",
    "narration",
    "poster",
    "detailed_coloring",
    "simple_coloring",
    "activity_pdf",
    "whatsapp_caption",
    "manifest",
    "quality_gate",
    "atomic_publish",
    "drive_sync",
)

STATUS_PENDING = "pending"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

STATE_FILENAME = "stage_state.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]


def recovery_root(project_root: Path, story_id: str, run_id: str) -> Path:
    return project_root / "work" / "stories" / story_id.zfill(3) / run_id


def package_dir(run_root: Path) -> Path:
    return run_root / "package"


@dataclass
class StageState:
    story_id: str
    run_id: str
    stages: dict[str, str] = field(default_factory=dict)
    checksums: dict[str, str] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    last_errors: dict[str, str] = field(default_factory=dict)
    provider_request_ids: dict[str, str] = field(default_factory=dict)
    updated_at: str = ""
    recovery_enabled: bool = False

    def __post_init__(self) -> None:
        for name in STAGE_ORDER:
            self.stages.setdefault(name, STATUS_PENDING)
            self.attempts.setdefault(name, 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "story_id": self.story_id,
            "run_id": self.run_id,
            "stages": dict(self.stages),
            "checksums": dict(self.checksums),
            "attempts": dict(self.attempts),
            "last_errors": dict(self.last_errors),
            "provider_request_ids": dict(self.provider_request_ids),
            "updated_at": self.updated_at,
            "recovery_enabled": self.recovery_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StageState":
        return cls(
            story_id=str(data.get("story_id") or ""),
            run_id=str(data.get("run_id") or ""),
            stages=dict(data.get("stages") or {}),
            checksums=dict(data.get("checksums") or {}),
            attempts={k: int(v) for k, v in dict(data.get("attempts") or {}).items()},
            last_errors=dict(data.get("last_errors") or {}),
            provider_request_ids=dict(data.get("provider_request_ids") or {}),
            updated_at=str(data.get("updated_at") or ""),
            recovery_enabled=bool(data.get("recovery_enabled")),
        )

    def is_complete(self, stage: str) -> bool:
        return self.stages.get(stage) == STATUS_COMPLETE

    def mark(
        self,
        stage: str,
        status: str,
        *,
        checksum: str = "",
        error: str = "",
        provider_request_id: str = "",
    ) -> None:
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage}")
        self.stages[stage] = status
        self.attempts[stage] = int(self.attempts.get(stage, 0)) + (1 if status != STATUS_PENDING else 0)
        if checksum:
            self.checksums[stage] = checksum
        if error:
            self.last_errors[stage] = error[:2000]
        elif status == STATUS_COMPLETE:
            self.last_errors.pop(stage, None)
        if provider_request_id:
            self.provider_request_ids[stage] = provider_request_id
        self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")


def state_path(run_root: Path) -> Path:
    return run_root / STATE_FILENAME


def load_state(run_root: Path) -> StageState | None:
    path = state_path(run_root)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return StageState.from_dict(data)


def save_state(run_root: Path, state: StageState) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    path = state_path(run_root)
    tmp = path.with_suffix(".tmp")
    state.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def mark_file_stage(run_root: Path, state: StageState, stage: str, path: Path) -> None:
    if not path.is_file() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"Cannot complete stage {stage}: missing {path}")
    state.mark(stage, STATUS_COMPLETE, checksum=_sha256(path))
    save_state(run_root, state)


def production_recovery_enabled(*, cli_flag: bool = False) -> bool:
    if cli_flag:
        return True
    return os.getenv("BHAVA_ENABLE_PRODUCTION_RECOVERY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def find_latest_recovery_run(project_root: Path, story_id: str) -> Path | None:
    root = project_root / "work" / "stories" / story_id.zfill(3)
    if not root.is_dir():
        return None
    candidates = [
        p
        for p in root.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not (p / "COMPLETED").is_file()
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.name)[-1]


def seed_state_from_recovery_artifacts(run_root: Path, story_id: str) -> StageState:
    """Build or refresh stage state from preserved story/narration files."""
    existing = load_state(run_root)
    state = existing or StageState(story_id=story_id.zfill(3), run_id=run_root.name)
    pkg = package_dir(run_root)
    # Recovery layouts may keep artifacts at run root (008 quarantine) or under package/.
    story = pkg / "story.md" if (pkg / "story.md").is_file() else run_root / "story.md"
    narration = pkg / "narration.mp3" if (pkg / "narration.mp3").is_file() else run_root / "narration.mp3"
    if story.is_file():
        state.mark("story", STATUS_COMPLETE, checksum=_sha256(story))
    if narration.is_file():
        state.mark("narration", STATUS_COMPLETE, checksum=_sha256(narration))
    save_state(run_root, state)
    return state


def ensure_package_layout(run_root: Path) -> Path:
    """Ensure package/ contains reusable story + narration; return package dir."""
    pkg = package_dir(run_root)
    pkg.mkdir(parents=True, exist_ok=True)
    for name in ("story.md", "narration.mp3"):
        dest = pkg / name
        src = run_root / name
        if not dest.is_file() and src.is_file():
            dest.write_bytes(src.read_bytes())
    chunks_src = run_root / ".narration_chunks"
    chunks_dest = pkg / ".narration_chunks"
    if chunks_src.is_dir() and not chunks_dest.exists():
        import shutil

        shutil.copytree(chunks_src, chunks_dest)
    return pkg


def quarantine_incomplete_output_packages(output_root: Path, quarantine_root: Path) -> list[str]:
    """Move incomplete public packages out of output/; never delete evidence."""
    from .outputs import FINAL_OUTPUT_FILES

    moved: list[str] = []
    if not output_root.is_dir():
        return moved
    quarantine_root.mkdir(parents=True, exist_ok=True)
    for child in sorted(output_root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        names = {p.name for p in child.iterdir() if p.is_file()}
        if names == set(FINAL_OUTPUT_FILES):
            continue
        # Incomplete or polluted package — quarantine.
        dest = quarantine_root / f"{child.name}_{time.strftime('%Y%m%d_%H%M%S')}"
        import shutil

        shutil.move(str(child), str(dest))
        moved.append(str(dest))
        logger.warning("Quarantined incomplete output package to %s", dest)
    return moved
