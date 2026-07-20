from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
import json
import re

from ..config import Settings
from ..outputs import FINAL_OUTPUT_FILES

EXPECTED_FINAL_COUNT = len(FINAL_OUTPUT_FILES)

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
        folder = ensure_story_folder(settings, folder_name=folder_name)
        if folder.status != "READY":
            return DriveUploadResult(
                status="FAILED",
                publish_mode="drive_api",
                package_link=folder.package_link or settings.google_drive_folder_url,
                folder_id=folder.folder_id,
                detail=folder.detail or "Failed to ensure story folder.",
                folder_name=folder_name,
            )
        uploaded = upload_files_to_folder(
            settings,
            folder_id=folder.folder_id,
            package_link=folder.package_link,
            source_dir=source_dir,
            files=FINAL_OUTPUT_FILES,
            folder_name=folder_name,
        )
        if uploaded.status != "UPLOADED":
            return uploaded
        ok, detail = verify_drive_text_links(
            settings, folder_id=folder.folder_id, package_link=folder.package_link
        )
        if not ok:
            return DriveUploadResult(
                status="FAILED",
                publish_mode="drive_api",
                package_link=folder.package_link,
                folder_id=folder.folder_id,
                detail=detail,
                folder_name=folder_name,
                uploaded_files=uploaded.uploaded_files,
            )
        return DriveUploadResult(
            status="UPLOADED",
            publish_mode="drive_api",
            package_link=folder.package_link,
            folder_id=folder.folder_id,
            detail=f"Uploaded and verified {len(uploaded.uploaded_files)} final file(s).",
            folder_name=folder_name,
            uploaded_files=uploaded.uploaded_files,
        )
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


def ensure_story_folder(settings: Settings, *, folder_name: str) -> DriveUploadResult:
    """Create or reuse the per-story Drive child folder without uploading files."""
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
        link = f"https://drive.google.com/drive/folders/{child_folder_id}?usp=sharing"
        return DriveUploadResult(
            status="READY",
            publish_mode="drive_api",
            package_link=link,
            folder_id=child_folder_id,
            detail="Story folder ready.",
            folder_name=folder_name,
        )
    except Exception as exc:
        logger.warning("Google Drive ensure folder failed: %s", type(exc).__name__)
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=settings.google_drive_folder_url,
            detail=f"Drive folder ensure failed: {type(exc).__name__}: {exc}",
            folder_name=folder_name,
        )


def upload_files_to_folder(
    settings: Settings,
    *,
    folder_id: str,
    package_link: str,
    source_dir: Path,
    files: tuple[str, ...] = FINAL_OUTPUT_FILES,
    folder_name: str = "",
    prune_extras: bool = False,
) -> DriveUploadResult:
    """Upload/replace selected files into an existing Drive folder."""
    names = tuple(dict.fromkeys(files))
    missing = [name for name in names if not (source_dir / name).exists()]
    if missing:
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=package_link,
            folder_id=folder_id,
            detail=f"Missing files before upload: {missing}",
            folder_name=folder_name,
        )
    try:
        token = settings.google_drive_token_file or settings.project_root / "credentials" / "google_drive_token.json"
        service = _build_drive_service(settings.google_drive_credentials_file, token)
        uploaded: list[str] = []
        for filename in names:
            _upload_file(service, folder_id, source_dir / filename)
            uploaded.append(filename)
        if prune_extras or set(names) == set(FINAL_OUTPUT_FILES):
            _prune_non_final_files(service, folder_id)
        return DriveUploadResult(
            status="UPLOADED",
            publish_mode="drive_api",
            package_link=package_link,
            folder_id=folder_id,
            detail=f"Uploaded {len(uploaded)} file(s).",
            folder_name=folder_name,
            uploaded_files=tuple(uploaded),
        )
    except Exception as exc:
        logger.warning("Google Drive file upload failed: %s", type(exc).__name__)
        return DriveUploadResult(
            status="FAILED",
            publish_mode="drive_api",
            package_link=package_link,
            folder_id=folder_id,
            detail=f"Drive upload failed: {type(exc).__name__}: {exc}",
            folder_name=folder_name,
        )


