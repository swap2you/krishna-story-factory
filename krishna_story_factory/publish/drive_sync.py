from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from ..config import Settings
from ..models import PackagePaths, PlanRow


@dataclass(frozen=True, slots=True)
class PackagePublishResult:
    publish_mode: str
    package_link: str
    local_sync_path: str = ""


def resolve_package_link(settings: Settings) -> str:
    if settings.package_public_link:
        return settings.package_public_link.strip()
    if settings.google_drive_folder_url:
        return settings.google_drive_folder_url.strip()
    return ""


def publish_package(
    settings: Settings,
    plan: PlanRow,
    paths: PackagePaths,
) -> PackagePublishResult:
    package_link = resolve_package_link(settings)
    sync_root = settings.google_drive_local_sync_root

    if sync_root:
        dest = sync_root / f"{plan.chapter_no}_{plan.slug}"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(paths.root, dest)
        return PackagePublishResult(
            publish_mode="local_drive_sync",
            package_link=package_link,
            local_sync_path=str(dest),
        )

    mode = settings.package_publish_mode or "local"
    return PackagePublishResult(publish_mode=mode, package_link=package_link)
