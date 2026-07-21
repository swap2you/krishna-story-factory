"""Atomic directory-level package replacement with rollback and crash journal."""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import uuid
from pathlib import Path

from .outputs import FINAL_OUTPUT_FILES
from .paths import assert_path_under_root

JOURNAL_DIRNAME = "_swap_journal"
PHASE_PREPARED = "PREPARED"
PHASE_PRODUCTION_BACKED_UP = "PRODUCTION_BACKED_UP"
PHASE_STAGING_PROMOTED = "STAGING_PROMOTED"
PHASE_VALIDATED = "VALIDATED"
PHASE_COMMITTED = "COMMITTED"


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


def _write_journal(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def recover_unfinished_swaps(*, output_root: Path) -> list[dict]:
    """Detect unfinished journals and deterministically finish or restore."""
    root = journal_root(output_root)
    recovered: list[dict] = []
    for path in sorted(root.glob("swap_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            path.unlink(missing_ok=True)
            continue
        phase = str(data.get("phase") or "")
        production = Path(str(data.get("production_path") or ""))
        staging = Path(str(data.get("staging_path") or ""))
        backup = Path(str(data.get("backup_path") or ""))
        action = "noop"
        if phase in {PHASE_COMMITTED, ""}:
            path.unlink(missing_ok=True)
            action = "discard_committed_or_empty"
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
            # Staging already at production path (or should be). Validate or restore.
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
        recovered.append({"journal": str(path), "phase": phase, "action": action, "staging": str(staging)})
    return recovered


def atomic_replace_package_dir(
    *,
    staging_dir: Path,
    production_dir: Path,
    archive_root: Path,
    output_root: Path,
    attempts: int = 8,
) -> dict:
    """Validate staging, archive current package, swap directories atomically, rollback on failure.

    Uses a journal outside the production directory so crash recovery can finish or restore.
    """
    # Never start a new swap while an unfinished journal exists.
    recover_unfinished_swaps(output_root=output_root)

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
        "production_path": str(production_dir),
        "staging_path": str(staging_dir),
        "backup_path": str(backup_dir),
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
    "PHASE_COMMITTED",
    "PHASE_PREPARED",
    "PHASE_PRODUCTION_BACKED_UP",
    "PHASE_STAGING_PROMOTED",
    "PHASE_VALIDATED",
    "atomic_replace_package_dir",
    "journal_root",
    "recover_unfinished_swaps",
    "sha256_file",
    "validate_exact_eight_files",
]
