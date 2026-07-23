"""Configuration for the isolated Bhāva portal application."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _cors_origins() -> tuple[str, ...]:
    raw = os.getenv("BHAVA_WEB_ORIGINS", "").strip()
    if raw:
        return tuple(origin.strip() for origin in raw.split(",") if origin.strip())
    web_url = os.getenv("BHAVA_WEB_URL", "").strip().rstrip("/")
    if web_url:
        origins = {web_url}
        if "127.0.0.1" in web_url:
            origins.add(web_url.replace("127.0.0.1", "localhost"))
        elif "localhost" in web_url:
            origins.add(web_url.replace("localhost", "127.0.0.1"))
        return tuple(sorted(origins))
    # Safe local defaults spanning the dynamic web range preferences.
    ports = (3000, 3001, 3002, 3003)
    origins: list[str] = []
    for port in ports:
        origins.append(f"http://127.0.0.1:{port}")
        origins.append(f"http://localhost:{port}")
    return tuple(origins)


@dataclass(frozen=True)
class Settings:
    repository_root: Path
    output_root: Path
    catalog_db: Path
    factory_actions_enabled: bool
    enforce_loopback: bool
    cors_origins: tuple[str, ...]
    catalog_refresh_sec: float


def get_settings() -> Settings:
    root = Path(os.getenv("BHAVA_REPOSITORY_ROOT", Path(__file__).resolve().parents[3]))
    catalog_db = Path(
        os.getenv("BHAVA_CATALOG_DB", str(root / "data" / "catalog" / "bhava.sqlite"))
    )
    refresh = float(os.getenv("BHAVA_CATALOG_REFRESH_SEC", "20"))
    return Settings(
        repository_root=root,
        output_root=Path(os.getenv("BHAVA_OUTPUT_ROOT", str(root / "output"))),
        catalog_db=catalog_db,
        factory_actions_enabled=_as_bool("BHAVA_FACTORY_ACTIONS_ENABLED", False),
        enforce_loopback=_as_bool("BHAVA_ENFORCE_LOOPBACK", True),
        cors_origins=_cors_origins(),
        catalog_refresh_sec=max(15.0, min(refresh, 30.0)),
    )
