"""FastAPI application factory for the read-only Bhāva portal."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text

from .catalog.filesystem import discover_packages
from .catalog.freshness import catalog_freshness, refresh_if_stale
from .catalog.readiness import CatalogReadinessError, catalog_snapshot, public_catalog_ready
from .config import Settings, get_settings
from .csrf import issue_token
from .db import Base, SessionLocal, engine
from .knowledge.routes import router as knowledge_router
from .routes import media, public as public_routes, reader

logger = logging.getLogger(__name__)

_REQUIRED_WEB_ASSET_FILES = (
    "reader.md",
    "reader.txt",
    "source_links.json",
    "reflections.json",
    "shlokas.json",
    "sync.json",
    "waveform.json",
    "web_manifest.json",
)


def _story_number(package) -> int:
    raw = str(package.manifest.get("chapter_no", "") or "")
    digits = "".join(char for char in raw if char.isdigit())
    return int(digits) if digits else 0


def _validate_public_content() -> None:
    settings = get_settings()
    if not settings.public_site:
        return
    packages = discover_packages(settings.output_root)
    invalid = [package.path.name for package in packages if _story_number(package) > settings.public_story_max]
    if invalid:
        raise RuntimeError(
            "Public content boundary violation: packages above "
            f"{settings.public_story_max:03d}: {', '.join(invalid)}"
        )


def _verify_public_web_assets(settings: Settings) -> None:
    """Fail readiness when required derived web assets are missing or invalid."""
    root = settings.web_assets_root
    if not root.is_dir():
        raise HTTPException(
            status_code=503,
            detail=f"web-assets root missing: {root}",
        )
    for number in range(1, settings.public_story_max + 1):
        story_no = f"{number:03d}"
        dest = root / story_no
        if not dest.is_dir():
            raise HTTPException(
                status_code=503,
                detail=f"web-assets missing for story {story_no}",
            )
        for name in _REQUIRED_WEB_ASSET_FILES:
            path = dest / name
            if not path.is_file() or path.stat().st_size < 1:
                raise HTTPException(
                    status_code=503,
                    detail=f"web-assets/{story_no}/{name} missing or empty",
                )
        try:
            manifest = json.loads((dest / "web_manifest.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=503,
                detail=f"web-assets/{story_no}/web_manifest.json invalid",
            ) from exc
        for field in ("package_manifest_sha256", "story_md_sha256", "generated_at", "assets"):
            if field not in manifest:
                raise HTTPException(
                    status_code=503,
                    detail=f"web-assets/{story_no}/web_manifest.json missing {field}",
                )
        assets = manifest.get("assets")
        if not isinstance(assets, dict):
            raise HTTPException(
                status_code=503,
                detail=f"web-assets/{story_no}/web_manifest.json assets invalid",
            )
        for name in _REQUIRED_WEB_ASSET_FILES:
            if name == "web_manifest.json":
                continue
            meta = assets.get(name)
            if not isinstance(meta, dict):
                raise HTTPException(
                    status_code=503,
                    detail=f"web-assets/{story_no}/web_manifest.json missing assets.{name}",
                )
            sha = meta.get("sha256")
            size = meta.get("bytes")
            if not isinstance(sha, str) or len(sha) != 64:
                raise HTTPException(
                    status_code=503,
                    detail=f"web-assets/{story_no}/web_manifest.json bad sha for {name}",
                )
            if not isinstance(size, int) or size < 1:
                raise HTTPException(
                    status_code=503,
                    detail=f"web-assets/{story_no}/web_manifest.json bad bytes for {name}",
                )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    catalog_freshness.min_interval_sec = settings.catalog_refresh_sec
    _validate_public_content()

    settings.catalog_db.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    app.state.ready = False
    try:
        with SessionLocal() as session:
            app.state.indexed_packages = refresh_if_stale(session=session, force=True)
        app.state.ready = True
    except CatalogReadinessError:
        app.state.indexed_packages = 0
        app.state.ready = False
        logger.error("catalog_startup_incomplete public_site=%s", settings.public_site)

    app.state.csrf_token = issue_token()
    stop = asyncio.Event()

    async def _background_refresh() -> None:
        while not stop.is_set():
            try:
                await asyncio.to_thread(refresh_if_stale)
                if settings.public_site and not getattr(app.state, "ready", False):
                    with SessionLocal() as session:
                        public_catalog_ready(session, settings)
                    _verify_public_web_assets(settings)
                    app.state.ready = True
                    logger.info("catalog_ready_recovered_after_incomplete_startup")
            except Exception:
                # A refresh failure must not leak filesystem paths to clients.
                pass
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.catalog_refresh_sec)
            except asyncio.TimeoutError:
                continue

    task = asyncio.create_task(_background_refresh())
    try:
        yield
    finally:
        app.state.ready = False
        stop.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    settings = get_settings()
    public_mode = settings.public_site

    app = FastAPI(
        title="Bhāva Portal API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None if public_mode else "/docs",
        redoc_url=None if public_mode else "/redoc",
        openapi_url=None if public_mode else "/openapi.json",
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "HEAD", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "Range"],
        expose_headers=["Accept-Ranges", "Content-Range", "Content-Length", "ETag"],
        allow_credentials=False,
        max_age=3600,
    )

    app.include_router(public_routes.router)
    app.include_router(media.router)
    app.include_router(reader.router)
    app.include_router(knowledge_router)

    if not public_mode:
        from .routes import local_factory

        app.include_router(local_factory.router)

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok", "service": "bhava-api"}

    @app.get("/readyz", include_in_schema=False)
    def readyz() -> dict[str, str]:
        if not getattr(app.state, "ready", False):
            raise HTTPException(status_code=503, detail="not ready")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        if settings.public_site:
            _verify_public_web_assets(settings)
            try:
                with SessionLocal() as session:
                    public_catalog_ready(session, settings)
            except CatalogReadinessError as exc:
                raise HTTPException(status_code=503, detail="catalog not ready") from exc
        return {"status": "ready", "service": "bhava-api"}

    @app.get("/api/v1/version", include_in_schema=False)
    def version() -> dict[str, str | int]:
        short = settings.release_sha[:7] if settings.release_sha else "unknown"
        content_tag = (
            os.getenv("BHAVA_CONTENT_RELEASE", "").strip()
            or os.getenv("BHAVA_CONTENT_TAG", "").strip()
            or ""
        )
        payload: dict[str, str | int] = {
            "service": "bhava-api",
            "release_sha": settings.release_sha,
            "short_sha": short,
            "environment": settings.environment,
            "public_story_max": settings.public_story_max,
        }
        if content_tag:
            payload["content_tag"] = content_tag
        try:
            with SessionLocal() as session:
                snap = catalog_snapshot(session, settings)
            payload["indexed_story_count"] = snap.indexed_story_count
            payload["discovered_package_count"] = snap.discovered_package_count
        except Exception:
            payload["indexed_story_count"] = -1
            payload["discovered_package_count"] = -1
        return payload

    return app


app = create_app()
