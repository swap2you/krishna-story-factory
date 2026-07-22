"""Configuration for the isolated Bhāva portal application."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    repository_root: Path
    output_root: Path
    catalog_db: Path
    factory_actions_enabled: bool
    enforce_loopback: bool


def get_settings() -> Settings:
    root = Path(os.getenv("BHAVA_REPOSITORY_ROOT", Path(__file__).resolve().parents[3]))
    return Settings(
        repository_root=root,
        output_root=root / "output",
        catalog_db=root / "data" / "catalog" / "bhava.sqlite",
        factory_actions_enabled=_as_bool("BHAVA_FACTORY_ACTIONS_ENABLED", False),
        enforce_loopback=_as_bool("BHAVA_ENFORCE_LOOPBACK", True),
    )
