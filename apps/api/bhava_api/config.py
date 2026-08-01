"""Configuration for the isolated Bhāva portal application."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    raw = os.getenv(name, default).strip()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _cors_origins() -> tuple[str, ...]:
    configured = _csv("BHAVA_WEB_ORIGINS")
    if configured:
        return configured
    web_url = os.getenv("BHAVA_WEB_URL", "").strip().rstrip("/")
    if web_url:
        return (web_url,)
    return (
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    )


@dataclass(frozen=True)
class Settings:
    repository_root: Path
    output_root: Path
    web_assets_root: Path
    catalog_db: Path
    factory_actions_enabled: bool
    enforce_loopback: bool
    cors_origins: tuple[str, ...]
    allowed_hosts: tuple[str, ...]
    catalog_refresh_sec: float
    auto_web_assets: bool
    web_assets_writable: bool
    public_site: bool
    public_story_max: int
    release_sha: str
    environment: str


def get_settings() -> Settings:
    root = Path(os.getenv("BHAVA_REPOSITORY_ROOT", Path(__file__).resolve().parents[3]))
    catalog_db = Path(
        os.getenv("BHAVA_CATALOG_DB", str(root / "data" / "catalog" / "bhava.sqlite"))
    )
    refresh = float(os.getenv("BHAVA_CATALOG_REFRESH_SEC", "20"))
    story_max = int(os.getenv("BHAVA_PUBLIC_STORY_MAX", "20"))
    release_sha = os.getenv("BHAVA_RELEASE_SHA", "development").strip() or "development"
    environment = os.getenv("BHAVA_ENVIRONMENT", "development").strip().lower()
    public_site = _as_bool("BHAVA_PUBLIC_SITE", False)

    web_assets_root = Path(
        os.getenv("BHAVA_WEB_ASSETS_ROOT", str(root / "data" / "web-assets"))
    )
    if "BHAVA_WEB_ASSETS_WRITABLE" in os.environ:
        web_assets_writable = _as_bool("BHAVA_WEB_ASSETS_WRITABLE", False)
    else:
        # Production/public containers never generate derived assets at runtime.
        web_assets_writable = not public_site

    return Settings(
        repository_root=root,
        output_root=Path(os.getenv("BHAVA_OUTPUT_ROOT", str(root / "output"))),
        web_assets_root=web_assets_root,
        catalog_db=catalog_db,
        factory_actions_enabled=_as_bool("BHAVA_FACTORY_ACTIONS_ENABLED", False),
        enforce_loopback=_as_bool("BHAVA_ENFORCE_LOOPBACK", True),
        cors_origins=_cors_origins(),
        allowed_hosts=_csv(
            "BHAVA_ALLOWED_HOSTS",
            "bhava.me,www.bhava.me,staging.bhava.me,localhost,127.0.0.1",
        ),
        catalog_refresh_sec=max(15.0, min(refresh, 30.0)),
        auto_web_assets=_as_bool("BHAVA_AUTO_WEB_ASSETS", False),
        web_assets_writable=web_assets_writable,
        public_site=public_site,
        public_story_max=max(1, min(story_max, 999)),
        release_sha=release_sha[:64],
        environment=environment,
    )
