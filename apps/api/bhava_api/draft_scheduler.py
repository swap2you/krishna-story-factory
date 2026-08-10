"""Private draft scheduler for Knowledge / Vāṇī work (Unified Platform M4).

Controls schedule status only. Explicitly cannot approve, merge, deploy, publish,
or invoke Story Factory generation entrypoints.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DraftQueueChoice(str, Enum):
    KNOWLEDGE = "knowledge"
    VANI = "vani"
    AUDIO_PILOT = "audio_pilot"


class DraftScheduleStatus(str, Enum):
    DISABLED = "disabled"
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING_DRY_RUN = "running_dry_run"
    RETRY_WAIT = "retry_wait"
    BLOCKED = "blocked"
    COMPLETED_DRY_RUN = "completed_dry_run"


FORBIDDEN_CAPABILITIES = frozenset(
    {
        "approve",
        "merge",
        "deploy",
        "publish",
        "story_generation",
        "run_daily_story",
        "generate-next",
        "create-next-bhava-story",
    }
)

# Story generation entrypoints this module must never import or call.
STORY_GENERATION_ENTRYPOINTS = frozenset(
    {
        "krishna_story_factory.pipeline.run_daily_story",
        "run_daily_story.py",
        "scripts/run_daily_story_scheduled.ps1",
        "scripts/create-next-bhava-story.ps1",
        "bhava_api.factory_adapter.perform",
        "/api/v1/local/generate-next",
    }
)


class CostLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_usd_per_run: float = Field(default=0.0, ge=0.0)
    max_usd_per_day: float = Field(default=0.0, ge=0.0)
    paid_providers_allowed: bool = False


class DraftSchedulerControls(BaseModel):
    """Operator-facing controls for private draft work only."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    dry_run: bool = True
    queue: DraftQueueChoice = DraftQueueChoice.KNOWLEDGE
    idempotency_key: str | None = None
    max_retries: int = Field(default=0, ge=0, le=5)
    retry_count: int = Field(default=0, ge=0)
    cost_limits: CostLimits = Field(default_factory=CostLimits)
    status: DraftScheduleStatus = DraftScheduleStatus.DISABLED
    last_log: str | None = None


class DraftSchedulerCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    can_schedule_private_draft: bool = True
    can_dry_run: bool = True
    can_disable: bool = True
    can_approve: Literal[False] = False
    can_merge: Literal[False] = False
    can_deploy: Literal[False] = False
    can_publish: Literal[False] = False
    can_trigger_story_generation: Literal[False] = False


class DraftSchedulerState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    controls: DraftSchedulerControls
    capabilities: DraftSchedulerCapabilities = Field(default_factory=DraftSchedulerCapabilities)
    forbidden: list[str] = Field(default_factory=lambda: sorted(FORBIDDEN_CAPABILITIES))
    story_scheduler_unchanged: bool = True
    note: str = (
        "Private draft scheduler only. Cannot approve, merge, deploy, publish, "
        "or call Story Factory generation."
    )


_STATE = DraftSchedulerControls(enabled=False, dry_run=True, status=DraftScheduleStatus.DISABLED)


def get_state() -> DraftSchedulerState:
    return DraftSchedulerState(controls=_STATE)


def set_enabled(enabled: bool) -> DraftSchedulerState:
    global _STATE
    if not enabled:
        _STATE = _STATE.model_copy(
            update={"enabled": False, "status": DraftScheduleStatus.DISABLED, "last_log": "disabled by operator"}
        )
    else:
        _STATE = _STATE.model_copy(
            update={
                "enabled": True,
                "status": DraftScheduleStatus.IDLE if _STATE.dry_run else DraftScheduleStatus.BLOCKED,
                "last_log": "enabled; dry-run required until paid limits configured",
            }
        )
    return get_state()


def configure(
    *,
    queue: DraftQueueChoice | None = None,
    dry_run: bool | None = None,
    idempotency_key: str | None = None,
    max_retries: int | None = None,
    cost_limits: CostLimits | None = None,
) -> DraftSchedulerState:
    global _STATE
    updates: dict[str, Any] = {}
    if queue is not None:
        updates["queue"] = queue
    if dry_run is not None:
        updates["dry_run"] = dry_run
    if idempotency_key is not None:
        updates["idempotency_key"] = idempotency_key
    if max_retries is not None:
        updates["max_retries"] = max_retries
    if cost_limits is not None:
        updates["cost_limits"] = cost_limits
    if updates:
        _STATE = _STATE.model_copy(update=updates)
        if not _STATE.enabled:
            _STATE = _STATE.model_copy(update={"status": DraftScheduleStatus.DISABLED})
        elif not _STATE.dry_run and not _STATE.cost_limits.paid_providers_allowed:
            _STATE = _STATE.model_copy(
                update={
                    "status": DraftScheduleStatus.BLOCKED,
                    "last_log": "non-dry-run blocked: paid providers not allowed",
                }
            )
        elif _STATE.status == DraftScheduleStatus.DISABLED:
            _STATE = _STATE.model_copy(update={"status": DraftScheduleStatus.IDLE})
    return get_state()


def enqueue_dry_run(idempotency_key: str) -> DraftSchedulerState:
    """Queue a private dry-run. Never invokes story generation."""
    global _STATE
    if not _STATE.enabled:
        _STATE = _STATE.model_copy(
            update={"status": DraftScheduleStatus.DISABLED, "last_log": "enqueue refused: disabled"}
        )
        return get_state()
    if not _STATE.dry_run:
        _STATE = _STATE.model_copy(
            update={"status": DraftScheduleStatus.BLOCKED, "last_log": "enqueue refused: dry_run required"}
        )
        return get_state()
    if _STATE.idempotency_key and _STATE.idempotency_key == idempotency_key:
        _STATE = _STATE.model_copy(
            update={
                "status": DraftScheduleStatus.COMPLETED_DRY_RUN,
                "last_log": f"idempotent replay for key={idempotency_key}",
            }
        )
        return get_state()
    _STATE = _STATE.model_copy(
        update={
            "idempotency_key": idempotency_key,
            "status": DraftScheduleStatus.COMPLETED_DRY_RUN,
            "retry_count": 0,
            "last_log": (
                f"dry-run completed for queue={_STATE.queue.value} key={idempotency_key}; "
                "no story generation entrypoints called"
            ),
        }
    )
    return get_state()


def refuse_forbidden(action: str) -> dict[str, Any]:
    return {
        "status": "refused",
        "action": action,
        "detail": f"Draft scheduler cannot perform '{action}'.",
        "forbidden": sorted(FORBIDDEN_CAPABILITIES),
        "can_trigger_story_generation": False,
    }


def asserts_no_story_generation_imports() -> None:
    """Static safety: this module must not pull Story Factory pipeline symbols."""
    import sys

    banned_prefixes = (
        "krishna_story_factory.pipeline",
        "krishna_story_factory.scheduler_simulate",
    )
    leaked = [name for name in sys.modules if name.startswith(banned_prefixes)]
    if leaked:
        raise RuntimeError(f"draft_scheduler must not load story modules: {leaked}")
