"""Knowledge Library API routes."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from ..knowledge.governance import evaluate_publication
from ..knowledge.search import POSTGRES_DDL, search_knowledge

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.get("/search")
def knowledge_search(
    q: str = Query(""),
    include_private: bool = Query(False),
    lifecycle: str | None = None,
    content_type: str | None = None,
    x_bhava_studio: str | None = Header(default=None),
):
    # Private roadmap search requires studio header marker (local bootstrap).
    if include_private and x_bhava_studio != "1":
        raise HTTPException(status_code=403, detail="Private Knowledge search requires studio session")
    return search_knowledge(
        q,
        include_private=include_private,
        facet_lifecycle=lifecycle,
        facet_type=content_type,
    )


@router.post("/gates/evaluate")
def gates_evaluate(payload: dict):
    result = evaluate_publication(payload)
    return {"ok": result.ok, "reasons": result.reasons}


@router.get("/postgres-ddl")
def postgres_ddl():
    return {"ddl": POSTGRES_DDL, "note": "PostgreSQL-ready adapter DDL for Knowledge search."}
