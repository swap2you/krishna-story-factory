from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from ..models import PackagePaths, PlanRow
from ..storage.google_drive_uploader import DriveUploadResult, upload_story_package


@dataclass(frozen=True, slots=True)
class PackagePublishResult:
    publish_mode: str
    package_link: str
    local_sync_path: str = ""
    drive_status: str = ""
    drive_detail: str = ""
    drive_folder_id: str = ""


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
    folder_name = f"{plan.chapter_no}_{plan.slug}"
    drive_result: DriveUploadResult = upload_story_package(
        settings,
        folder_name=folder_name,
        source_dir=paths.root,
    )
    return PackagePublishResult(
        publish_mode=drive_result.publish_mode,
        package_link=drive_result.package_link,
        local_sync_path=drive_result.local_sync_path,
        drive_status=drive_result.status,
        drive_detail=drive_result.detail,
        drive_folder_id=drive_result.folder_id,
    )