def verify_drive_text_links(
    settings: Settings, *, folder_id: str, package_link: str
) -> tuple[bool, str]:
    """Read back manifest.json and whatsapp_caption.txt; require folder link and non-PENDING status."""
    try:
        token = settings.google_drive_token_file or settings.project_root / "credentials" / "google_drive_token.json"
        service = _build_drive_service(settings.google_drive_credentials_file, token)
        manifest_text = _download_drive_text(service, folder_id, "manifest.json")
        caption_text = _download_drive_text(service, folder_id, "whatsapp_caption.txt")
    except Exception as exc:
        return False, f"Drive read-back failed: {type(exc).__name__}: {exc}"

    if not manifest_text.strip():
        return False, "Remote manifest.json is empty."
    if not caption_text.strip():
        return False, "Remote whatsapp_caption.txt is empty."

    link_stem = package_link.split("?")[0]
    manifest_normalized = manifest_text.replace("\\/", "/")
    if folder_id not in manifest_normalized and link_stem not in manifest_normalized:
        return False, "Remote manifest.json does not contain the story folder link/id."
    if folder_id not in caption_text and link_stem not in caption_text:
        return False, "Remote whatsapp_caption.txt does not contain the story package link."

    try:
        data = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return False, f"Remote manifest.json is not valid JSON: {exc}"
    drive_status = str(data.get("package", {}).get("drive_status", "")).upper()
    if drive_status in {"", "PENDING"}:
        return False, f"Remote manifest drive_status is {drive_status or 'missing'} (must not be PENDING)."
    package_remote = str(data.get("package", {}).get("package_link", ""))
    if folder_id not in package_remote and link_stem not in package_remote.replace("\\/", "/"):
        return False, "Remote manifest package_link does not point at the story folder."
    return True, "Remote manifest and caption verified."


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


def _download_drive_text(service, folder_id: str, filename: str) -> str:
    from googleapiclient.http import MediaIoBaseDownload
    import io

    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    files = service.files().list(q=query, fields="files(id,name)", pageSize=1).execute().get("files", [])
    if not files:
        raise FileNotFoundError(f"{filename} not found in Drive folder {folder_id}")
    request = service.files().get_media(fileId=files[0]["id"])
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue().decode("utf-8", errors="replace")


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
    filenames = ("activity_sheet.pdf", "coloring_page.png", "simple_coloring_page.png", "manifest.json")
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
        for name in filenames[:-1]:
            shutil.copy2(source_dir / name, dest / name)
        count = len([p for p in dest.iterdir() if p.is_file()])
        status = "LOCAL_SYNC" if count == len(FINAL_OUTPUT_FILES) else "FAILED"
        detail = f"Replaced {len(filenames) - 1} component files; folder contains {count} files."
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
        # Allow migration from legacy 7-file packages by syncing exact finals.
        for name in filenames:
            if name != "manifest.json":
                _upload_file(service, folder_id, source_dir / name)
        _prune_non_final_files(service, folder_id)
        preflight = service.files().list(
            q=query, fields="files(id,name,modifiedTime)", pageSize=100,
        ).execute().get("files", [])
        preflight_names = {item.get("name", "") for item in preflight}
        if len(preflight) != len(FINAL_OUTPUT_FILES) or preflight_names != set(FINAL_OUTPUT_FILES):
            # Upload remaining finals from source if present, then prune again.
            for name in FINAL_OUTPUT_FILES:
                path = source_dir / name
                if path.exists() and name != "manifest.json":
                    _upload_file(service, folder_id, path)
            _prune_non_final_files(service, folder_id)
            interim = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
            if {item.get("name", "") for item in interim} != set(FINAL_OUTPUT_FILES):
                return DriveUploadResult(
                    status="FAILED", publish_mode="component_replace", package_link=link, folder_id=folder_id,
                    detail=f"Drive exact-final sync failed: found {sorted(item.get('name', '') for item in interim)}.",
                    remote_files=tuple(interim),
                )
        detail = f"Replaced {len(filenames)} component files; Drive folder contains {len(FINAL_OUTPUT_FILES)} exact final files."
        _set_manifest_drive_result(manifest_path, "UPLOADED", detail)
        _upload_file(service, folder_id, manifest_path)
        final_files = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
        final_ok = len(final_files) == len(FINAL_OUTPUT_FILES) and {item.get("name", "") for item in final_files} == set(FINAL_OUTPUT_FILES)
        return DriveUploadResult(
            status="UPLOADED" if final_ok else "FAILED",
            publish_mode="component_replace",
            package_link=link,
            folder_id=folder_id,
            detail=detail if final_ok else "Drive post-replace exact-final validation failed.",
            uploaded_files=filenames,
            remote_files=tuple(final_files),
        )
    except Exception as exc:
        return DriveUploadResult(status="FAILED", publish_mode="component_replace", package_link=link, folder_id=folder_id,
            detail=f"Component replace failed: {type(exc).__name__}: {exc}")


