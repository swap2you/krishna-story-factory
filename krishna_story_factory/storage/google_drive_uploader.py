from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
import json
import re

from ..config import Settings
from ..outputs import FINAL_OUTPUT_FILES

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@dataclass(frozen=True, slots=True)
class DriveUploadResult:
    status: str
    publish_mode: str
    package_link: str
    folder_id: str = ""
    local_sync_path: str = ""
    detail: str = ""
    folder_name: str = ""
    uploaded_files: tuple[str, ...] = field(default_factory=tuple)
    remote_files: tuple[dict, ...] = field(default_factory=tuple)


def upload_final_package(settings: Settings, *, folder_name: str, source_dir: Path) -> DriveUploadResult:
    missing = [name for name in FINAL_OUTPUT_FILES if not (source_dir / name).exists()]
    if missing:
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=settings.google_drive_folder_url,
            detail=f"Missing final files before upload: {missing}",
            folder_name=folder_name,
        )
    if settings.google_drive_upload_enabled:
        return _upload_via_api(settings, folder_name=folder_name, source_dir=source_dir, files=FINAL_OUTPUT_FILES)
    if settings.google_drive_local_sync_root:
        return _upload_via_local_sync(settings, folder_name=folder_name, source_dir=source_dir, files=FINAL_OUTPUT_FILES)
    link = settings.package_public_link or settings.google_drive_folder_url
    return DriveUploadResult(
        status="DISABLED",
        publish_mode="link_only",
        package_link=link,
        detail="Drive upload disabled.",
        folder_name=folder_name,
    )


def _upload_via_local_sync(settings: Settings, *, folder_name: str, source_dir: Path, files: tuple[str, ...]) -> DriveUploadResult:
    import shutil

    dest = settings.google_drive_local_sync_root / folder_name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    uploaded: list[str] = []
    for name in files:
        src = source_dir / name
        if src.exists():
            shutil.copy2(src, dest / name)
            uploaded.append(name)
    link = settings.package_public_link or settings.google_drive_folder_url
    return DriveUploadResult(
        status="LOCAL_SYNC",
        publish_mode="local_drive_sync",
        package_link=link,
        local_sync_path=str(dest),
        detail=f"Copied {len(uploaded)} final file(s).",
        folder_name=folder_name,
        uploaded_files=tuple(uploaded),
    )


def _upload_via_api(settings: Settings, *, folder_name: str, source_dir: Path, files: tuple[str, ...]) -> DriveUploadResult:
    creds_file = settings.google_drive_credentials_file
    token_file = settings.google_drive_token_file
    parent_id = settings.google_drive_folder_id
    if not creds_file or not creds_file.exists():
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=settings.google_drive_folder_url,
            detail="GOOGLE_DRIVE_CREDENTIALS_FILE missing.",
            folder_name=folder_name,
        )
    if not token_file:
        token_file = settings.project_root / "credentials" / "google_drive_token.json"
    if not parent_id:
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=settings.google_drive_folder_url,
            detail="GOOGLE_DRIVE_FOLDER_ID missing.",
            folder_name=folder_name,
        )
    try:
        service = _build_drive_service(creds_file, token_file)
        child_folder_id = _ensure_child_folder(service, parent_id, folder_name)
        uploaded: list[str] = []
        for filename in files:
            path = source_dir / filename
            _upload_file(service, child_folder_id, path)
            uploaded.append(filename)
        link = f"https://drive.google.com/drive/folders/{child_folder_id}?usp=sharing"
        return DriveUploadResult(
            status="UPLOADED",
            publish_mode="drive_api",
            package_link=link,
            folder_id=child_folder_id,
            detail=f"Uploaded {len(uploaded)} final file(s).",
            folder_name=folder_name,
            uploaded_files=tuple(uploaded),
        )
    except Exception as exc:
        logger.warning("Google Drive upload failed: %s", type(exc).__name__)
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=settings.google_drive_folder_url,
            detail=f"Drive upload failed: {type(exc).__name__}: {exc}",
            folder_name=folder_name,
        )


