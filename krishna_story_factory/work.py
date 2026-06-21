from __future__ import annotations

import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class WorkPaths:
    root: Path
    run_id: str
    poster_candidates: Path
    coloring_candidates: Path
    reviews: Path


def new_work_paths(project_root: Path, *, debug: bool = False) -> WorkPaths:
    run_id = uuid.uuid4().hex[:12]
    root = project_root / ".work" / run_id
    paths = WorkPaths(
        root=root,
        run_id=run_id,
        poster_candidates=root / "poster_candidates",
        coloring_candidates=root / "coloring_candidates",
        reviews=root / "reviews",
    )
    for p in (paths.poster_candidates, paths.coloring_candidates, paths.reviews):
        p.mkdir(parents=True, exist_ok=True)
    return paths


def cleanup_work(work: WorkPaths, *, keep: bool = False) -> None:
    if keep or not work.root.exists():
        return
    shutil.rmtree(work.root, ignore_errors=True)


def prune_output_folder(output_dir: Path) -> None:
    allowed = set(FINAL_OUTPUT_FILES)
    if not output_dir.exists():
        return
    for item in output_dir.iterdir():
        if item.name not in allowed:
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)


from .outputs import FINAL_OUTPUT_FILES  # noqa: E402