def _prune_non_final_files(service, folder_id: str) -> None:
    query = f"'{folder_id}' in parents and trashed=false"
    remote = service.files().list(q=query, fields="files(id,name)", pageSize=100).execute().get("files", [])
    allowed = set(FINAL_OUTPUT_FILES)
    for item in remote:
        name = item.get("name", "")
        if name and name not in allowed:
            service.files().update(fileId=item["id"], body={"trashed": True}).execute()


def replace_existing_files(
    settings: Settings, *, source_dir: Path, manifest_path: Path, filenames: tuple[str, ...]
) -> DriveUploadResult:
    """Replace selected files in an existing exact-final package without creating a new folder.

    ``filenames`` may include any final package file such as ``whatsapp_caption.txt``,
    ``manifest.json``, PDFs, images, or audio. Manifest is written last after drive_status update.
    """
    names = tuple(dict.fromkeys(filenames))
    if not names or "manifest.json" not in names or any(name not in FINAL_OUTPUT_FILES for name in names):
        return DriveUploadResult(status="FAILED", publish_mode="package_repair", package_link="", detail="Invalid repair file set.")
    missing = [name for name in names if not (source_dir / name).exists()]
    if missing:
        return DriveUploadResult(status="FAILED", publish_mode="package_repair", package_link="", detail=f"Missing repair files: {missing}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    link = str(data.get("package", {}).get("package_link", ""))
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", link)
    folder_id = match.group(1) if match else str(data.get("package", {}).get("drive_folder_id", ""))
    if not settings.google_drive_upload_enabled or not folder_id:
        return DriveUploadResult(status="FAILED", publish_mode="package_repair", package_link=link, folder_id=folder_id,
            detail="Drive upload must be enabled and the existing folder ID must be present.")
    try:
        token = settings.google_drive_token_file or settings.project_root / "credentials" / "google_drive_token.json"
        service = _build_drive_service(settings.google_drive_credentials_file, token)
        query = f"'{folder_id}' in parents and trashed=false"
        before = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
        before_names = {item.get("name", "") for item in before}
        # Allow migration from legacy packages by uploading full finals when source has them.
        if before_names != set(FINAL_OUTPUT_FILES):
            for name in FINAL_OUTPUT_FILES:
                path = source_dir / name
                if path.exists() and name != "manifest.json":
                    _upload_file(service, folder_id, path)
            _prune_non_final_files(service, folder_id)
            before = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
            if {item.get("name", "") for item in before} != set(FINAL_OUTPUT_FILES):
                return DriveUploadResult(status="FAILED", publish_mode="package_repair", package_link=link, folder_id=folder_id,
                    detail=f"Drive preflight refused repair: found {[item.get('name', '') for item in before]}.", remote_files=tuple(before))
        for name in names:
            if name != "manifest.json":
                _upload_file(service, folder_id, source_dir / name)
        _prune_non_final_files(service, folder_id)
        detail = f"Replaced {len(names)} repaired files; Drive folder contains {len(FINAL_OUTPUT_FILES)} exact final files."
        _set_manifest_drive_result(manifest_path, "UPLOADED", detail)
        _upload_file(service, folder_id, manifest_path)
        after = service.files().list(q=query, fields="files(id,name,modifiedTime)", pageSize=100).execute().get("files", [])
        ok = len(after) == len(FINAL_OUTPUT_FILES) and {item.get("name", "") for item in after} == set(FINAL_OUTPUT_FILES)
        return DriveUploadResult(status="UPLOADED" if ok else "FAILED", publish_mode="package_repair", package_link=link,
            folder_id=folder_id, detail=detail if ok else "Drive post-repair exact-final validation failed.",
            uploaded_files=names, remote_files=tuple(after))
    except Exception as exc:
        return DriveUploadResult(status="FAILED", publish_mode="package_repair", package_link=link, folder_id=folder_id,
            detail=f"Drive package repair failed: {type(exc).__name__}: {exc}")


def _set_manifest_drive_result(path: Path, status: str, detail: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    package = data.setdefault("package", {})
    package["drive_status"] = status
    package["drive_detail"] = detail
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

__all__ = [
    "DriveUploadResult",
    "upload_final_package",
    "upload_story_package",
    "ensure_story_folder",
    "upload_files_to_folder",
    "verify_drive_text_links",
    "replace_component_files",
    "replace_existing_files",
]