def _build_drive_service(creds_file: Path, token_file: Path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _ensure_child_folder(service, parent_id: str, folder_name: str) -> str:
    query = (
        f"mimeType='application/vnd.google-apps.folder' and "
        f"name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    )
    result = service.files().list(q=query, fields="files(id,name)", pageSize=1).execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    created = service.files().create(body=metadata, fields="id").execute()
    return created["id"]


def _upload_file(service, folder_id: str, path: Path) -> None:
    from googleapiclient.http import MediaFileUpload

    mime = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".json": "application/json",
        ".mp3": "audio/mpeg",
    }.get(path.suffix.lower(), "application/octet-stream")
    query = f"name='{path.name}' and '{folder_id}' in parents and trashed=false"
    existing = service.files().list(q=query, fields="files(id)", pageSize=1).execute().get("files", [])
    media = MediaFileUpload(str(path), mimetype=mime, resumable=True)
    if existing:
        service.files().update(fileId=existing[0]["id"], media_body=media).execute()
    else:
        metadata = {"name": path.name, "parents": [folder_id]}
        service.files().create(body=metadata, media_body=media, fields="id").execute()


upload_story_package = upload_final_package


def replace_component_files(settings: Settings, *, source_dir: Path, manifest_path: Path) -> DriveUploadResult:
    filenames = ("activity_sheet.pdf", "coloring_page.png", "manifest.json")
    missing = [name for name in filenames if not (source_dir / name).exists()]
    if missing:
        return DriveUploadResult(status="FAILED", publish_mode="component_replace", package_link="", detail=f"Missing component files: {missing}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    link = str(data.get("package", {}).get("package_link", ""))
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", link)
    folder_id = match.group(1) if match else str(data.get("package", {}).get("drive_folder_id", ""))
    if settings.google_drive_local_sync_root:
        import shutil
        dest = settings.google_drive_local_sync_root / source_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        for name in filenames[:2]:
            shutil.copy2(source_dir / name, dest / name)
        count = len([p for p in dest.iterdir() if p.is_file()])
        status = "LOCAL_SYNC" if count == 7 else "FAILED"
        detail = f"Replaced 3 component files; folder contains {count} files."
        _set_manifest_drive_result(manifest_path, status, detail)
        shutil.copy2(manifest_path, dest / "manifest.json")
        return DriveUploadResult(status=status, publish_mode="component_replace", package_link=link, folder_id=folder_id,
            detail=detail, uploaded_files=filenames)
    if not settings.google_drive_upload_enabled:
        return DriveUploadResult(status="SKIPPED", publish_mode="component_replace", package_link=link, folder_id=folder_id,
            detail="Upload disabled by flag.")
    if not folder_id:
        return DriveUploadResult(status="FAILED", publish_mode="component_replace", package_link=link, detail="Existing Drive folder ID missing from manifest package link.")
    try:
        token = settings.google_drive_token_file or settings.project_root / "credentials" / "google_drive_token.json"
        service = _build_drive_service(settings.google_drive_credentials_file, token)
        query = f"'{folder_id}' in parents and trashed=false"
        preflight = service.files().list(
            q=query, fields="files(id,name,modifiedTime)", pageSize=100,
        ).execute().get("files", [])
        preflight_names = {item.get("name", "") for item in preflight}
        if len(preflight) != 7 or preflight_names != set(FINAL_OUTPUT_FILES):
            return DriveUploadResult(
                status="FAILED", publish_mode="component_replace", package_link=link, folder_id=folder_id,
                detail=f"Drive preflight refused replacement: expected exact seven final files, found {sorted(preflight_names)}.",
                remote_files=tuple(preflight),
            )
        for name in filenames[:2]:
            _upload_file(service, folder_id, source_dir / name)
        interim = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
        status = "UPLOADED" if len(interim) == 7 and {item.get("name", "") for item in interim} == set(FINAL_OUTPUT_FILES) else "FAILED"
        detail = f"Replaced 3 component files; Drive folder contains {len(interim)} exact final files."
        _set_manifest_drive_result(manifest_path, status, detail)
        _upload_file(service, folder_id, manifest_path)
        final_files = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
        final_ok = len(final_files) == 7 and {item.get("name", "") for item in final_files} == set(FINAL_OUTPUT_FILES)
        if not final_ok:
            status = "FAILED"
            detail = f"Drive post-replacement verification failed: found {[item.get('name', '') for item in final_files]}."
            _set_manifest_drive_result(manifest_path, status, detail)
            _upload_file(service, folder_id, manifest_path)
        return DriveUploadResult(status=status, publish_mode="component_replace", package_link=link, folder_id=folder_id,
            detail=detail, uploaded_files=filenames, remote_files=tuple(final_files))
    except Exception as exc:
        return DriveUploadResult(status="FAILED", publish_mode="component_replace", package_link=link, folder_id=folder_id,
            detail=f"Drive component replacement failed: {type(exc).__name__}: {exc}")


def _set_manifest_drive_result(path: Path, status: str, detail: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    package = data.setdefault("package", {})
    package["drive_status"] = status
    package["drive_detail"] = detail
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

__all__ = ["DriveUploadResult", "upload_final_package", "upload_story_package", "replace_component_files"]
