"""FastAPI application factory for the read-only Bhāva portal."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .catalog.indexer import index_packages
from .csrf import issue_token
from .db import Base, SessionLocal, engine
from .routes import local_factory, media, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        app.state.indexed_packages = index_packages(session)
    app.state.csrf_token = issue_token()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Bhāva Portal API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3002",
            "http://127.0.0.1:3002",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(public.router)
    app.include_router(media.router)
    app.include_router(local_factory.router)
    return app


app = create_app()
