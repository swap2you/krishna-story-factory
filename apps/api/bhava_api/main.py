"""FastAPI application factory for the read-only Bhāva portal."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text

from .catalog.filesystem import discover_packages
from .catalog.freshness import catalog_freshness, refresh_if_stale
from .config import get_settings
from .csrf import issue_token
from .db import Base, SessionLocal, engine
from .knowledge.routes import router as knowledge_router
from .routes import media, public as public_routes, reader


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    catalog_freshness.min_interval_sec = settings.catalog_refresh_sec
    _validate_public_content()

    settings.catalog_db.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        app.state.indexed_packages = refresh_if_stale(session=session, force=True)

    app.state.csrf_token = issue_token()
    app.state.ready = True
    stop = asyncio.Event()

    async def _background_refresh() -> None:
        while not stop.is_set():
            try:
                await asyncio.to_thread(refresh_if_stale)
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
        return {"status": "ready", "service": "bhava-api"}

    @app.get("/api/v1/version", include_in_schema=False)
    def version() -> dict[str, str | int]:
        return {
            "service": "bhava-api",
            "release_sha": settings.release_sha,
            "environment": settings.environment,
            "public_story_max": settings.public_story_max,
        }

    return app


app = create_app()
