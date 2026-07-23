"""FastAPI application factory for the read-only Bhāva portal."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .catalog.freshness import catalog_freshness, refresh_if_stale
from .config import get_settings
from .csrf import issue_token
from .db import Base, SessionLocal, engine
from .routes import local_factory, media, public, reader


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    catalog_freshness.min_interval_sec = settings.catalog_refresh_sec
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        app.state.indexed_packages = refresh_if_stale(session=session, force=True)
    app.state.csrf_token = issue_token()

    stop = asyncio.Event()

    async def _background_refresh() -> None:
        while not stop.is_set():
            try:
                await asyncio.to_thread(refresh_if_stale)
            except Exception:
                pass
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.catalog_refresh_sec)
            except asyncio.TimeoutError:
                continue

    task = asyncio.create_task(_background_refresh())
    yield
    stop.set()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Bhāva Portal API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(public.router)
    app.include_router(media.router)
    app.include_router(reader.router)
    app.include_router(local_factory.router)
    return app


app = create_app()
