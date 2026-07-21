"""Atomic directory-level package replacement with rollback and crash journal."""
from __future__ import annotations

import hashlib
import json
import logging
import shutil
import time
import uuid
from pathlib import Path

from .outputs import FINAL_OUTPUT_FILES
from .paths import assert_path_under_root

logger = logging.getLogger(__name__)

JOURNAL_DIRNAME = "_swap_journal"
JOURNAL_QUARANTINE = "_swap_journal_invalid"
PHASE_PREPARED = "PREPARED"
PHASE_PRODUCTION_BACKED_UP = "PRODUCTION_BACKED_UP"
PHASE_STAGING_PROMOTED = "STAGING_PROMOTED"
PHASE_VALIDATED = "VALIDATED"
PHASE_COMMITTED = "COMMITTED"
STATUS_INVALID_SWAP_JOURNAL = "INVALID_SWAP_JOURNAL"

_REQUIRED_JOURNAL_FIELDS = (
    "transaction_id",
    "production_path",
    "staging_path",
    "backup_path",
    "phase",
)
_VALID_PHASES = {
    PHASE_PREPARED,
    PHASE_PRODUCTION_BACKED_UP,
    PHASE_STAGING_PROMOTED,
    PHASE_VALIDATED,
    PHASE_COMMITTED,
}


