"""Private Knowledge draft factory (M2).

Deterministic 50-item queue with idempotency, resumability, per-stage retry,
duplicate detection, prompt-ledger path, cost counters, and dry-run mode.

HARD AUTHORITY BOUNDARY: zero approve / merge / deploy / publication power.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = ("queue", "scaffold", "duplicate_check", "ledger", "cost_tally")
FORBIDDEN_ACTIONS = frozenset({"approve", "merge", "deploy", "publish", "publication"})
FACTORY_VERSION = "1.0.0"
DEFAULT_QUEUE_SIZE = 50
MAX_STAGE_RETRIES = 2


class FactoryAuthorityError(PermissionError):
    """Raised when a caller attempts approval/merge/deploy/publication."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def factory_root(root: Path | None = None) -> Path:
    return (root or repo_root()) / "content" / "knowledge" / "factory"


def prompt_ledger_path(root: Path | None = None) -> Path:
    return factory_root(root) / "prompt_ledger_v1.json"


def default_status_path(root: Path | None = None) -> Path:
    return factory_root(root) / "state" / "draft_factory_status.json"


def batch_manifest_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "content" / "knowledge" / "batches" / "batch_25_manifest_v1.json"


def roadmap_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "content" / "knowledge" / "roadmap" / "records.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def idempotency_key(item_id: str, stage: str, factory_version: str = FACTORY_VERSION) -> str:
    payload = f"{item_id}|{stage}|{factory_version}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def assert_no_publication_authority(action: str) -> None:
    normalized = (action or "").strip().lower()
    if normalized in FORBIDDEN_ACTIONS:
        raise FactoryAuthorityError(
            f"Draft factory has zero {normalized} authority (M2 hard boundary)."
        )


@dataclass
class CostCounters:
    items_queued: int = 0
    items_processed: int = 0
    stages_executed: int = 0
    retries: int = 0
    duplicates_skipped: int = 0
    estimated_tokens: int = 0
    estimated_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "items_queued": self.items_queued,
            "items_processed": self.items_processed,
            "stages_executed": self.stages_executed,
            "retries": self.retries,
            "duplicates_skipped": self.duplicates_skipped,
            "estimated_tokens": self.estimated_tokens,
            "estimated_usd": self.estimated_usd,
        }


