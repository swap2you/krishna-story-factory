"""Knowledge Library API routes."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query, Request

from ..knowledge.governance import evaluate_publication
from ..knowledge.packages import get_package, is_loopback_host, list_packages, validate_package
from ..knowledge.search import POSTGRES_DDL, search_knowledge

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


def _require_private_access(request: Request, x_bhava_studio: str | None, x_bhava_studio_secret: str | None) -> None:
    """Private Knowledge access requires loopback plus studio secret — not a forgeable '1' header alone."""
    import os

    client_host = request.client.host if request.client else None
    if not is_loopback_host(client_host):
        raise HTTPException(status_code=403, detail="Private Knowledge access requires loopback")
    expected = (os.environ.get("BHAVA_STUDIO_BOOTSTRAP_TOKEN") or "").strip()
    if not expected:
        # Local-only default still requires explicit local marker env when unset is forbidden for private.
        expected = "bhava-local-studio"
    provided = (x_bhava_studio_secret or "").strip()
    if provided != expected:
        raise HTTPException(
            status_code=403,
            detail="Private Knowledge access requires studio secret (forgeable X-Bhava-Studio:1 is not sufficient)",
        )
    # Intentionally ignore x_bhava_studio == "1" as sole credential.
    _ = x_bhava_studio


@router.get("/search")
def knowledge_search(
    request: Request,
    q: str = Query(""),
    include_private: bool = Query(False),
    lifecycle: str | None = None,
    content_type: str | None = None,
    x_bhava_studio: str | None = Header(default=None),
    x_bhava_studio_secret: str | None = Header(default=None),
):
    if include_private:
        _require_private_access(request, x_bhava_studio, x_bhava_studio_secret)
    return search_knowledge(
        q,
        include_private=include_private,
        facet_lifecycle=lifecycle,
        facet_type=content_type,
    )


@router.get("/packages")
def knowledge_packages(
    request: Request,
    x_bhava_studio: str | None = Header(default=None),
    x_bhava_studio_secret: str | None = Header(default=None),
):
    _require_private_access(request, x_bhava_studio, x_bhava_studio_secret)
    rows = []
    for pkg in list_packages():
        record = pkg["record"]
        rows.append(
            {
                "record_id": record.get("record_id"),
                "slug": record.get("slug"),
                "title": record.get("title"),
                "source_status": record.get("source_status"),
                "lifecycle": record.get("lifecycle"),
                "visibility": record.get("visibility"),
                "fixture": bool(record.get("fixture")),
            }
        )
    return {"packages": rows}


@router.get("/packages/{slug}")
def knowledge_package_detail(
    slug: str,
    request: Request,
    x_bhava_studio: str | None = Header(default=None),
    x_bhava_studio_secret: str | None = Header(default=None),
):
    _require_private_access(request, x_bhava_studio, x_bhava_studio_secret)
    pkg = get_package(slug)
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    result = validate_package(pkg)
    if not result.ok:
        raise HTTPException(status_code=422, detail={"errors": result.errors})
    # Do not expose filesystem path
    safe = {k: v for k, v in pkg.items() if not k.startswith("_")}
    return safe


@router.post("/gates/evaluate")
def gates_evaluate(payload: dict):
    result = evaluate_publication(payload)
    return {"ok": result.ok, "reasons": result.reasons}


@router.get("/postgres-ddl")
def postgres_ddl():
    return {"ddl": POSTGRES_DDL, "note": "PostgreSQL-ready adapter DDL for Knowledge search."}