class InvalidSwapJournalError(ValueError):
    """Raised when a swap journal fails path/schema validation."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate_exact_eight_files(package_dir: Path) -> list[str]:
    errors: list[str] = []
    if not package_dir.exists():
        return [f"Package directory missing: {package_dir}"]
    names = {p.name for p in package_dir.iterdir() if p.is_file()}
    if names != set(FINAL_OUTPUT_FILES):
        errors.append(f"Exact eight-file contract failed: found {sorted(names)}")
    for name in FINAL_OUTPUT_FILES:
        path = package_dir / name
        if not path.exists() or path.stat().st_size <= 0:
            errors.append(f"Missing or empty final file: {name}")
    return errors


def journal_root(output_root: Path) -> Path:
    root = output_root / JOURNAL_DIRNAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def quarantine_root(output_root: Path) -> Path:
    root = output_root / JOURNAL_QUARANTINE
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sanitize_path_for_log(path: Path | str) -> str:
    text = str(path or "")
    if len(text) > 180:
        return text[:177] + "..."
    return text


def _write_journal(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _quarantine_journal(journal_path: Path, output_root: Path, reason: str) -> Path:
    """Move invalid journal aside for diagnosis; never delete evidence."""
    dest_dir = quarantine_root(output_root)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = dest_dir / f"{journal_path.stem}_{stamp}{journal_path.suffix}"
    if dest.exists():
        dest = dest_dir / f"{journal_path.stem}_{stamp}_{uuid.uuid4().hex[:6]}{journal_path.suffix}"
    note = dest.with_suffix(dest.suffix + ".reason.txt")
    note.write_text(reason[:2000], encoding="utf-8")
    if journal_path.exists():
        journal_path.replace(dest)
    return dest


def parse_and_validate_journal(
    data: dict,
    *,
    output_root: Path,
    project_root: Path | None = None,
) -> dict[str, Path | str]:
    """Validate untrusted journal JSON and return resolved operational paths.

    Raises InvalidSwapJournalError without performing any filesystem mutation.
    """
    if not isinstance(data, dict):
        raise InvalidSwapJournalError("journal payload must be an object")

    missing = [key for key in _REQUIRED_JOURNAL_FIELDS if key not in data]
    if missing:
        raise InvalidSwapJournalError(f"missing required fields: {', '.join(missing)}")

    for key in _REQUIRED_JOURNAL_FIELDS:
        value = data.get(key)
        if value is None:
            raise InvalidSwapJournalError(f"{key} is null")
        if not isinstance(value, str):
            raise InvalidSwapJournalError(f"{key} must be a string")
        if not value.strip():
            raise InvalidSwapJournalError(f"{key} is empty")

    phase = data["phase"].strip()
    if phase not in _VALID_PHASES:
        raise InvalidSwapJournalError(f"unsupported phase: {phase!r}")

    output_root = Path(output_root).resolve()
    cwd = Path.cwd().resolve()
    repo = Path(project_root).resolve() if project_root else None

    def _resolve_field(field: str) -> Path:
        raw = data[field].strip()
        # Reject empty after strip and bare relative empties that become cwd.
        if raw in {"", ".", "./", "..", "../", "..."}:
            raise InvalidSwapJournalError(f"{field} resolves to an unsafe empty/cwd path")
        candidate = Path(raw)
        # Journal paths must be absolute and deterministic — never resolve relative to cwd.
        if not candidate.is_absolute():
            raise InvalidSwapJournalError(f"{field} must be an absolute path")
        # Disallow parent traversal segments before resolve.
        if ".." in candidate.parts:
            raise InvalidSwapJournalError(f"{field} contains parent traversal")
        try:
            resolved = assert_path_under_root(candidate, output_root, label=field)
        except ValueError as exc:
            raise InvalidSwapJournalError(str(exc)) from exc
        if resolved == output_root:
            raise InvalidSwapJournalError(f"{field} must not equal output_root")
        if resolved == cwd:
            raise InvalidSwapJournalError(f"{field} must not equal current working directory")
        if repo is not None and resolved == repo:
            raise InvalidSwapJournalError(f"{field} must not equal repository root")
        return resolved

    production = _resolve_field("production_path")
    staging = _resolve_field("staging_path")
    backup = _resolve_field("backup_path")

    if len({production, staging, backup}) < 3:
        raise InvalidSwapJournalError("production, staging, and backup paths must be distinct")

    staging_root = (output_root / "_staging").resolve()
    archive_root = (output_root / "_archive").resolve()
    journal_dir = (output_root / JOURNAL_DIRNAME).resolve()
    quarantine_dir = (output_root / JOURNAL_QUARANTINE).resolve()

    if staging == staging_root or not staging.is_relative_to(staging_root):
        raise InvalidSwapJournalError("staging_path must be under output/_staging/")
    if backup == archive_root or not backup.is_relative_to(archive_root):
        raise InvalidSwapJournalError("backup_path must be under output/_archive/")
    # Production package: direct child of output_root (output/<chapter_slug>), not a system folder.
    if production.parent.resolve() != output_root:
        raise InvalidSwapJournalError("production_path must be a package folder directly under output_root")
    for forbidden in (staging_root, archive_root, journal_dir, quarantine_dir):
        if production == forbidden or production.is_relative_to(forbidden):
            raise InvalidSwapJournalError("production_path must not live under system output folders")
    if production.name.startswith("_"):
        raise InvalidSwapJournalError("production_path must be a package directory, not a system folder")

    return {
        "transaction_id": data["transaction_id"].strip(),
        "phase": phase,
        "production": production,
        "staging": staging,
        "backup": backup,
    }


def recover_unfinished_swaps(*, output_root: Path, project_root: Path | None = None) -> list[dict]:
    """Detect unfinished journals and deterministically finish or restore.

    Invalid journals are quarantined (not deleted) and reported as INVALID_SWAP_JOURNAL.
    No rename/delete of package paths occurs for invalid journals.
    """
    root = journal_root(output_root)
    recovered: list[dict] = []
    blocking_invalid = False
    for path in sorted(root.glob("swap_*.json")):
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            reason = f"malformed journal JSON: {type(exc).__name__}"
            quarantined = _quarantine_journal(path, output_root, reason)
            recovered.append(
                {
                    "journal": _sanitize_path_for_log(path),
                    "status": STATUS_INVALID_SWAP_JOURNAL,
                    "action": "quarantine_malformed",
                    "quarantine": _sanitize_path_for_log(quarantined),
                    "detail": reason,
                }
            )
            blocking_invalid = True
            continue

        try:
            validated = parse_and_validate_journal(data, output_root=output_root, project_root=project_root)
        except InvalidSwapJournalError as exc:
            reason = str(exc)
            quarantined = _quarantine_journal(path, output_root, reason)
            logger.warning(
                "Invalid swap journal quarantined (%s): %s",
                _sanitize_path_for_log(path),
                reason,
            )
            recovered.append(
                {
                    "journal": _sanitize_path_for_log(path),
                    "status": STATUS_INVALID_SWAP_JOURNAL,
                    "action": "quarantine_invalid",
                    "quarantine": _sanitize_path_for_log(quarantined),
                    "detail": reason,
                }
            )
            blocking_invalid = True
            continue

        phase = str(validated["phase"])
        production = Path(validated["production"])  # type: ignore[arg-type]
        staging = Path(validated["staging"])  # type: ignore[arg-type]
        backup = Path(validated["backup"])  # type: ignore[arg-type]
        action = "noop"
        if phase == PHASE_COMMITTED:
            path.unlink(missing_ok=True)
            action = "discard_committed"
        elif phase == PHASE_PREPARED:
            # Nothing mutated yet.
            path.unlink(missing_ok=True)
            action = "discard_prepared"
        elif phase == PHASE_PRODUCTION_BACKED_UP:
            # Production moved to backup; staging not promoted. Restore backup.
            if backup.exists() and not production.exists():
                _retry_rename(backup, production)
            path.unlink(missing_ok=True)
            action = "restore_backup"
        elif phase in {PHASE_STAGING_PROMOTED, PHASE_VALIDATED}:
            if production.exists() and not validate_exact_eight_files(production):
                data["phase"] = PHASE_COMMITTED
                _write_journal(path, data)
                path.unlink(missing_ok=True)
                action = "commit_promoted"
            elif backup.exists():
                if production.exists():
                    failed = production.with_name(production.name + f".failed_recovery_{int(time.time())}")
                    if failed.exists():
                        shutil.rmtree(failed, ignore_errors=True)
                    _retry_rename(production, failed)
                _retry_rename(backup, production)
                path.unlink(missing_ok=True)
                action = "restore_after_bad_promote"
            else:
                path.unlink(missing_ok=True)
                action = "discard_orphaned"
        else:
            path.unlink(missing_ok=True)
            action = "discard_unknown"
        recovered.append(
            {
                "journal": _sanitize_path_for_log(path),
                "phase": phase,
                "action": action,
                "staging": _sanitize_path_for_log(staging),
                "status": "OK",
            }
        )

    if blocking_invalid:
        # Signal callers that operator action is required before a new rebuild.
        recovered.append(
            {
                "status": STATUS_INVALID_SWAP_JOURNAL,
                "action": "block_new_rebuild",
                "detail": "One or more invalid swap journals were quarantined; clear or repair before rebuilding.",
            }
        )
    return recovered


def atomic_replace_package_dir(
    *,
    staging_dir: Path,
    production_dir: Path,
    archive_root: Path,
    output_root: Path,
    attempts: int = 8,
    project_root: Path | None = None,
) -> dict:
    """Validate staging, archive current package, swap directories atomically, rollback on failure.

    Uses a journal outside the production directory so crash recovery can finish or restore.
    """
    recovery = recover_unfinished_swaps(output_root=output_root, project_root=project_root)
    if any(item.get("status") == STATUS_INVALID_SWAP_JOURNAL for item in recovery):
        raise RuntimeError(
            f"{STATUS_INVALID_SWAP_JOURNAL}: clear or repair quarantined journals under "
            f"{JOURNAL_QUARANTINE} before starting a new package swap."
        )

    staging_dir = assert_path_under_root(staging_dir, output_root, label="staging package")
    production_dir = assert_path_under_root(production_dir, output_root, label="production package")
    archive_root = assert_path_under_root(archive_root, output_root, label="archive root")
    archive_root.mkdir(parents=True, exist_ok=True)

    errors = validate_exact_eight_files(staging_dir)
    if errors:
        raise RuntimeError("Staging package invalid before swap: " + " | ".join(errors))

    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = archive_root / f"{production_dir.name}_pre_swap_{stamp}"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    before_hashes = {
        name: (sha256_file(production_dir / name) if (production_dir / name).exists() else "")
        for name in FINAL_OUTPUT_FILES
    }
    after_hashes = {name: sha256_file(staging_dir / name) for name in FINAL_OUTPUT_FILES}

    tx_id = f"{stamp}_{uuid.uuid4().hex[:8]}"
    journal_path = journal_root(output_root) / f"swap_{tx_id}.json"
    journal = {
        "transaction_id": tx_id,
        "production_path": str(production_dir.resolve()),
        "staging_path": str(staging_dir.resolve()),
        "backup_path": str(backup_dir.resolve()),
        "phase": PHASE_PREPARED,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "expected_hashes": after_hashes,
        "before_hashes": before_hashes,
    }
    _write_journal(journal_path, journal)

    production_existed = production_dir.exists()
    swapped = False
    try:
        if production_existed:
            _retry_rename(production_dir, backup_dir, attempts=attempts)
            journal["phase"] = PHASE_PRODUCTION_BACKED_UP
            _write_journal(journal_path, journal)
        parent = production_dir.parent
        parent.mkdir(parents=True, exist_ok=True)
        _retry_rename(staging_dir, production_dir, attempts=attempts)
        swapped = True
        journal["phase"] = PHASE_STAGING_PROMOTED
        _write_journal(journal_path, journal)
    except Exception:
        if production_existed and backup_dir.exists() and not swapped:
            if production_dir.exists():
                shutil.rmtree(production_dir, ignore_errors=True)
            try:
                _retry_rename(backup_dir, production_dir, attempts=attempts)
            except Exception as restore_exc:  # noqa: BLE001
                raise RuntimeError(
                    f"Package swap failed and rollback restore also failed: {restore_exc}"
                ) from restore_exc
        journal_path.unlink(missing_ok=True)
        raise

    post_errors = validate_exact_eight_files(production_dir)
    if post_errors:
        if backup_dir.exists():
            if production_dir.exists():
                failed = production_dir.with_name(production_dir.name + f".failed_{stamp}")
                if failed.exists():
                    shutil.rmtree(failed, ignore_errors=True)
                _retry_rename(production_dir, failed, attempts=attempts)
            _retry_rename(backup_dir, production_dir, attempts=attempts)
        journal_path.unlink(missing_ok=True)
        raise RuntimeError("Post-swap validation failed; restored backup: " + " | ".join(post_errors))

    journal["phase"] = PHASE_VALIDATED
    _write_journal(journal_path, journal)
    journal["phase"] = PHASE_COMMITTED
    _write_journal(journal_path, journal)
    journal_path.unlink(missing_ok=True)

    return {
        "status": "REPLACED",
        "production_dir": str(production_dir),
        "backup_dir": str(backup_dir) if backup_dir.exists() else "",
        "before_hashes": before_hashes,
        "after_hashes": after_hashes,
        "transaction_id": tx_id,
    }


def _retry_rename(src: Path, dest: Path, *, attempts: int = 8) -> None:
    last_exc: OSError | None = None
    for attempt in range(max(1, attempts)):
        try:
            src.rename(dest)
            return
        except OSError as exc:
            last_exc = exc
            if attempt + 1 >= attempts:
                break
            time.sleep(min(2.0, 0.05 * (2**attempt)))
    raise OSError(f"Directory rename failed after {attempts} attempts: {src} -> {dest}") from last_exc


__all__ = [
    "InvalidSwapJournalError",
    "PHASE_COMMITTED",
    "PHASE_PREPARED",
    "PHASE_PRODUCTION_BACKED_UP",
    "PHASE_STAGING_PROMOTED",
    "PHASE_VALIDATED",
    "STATUS_INVALID_SWAP_JOURNAL",
    "atomic_replace_package_dir",
    "journal_root",
    "parse_and_validate_journal",
    "quarantine_root",
    "recover_unfinished_swaps",
    "sha256_file",
    "validate_exact_eight_files",
]
