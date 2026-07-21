"""Read back Story 005 Drive activity PDF + manifest for coverage proof."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER_ID = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"


def main() -> int:
    import pypdfium2 as pdfium
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.storage.google_drive_uploader import _build_drive_service

    settings = load_settings(ROOT)
    token = settings.google_drive_token_file or ROOT / "credentials" / "google_drive_token.json"
    service = _build_drive_service(settings.google_drive_credentials_file, token)
    query = f"'{FOLDER_ID}' in parents and trashed=false"
    files = service.files().list(q=query, fields="files(id,name)", pageSize=100).execute().get("files", [])
    names = sorted(item.get("name", "") for item in files)
    print("DRIVE_FILES", names, "COUNT", len(names))
    by_name = {item["name"]: item["id"] for item in files}
    dest = ROOT / ".work" / "qa" / "005"
    dest.mkdir(parents=True, exist_ok=True)
    pdf_bytes = service.files().get_media(fileId=by_name["activity_sheet.pdf"]).execute()
    (dest / "drive_activity_sheet.pdf").write_bytes(pdf_bytes)
    manifest_text = service.files().get_media(fileId=by_name["manifest.json"]).execute().decode("utf-8")
    (dest / "drive_manifest.json").write_text(manifest_text, encoding="utf-8")
    data = json.loads(manifest_text)
    print("DRIVE_MANIFEST_COV", data.get("activity", {}).get("matching_coverage"))
    print("DRIVE_STATUS", data.get("package", {}).get("drive_status"))
    print("DRIVE_LINK", data.get("package", {}).get("package_link"))
    doc = pdfium.PdfDocument(str(dest / "drive_activity_sheet.pdf"))
    text = " ".join(doc[i].get_textpage().get_text_range() for i in range(len(doc))).lower()
    doc.close()
    labels = [
        "brahma",
        "shiva",
        "narada",
        "other demigods",
        "devaki",
        "leads the prayer gathering",
        "joins and offers prayers",
        "comes as a great sage and devotee",
        "offer respectful prayers",
        "carries krishna unseen within her",
    ]
    missing = [label for label in labels if label not in text]
    print("DRIVE_PDF_MISSING", missing or "none")
    from krishna_story_factory.outputs import FINAL_OUTPUT_FILES

    expected = set(FINAL_OUTPUT_FILES)
    return 0 if not missing and set(names) == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
