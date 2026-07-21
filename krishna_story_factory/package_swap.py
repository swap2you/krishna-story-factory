"""Atomic directory-level package replacement with rollback."""
from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path

from .outputs import FINAL_OUTPUT_FILES
from .paths import assert_path_under_root


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


def atomic_replace_package_dir(
    *,
    staging_dir: Path,
    production_dir: Path,
    archive_root: Path,
    output_root: Path,
    attempts: int = 8,
) -> dict:
    """Validate staging, archive current package, swap directories atomically, rollback on failure.

    Steps:
    1. Validate staging has exact eight files.
    2. Move production -> backup under archive_root.
    3. Move staging -> production.
    4. On failure after backup, restore backup to production.
    """
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

    production_existed = production_dir.exists()
    swapped = False
    try:
        if production_existed:
            _retry_rename(production_dir, backup_dir, attempts=attempts)
        parent = production_dir.parent
        parent.mkdir(parents=True, exist_ok=True)
        _retry_rename(staging_dir, production_dir, attempts=attempts)
        swapped = True
    except Exception:
        # Rollback: restore backup if production is missing/partial.
        if production_existed and backup_dir.exists() and not swapped:
            if production_dir.exists():
                shutil.rmtree(production_dir, ignore_errors=True)
            try:
                _retry_rename(backup_dir, production_dir, attempts=attempts)
            except Exception as restore_exc:  # noqa: BLE001
                raise RuntimeError(
                    f"Package swap failed and rollback restore also failed: {restore_exc}"
                ) from restore_exc
        raise

    post_errors = validate_exact_eight_files(production_dir)
    if post_errors:
        # Attempt restore from backup.
        if backup_dir.exists():
            if production_dir.exists():
                failed = production_dir.with_name(production_dir.name + f".failed_{stamp}")
                if failed.exists():
                    shutil.rmtree(failed, ignore_errors=True)
                _retry_rename(production_dir, failed, attempts=attempts)
            _retry_rename(backup_dir, production_dir, attempts=attempts)
        raise RuntimeError("Post-swap validation failed; restored backup: " + " | ".join(post_errors))

    return {
        "status": "REPLACED",
        "production_dir": str(production_dir),
        "backup_dir": str(backup_dir) if backup_dir.exists() else "",
        "before_hashes": before_hashes,
        "after_hashes": after_hashes,
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
    "atomic_replace_package_dir",
    "sha256_file",
    "validate_exact_eight_files",
]
