"""Loopback-only private draft scheduler routes (Knowledge / Vāṇī).

Does not mount Story Factory generation controls and cannot approve/merge/deploy/publish.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from ..csrf import require_csrf
from ..draft_scheduler import (
    CostLimits,
    DraftQueueChoice,
    configure,
    enqueue_dry_run,
    get_state,
    refuse_forbidden,
    set_enabled,
)
from .local_factory import require_loopback

router = APIRouter(prefix="/api/v1/local/draft-scheduler", tags=["draft-scheduler"])


class ConfigureBody(BaseModel):
    queue: DraftQueueChoice | None = None
    dry_run: bool | None = True
    idempotency_key: str | None = None
    max_retries: int | None = Field(default=None, ge=0, le=5)
    max_usd_per_run: float | None = Field(default=None, ge=0.0)
    max_usd_per_day: float | None = Field(default=None, ge=0.0)
    paid_providers_allowed: bool | None = False


class EnqueueBody(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=128)


@router.get("", dependencies=[Depends(require_loopback)])
def draft_scheduler_status() -> dict:
    return get_state().model_dump(mode="json")


@router.post("/enable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_enable() -> dict:
    return set_enabled(True).model_dump(mode="json")


@router.post("/disable", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_disable() -> dict:
    return set_enabled(False).model_dump(mode="json")


@router.post("/configure", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_configure(body: ConfigureBody) -> dict:
    limits = None
    if any(
        value is not None
        for value in (body.max_usd_per_run, body.max_usd_per_day, body.paid_providers_allowed)
    ):
        current = get_state().controls.cost_limits
        limits = CostLimits(
            max_usd_per_run=body.max_usd_per_run if body.max_usd_per_run is not None else current.max_usd_per_run,
            max_usd_per_day=body.max_usd_per_day if body.max_usd_per_day is not None else current.max_usd_per_day,
            paid_providers_allowed=bool(body.paid_providers_allowed)
            if body.paid_providers_allowed is not None
            else current.paid_providers_allowed,
        )
    return configure(
        queue=body.queue,
        dry_run=body.dry_run,
        idempotency_key=body.idempotency_key,
        max_retries=body.max_retries,
        cost_limits=limits,
    ).model_dump(mode="json")


@router.post("/enqueue-dry-run", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_enqueue(body: EnqueueBody) -> dict:
    return enqueue_dry_run(body.idempotency_key).model_dump(mode="json")


@router.post("/approve", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_approve_refused() -> dict:
    return refuse_forbidden("approve")


@router.post("/merge", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_merge_refused() -> dict:
    return refuse_forbidden("merge")


@router.post("/deploy", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_deploy_refused() -> dict:
    return refuse_forbidden("deploy")


@router.post("/publish", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_publish_refused() -> dict:
    return refuse_forbidden("publish")


@router.post("/generate-story", dependencies=[Depends(require_loopback), Depends(require_csrf)])
def draft_scheduler_generate_story_refused(_request: Request) -> dict:
    return refuse_forbidden("story_generation")