@dataclass
class FactoryState:
    run_id: str
    dry_run: bool
    queue: list[dict[str, Any]] = field(default_factory=list)
    completed_keys: list[str] = field(default_factory=list)
    item_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    costs: CostCounters = field(default_factory=CostCounters)
    started_at: str = ""
    updated_at: str = ""
    finished_at: str | None = None
    authority: dict[str, bool] = field(
        default_factory=lambda: {
            "approve": False,
            "merge": False,
            "deploy": False,
            "publish": False,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "factory_version": FACTORY_VERSION,
            "run_id": self.run_id,
            "dry_run": self.dry_run,
            "prompt_ledger": "content/knowledge/factory/prompt_ledger_v1.json",
            "stages": list(STAGES),
            "queue_size": len(self.queue),
            "queue": self.queue,
            "completed_keys": self.completed_keys,
            "item_states": self.item_states,
            "costs": self.costs.to_dict(),
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "finished_at": self.finished_at,
            "authority": self.authority,
            "publication_authority": False,
        }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_deterministic_queue(size: int = DEFAULT_QUEUE_SIZE, root: Path | None = None) -> list[dict[str, Any]]:
    """Build a stable 50-item private draft queue from batch-25 + roadmap fill."""
    root = root or repo_root()
    batch = _load_json(batch_manifest_path(root))
    roadmap = _load_json(roadmap_path(root))
    seen: set[str] = set()
    queue: list[dict[str, Any]] = []

    for row in batch.get("records") or []:
        item_id = str(row["id"])
        if item_id in seen:
            continue
        seen.add(item_id)
        queue.append(
            {
                "id": item_id,
                "title": row.get("title") or item_id,
                "kind": row.get("kind") or "unknown",
                "batch_state": row.get("state") or "draft",
                "public": bool(row.get("public")),
                "source": "batch_25_manifest_v1",
            }
        )

    for row in roadmap:
        if len(queue) >= size:
            break
        item_id = str(row.get("id") or "")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        queue.append(
            {
                "id": item_id,
                "title": row.get("title") or item_id,
                "kind": "roadmap",
                "batch_state": "draft",
                "public": False,
                "source": "roadmap_fill",
            }
        )

    # Deterministic order: already batch-first then roadmap id order as loaded.
    queue = queue[:size]
    for idx, item in enumerate(queue, start=1):
        item["ord"] = idx
        item["idempotency_seed"] = idempotency_key(item["id"], "queue")
    return queue


def _stage_ok(item: dict[str, Any], stage: str, seen_ids: set[str], costs: CostCounters) -> tuple[bool, str]:
    item_id = item["id"]
    if stage == "queue":
        return True, "queued"
    if stage == "duplicate_check":
        if item_id in seen_ids:
            costs.duplicates_skipped += 1
            return False, "duplicate"
        seen_ids.add(item_id)
        return True, "unique"
    if stage == "scaffold":
        # Metadata-only scaffold; never invent scripture bodies.
        if item.get("public") and item.get("kind") in {"article", "question"}:
            return True, "existing_public_guide_noted"
        return True, "private_scaffold_ok"
    if stage == "ledger":
        return prompt_ledger_path().exists(), "prompt_ledger"
    if stage == "cost_tally":
        # Dry accounting only — no paid API calls.
        costs.estimated_tokens += 0
        costs.estimated_usd += 0.0
        return True, "cost_tallied"
    return False, "unknown_stage"


def run_factory(
    *,
    dry_run: bool = True,
    resume: bool = True,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    max_retries: int = MAX_STAGE_RETRIES,
    root: Path | None = None,
    status_path: Path | None = None,
    state: FactoryState | None = None,
    write_drafts: bool = False,
) -> FactoryState:
    """Execute the private draft factory. Defaults to dry-run."""
    root = root or repo_root()
    status_path = status_path or default_status_path(root)

    if state is None and resume and status_path.exists():
        prior = _load_json(status_path)
        cost_raw = prior.get("costs") or {}
        costs = CostCounters(
            items_queued=int(cost_raw.get("items_queued") or 0),
            items_processed=int(cost_raw.get("items_processed") or 0),
            stages_executed=int(cost_raw.get("stages_executed") or 0),
            retries=int(cost_raw.get("retries") or 0),
            duplicates_skipped=int(cost_raw.get("duplicates_skipped") or 0),
            estimated_tokens=int(cost_raw.get("estimated_tokens") or 0),
            estimated_usd=float(cost_raw.get("estimated_usd") or 0.0),
        )
        state = FactoryState(
            run_id=prior.get("run_id") or f"kf-m2-{utc_now()}",
            dry_run=bool(prior.get("dry_run", dry_run)),
            queue=list(prior.get("queue") or []),
            completed_keys=list(prior.get("completed_keys") or []),
            item_states=dict(prior.get("item_states") or {}),
            costs=costs,
            started_at=prior.get("started_at") or utc_now(),
            updated_at=prior.get("updated_at") or utc_now(),
            finished_at=prior.get("finished_at"),
        )
        if not state.queue:
            state = None

    if state is None:
        run_id = f"kf-m2-{'dry' if dry_run else 'live'}-{utc_now()}"
        queue = build_deterministic_queue(queue_size, root=root)
        state = FactoryState(
            run_id=run_id,
            dry_run=dry_run,
            queue=queue,
            started_at=utc_now(),
            updated_at=utc_now(),
        )
        state.costs.items_queued = len(queue)

    completed = set(state.completed_keys)
    seen_ids: set[str] = set()
    # Reconstruct seen ids from already-completed duplicate_check keys for resume.
    for key in completed:
        for item in state.queue:
            if key == idempotency_key(item["id"], "duplicate_check"):
                seen_ids.add(item["id"])

    drafts_dir = factory_root(root) / "drafts"
    if write_drafts and not dry_run:
        drafts_dir.mkdir(parents=True, exist_ok=True)

    for item in state.queue:
        item_id = item["id"]
        item_state = state.item_states.setdefault(
            item_id,
            {"id": item_id, "stages": {}, "status": "pending", "attempts": {}},
        )
        if item_state.get("status") == "done":
            continue

        failed = False
        for stage in STAGES:
            key = idempotency_key(item_id, stage)
            if key in completed:
                continue
            attempts = int(item_state["attempts"].get(stage, 0))
            ok = False
            detail = ""
            while attempts <= max_retries and not ok:
                attempts += 1
                item_state["attempts"][stage] = attempts
                if attempts > 1:
                    state.costs.retries += 1
                ok, detail = _stage_ok(item, stage, seen_ids, state.costs)
                state.costs.stages_executed += 1
                if not ok and detail != "duplicate":
                    # retry loop continues
                    continue
                break

            item_state["stages"][stage] = {
                "ok": ok,
                "detail": detail,
                "idempotency_key": key,
                "attempts": attempts,
            }
            if ok or detail == "duplicate":
                completed.add(key)
                state.completed_keys = sorted(completed)
            if detail == "duplicate":
                item_state["status"] = "duplicate_skipped"
                failed = True
                break
            if not ok:
                item_state["status"] = f"failed:{stage}"
                failed = True
                break

        if not failed and item_state.get("status") != "duplicate_skipped":
            item_state["status"] = "done"
            state.costs.items_processed += 1
            if write_drafts and not dry_run:
                scaffold = {
                    "id": item_id,
                    "title": item.get("title"),
                    "kind": item.get("kind"),
                    "visibility": "private" if not item.get("public") else "public",
                    "lifecycle": "draft" if not item.get("public") else "published",
                    "source_status": "SOURCE_INCOMPLETE" if not item.get("public") else "EDITORIAL_PUBLISHED",
                    "scripture_bodies": None,
                    "factory_run_id": state.run_id,
                    "note": "Private scaffold only — no scripture fabricated",
                }
                (drafts_dir / f"{item_id}.json").write_text(
                    json.dumps(scaffold, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

        state.updated_at = utc_now()

    state.finished_at = utc_now()
    state.updated_at = state.finished_at
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state


def get_factory_status(status_path: Path | None = None, root: Path | None = None) -> dict[str, Any]:
    """Read-only factory status for Studio."""
    path = status_path or default_status_path(root)
    if not path.exists():
        return {
            "available": False,
            "publication_authority": False,
            "message": "No factory run status yet. Execute dry-run to populate.",
            "authority": {
                "approve": False,
                "merge": False,
                "deploy": False,
                "publish": False,
            },
        }
    data = _load_json(path)
    costs = data.get("costs") or {}
    item_states = data.get("item_states") or {}
    done = sum(1 for v in item_states.values() if v.get("status") == "done")
    blockedish = sum(
        1
        for v in item_states.values()
        if str(v.get("status", "")).startswith("failed") or v.get("status") == "duplicate_skipped"
    )
    return {
        "available": True,
        "run_id": data.get("run_id"),
        "dry_run": data.get("dry_run"),
        "factory_version": data.get("factory_version"),
        "queue_size": data.get("queue_size"),
        "items_done": done,
        "items_blocked_or_duplicate": blockedish,
        "completed_keys": len(data.get("completed_keys") or []),
        "costs": costs,
        "started_at": data.get("started_at"),
        "finished_at": data.get("finished_at"),
        "prompt_ledger": data.get("prompt_ledger"),
        "publication_authority": False,
        "authority": data.get("authority")
        or {"approve": False, "merge": False, "deploy": False, "publish": False},
        "message": "Read-only factory progress. No approve/merge/deploy/publish controls.",
    }
