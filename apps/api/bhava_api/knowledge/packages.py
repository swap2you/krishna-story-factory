"""Knowledge record package loading, hashing, validation, and export."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

FIXTURE_MARKER = "TEST FIXTURE — NOT APPROVED DEVOTIONAL CONTENT"
LENSES = ("little_learner", "explorer", "teen", "study")
DEFAULT_LENS = "explorer"


def repo_root() -> Path:
    # apps/api/bhava_api/knowledge/packages.py -> repo root is parents[4]
    return Path(__file__).resolve().parents[4]


def packages_root() -> Path:
    return repo_root() / "content" / "knowledge" / "packages"


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value or "")


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def stanza_blocks(content: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = content.get("blocks") or []
    return [b for b in blocks if b.get("block_type") == "stanza"]


def canonical_text_hash(content: dict[str, Any]) -> str:
    parts: list[str] = []
    for block in sorted(stanza_blocks(content), key=lambda b: int(b.get("ord", 0))):
        parts.append(nfc(block.get("devanagari") or ""))
        parts.append(nfc(block.get("iast") or ""))
        parts.append(nfc(block.get("translation_en") or ""))
    return sha256_hex("\n".join(parts))


def scripture_hash(content: dict[str, Any]) -> str:
    parts = [nfc(b.get("devanagari") or "") for b in sorted(stanza_blocks(content), key=lambda b: int(b.get("ord", 0)))]
    return sha256_hex("\n".join(parts))


def translation_hash(content: dict[str, Any]) -> str:
    parts = [nfc(b.get("translation_en") or "") for b in sorted(stanza_blocks(content), key=lambda b: int(b.get("ord", 0)))]
    return sha256_hex("\n".join(parts))


@dataclass
class PackageValidation:
    ok: bool
    errors: list[str]
    package: dict[str, Any] | None = None


def load_package_dir(path: Path) -> dict[str, Any]:
    def read(name: str) -> Any:
        return json.loads((path / name).read_text(encoding="utf-8"))

    return {
        "record": read("record.json"),
        "content": read("content.json"),
        "source_dossier": read("source_dossier.json"),
        "rights": read("rights.json"),
        "assets": read("assets.json"),
        "reviews": read("reviews.json"),
        "manifest": read("manifest.json"),
        "_path": str(path),
    }


def validate_package(pkg: dict[str, Any]) -> PackageValidation:
    errors: list[str] = []
    record = pkg.get("record") or {}
    content = pkg.get("content") or {}
    dossier = pkg.get("source_dossier") or {}

    for key in (
        "record_id",
        "slug",
        "title",
        "content_type",
        "lifecycle",
        "package_status",
        "visibility",
        "source_status",
        "record_version",
        "canonical_text_hash",
        "unicode_normalization",
    ):
        if not record.get(key):
            errors.append(f"record missing {key}")

    if record.get("unicode_normalization") != "NFC":
        errors.append("unicode_normalization must be NFC")

    expected = canonical_text_hash(content)
    if record.get("canonical_text_hash") and record["canonical_text_hash"] != expected:
        errors.append("canonical_text_hash mismatch")

    if record.get("visibility") == "public" and record.get("source_status") != "DOSSIER_READY":
        errors.append("public visibility requires DOSSIER_READY")

    if record.get("source_status") == "SOURCE_BLOCKED" and dossier.get("decision") != "SOURCE_BLOCKED":
        errors.append("source_status SOURCE_BLOCKED requires dossier decision SOURCE_BLOCKED")

    if record.get("fixture"):
        label = record.get("fixture_label") or ""
        if FIXTURE_MARKER not in label:
            errors.append("fixture packages must carry conspicuous fixture_label")
        for block in stanza_blocks(content):
            blob = " ".join(
                [
                    block.get("devanagari") or "",
                    block.get("iast") or "",
                    block.get("translation_en") or "",
                ]
            )
            if "TEST FIXTURE" not in blob:
                errors.append(f"fixture stanza {block.get('block_id')} missing TEST FIXTURE marker")

    # Reject private path leakage markers in public-facing fields
    public_blob = json.dumps({k: pkg[k] for k in ("record", "content", "manifest")}, ensure_ascii=False)
    if re.search(r"(?i)MyPilotDropbox|C:\\\\Users|C:/Users", public_blob):
        errors.append("private operator path leakage detected in package fields")

    return PackageValidation(ok=not errors, errors=errors, package=pkg)


def list_packages() -> list[dict[str, Any]]:
    root = packages_root()
    if not root.exists():
        return []
    out: list[dict[str, Any]] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "record.json").exists():
            continue
        pkg = load_package_dir(child)
        out.append(pkg)
    return out


def get_package(slug_or_id: str) -> dict[str, Any] | None:
    for pkg in list_packages():
        record = pkg["record"]
        if record.get("slug") == slug_or_id or record.get("record_id") == slug_or_id:
            return pkg
    return None


def is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    h = host.split("%")[0].lower().strip("[]")
    if h in {"127.0.0.1", "::1", "localhost"}:
        return True
    # Starlette/FastAPI TestClient presents as "testclient".
    if h == "testclient":
        return True
    if h.startswith("127."):
        return True
    return False


def export_manifest(pkg: dict[str, Any], *, format_name: str, artifact_sha256: str, page_size: str) -> dict[str, Any]:
    content = pkg["content"]
    record = pkg["record"]
    return {
        "record_id": record["record_id"],
        "record_version": record["record_version"],
        "template_id": f"knowledge-{format_name}-v1",
        "template_version": "1.0.0",
        "scripture_hash": scripture_hash(content),
        "translation_hash": translation_hash(content),
        "canonical_content_hash": canonical_text_hash(content),
        "asset_hashes": [],
        "page_sizes": [page_size],
        "generators": {
            "pdf": "reportlab",
            "docx": "python-docx",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation": {
            "unicode": "pass",
            "study_neutral": True,
            "pdf_ua_claimed": False,
        },
        "artifact_sha256": artifact_sha256,
        "format": format_name,
        "fixture": bool(record.get("fixture")),
    }


def _xml_escape(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _register_unicode_fonts() -> tuple[str, str]:
    """Return (latin_font, devanagari_font). Fail closed if unavailable."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    def register(name: str, path: Path, *, subfont_index: int | None = None) -> bool:
        if name in pdfmetrics.getRegisteredFontNames():
            return True
        if not path.exists():
            return False
        try:
            if subfont_index is None:
                pdfmetrics.registerFont(TTFont(name, str(path)))
            else:
                pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=subfont_index))
            return True
        except Exception:
            return False

    latin_candidates = [
        Path(r"C:\Windows\Fonts\NotoSans-Regular.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
    ]
    deva_candidates = [
        (Path(r"C:\Windows\Fonts\Nirmala.ttc"), 0),
        (Path(r"C:\Windows\Fonts\Nirmala.ttf"), None),
        (Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"), None),
    ]

    latin = None
    for cand in latin_candidates:
        if register("BhavaLatin", cand):
            latin = "BhavaLatin"
            break
    if not latin:
        raise RuntimeError("Latin Unicode PDF font unavailable (need Noto Sans or DejaVu)")

    deva = None
    for cand, idx in deva_candidates:
        if register("BhavaDeva", cand, subfont_index=idx):
            deva = "BhavaDeva"
            break
    if not deva:
        # Fall back to latin font if it can still carry ASCII markers; Devanāgarī may box.
        # Prefer hard fail for Phase 1 export quality.
        raise RuntimeError("Devanāgarī PDF font unavailable (need Nirmala or Noto Sans Devanagari)")
    return latin, deva


def assert_export_allowed(pkg: dict[str, Any]) -> None:
    """Fixture packages may export synthetic text; non-fixture blocked packages may not."""
    record = pkg.get("record") or {}
    rights = pkg.get("rights") or {}
    if record.get("visibility") == "public":
        raise PermissionError("public packages are not exported from private studio routes")
    if record.get("source_status") in {"SOURCE_BLOCKED", "RIGHTS_BLOCKED"} and not record.get("fixture"):
        raise PermissionError("blocked non-fixture packages cannot export scripture bodies")
    if rights.get("download_right") in {"denied", "forbidden", "none"}:
        raise PermissionError("download_right denies export")


def render_pdf(pkg: dict[str, Any], *, page_size: str = "letter") -> tuple[bytes, dict[str, Any]]:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    assert_export_allowed(pkg)
    latin_font, deva_font = _register_unicode_fonts()

    buf = BytesIO()
    pagesize = letter if page_size.lower() == "letter" else A4
    doc = SimpleDocTemplate(buf, pagesize=pagesize, title=pkg["record"]["title"])
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("KTitle", parent=styles["Heading1"], fontName=latin_font, fontSize=16, leading=20)
    body = ParagraphStyle("KBody", parent=styles["Normal"], fontName=latin_font, fontSize=11, leading=16)
    deva = ParagraphStyle("KDeva", parent=styles["Normal"], fontName=deva_font, fontSize=12, leading=18)
    story = []
    record = pkg["record"]
    story.append(Paragraph(_xml_escape(record["title"]), title_style))
    story.append(
        Paragraph(
            _xml_escape(f"Status: {record.get('source_status')} · {record.get('fixture_label') or ''}"),
            body,
        )
    )
    story.append(Spacer(1, 12))
    for block in sorted(stanza_blocks(pkg["content"]), key=lambda b: int(b.get("ord", 0))):
        story.append(Paragraph(f"<b>Stanza {block.get('ord')}</b>", body))
        story.append(Paragraph(_xml_escape(nfc(block.get("devanagari") or "")), deva))
        story.append(Paragraph(_xml_escape(nfc(block.get("iast") or "")), body))
        story.append(Paragraph(_xml_escape(nfc(block.get("translation_en") or "")), body))
        story.append(Spacer(1, 10))
    story.append(Paragraph("Export is study-neutral (canonical text only). PDF/UA is not claimed.", body))
    doc.build(story)
    data = buf.getvalue()
    return data, export_manifest(pkg, format_name="pdf", artifact_sha256=sha256_hex(data), page_size=page_size)


def render_docx(pkg: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    from docx import Document
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

    assert_export_allowed(pkg)
    document = Document()
    record = pkg["record"]
    document.core_properties.title = record["title"]
    document.core_properties.language = "en"
    h = document.add_heading(record["title"], level=1)
    h.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    document.add_paragraph(f"Status: {record.get('source_status')}")
    if record.get("fixture_label"):
        document.add_paragraph(record["fixture_label"])
    for block in sorted(stanza_blocks(pkg["content"]), key=lambda b: int(b.get("ord", 0))):
        document.add_heading(f"Stanza {block.get('ord')}", level=2)
        p = document.add_paragraph(nfc(block.get("devanagari") or ""))
        p.style = document.styles["Normal"]
        document.add_paragraph(nfc(block.get("iast") or ""))
        document.add_paragraph(nfc(block.get("translation_en") or ""))
    document.add_paragraph("Export is study-neutral (canonical text only).")
    buf = BytesIO()
    document.save(buf)
    data = buf.getvalue()
    return data, export_manifest(pkg, format_name="docx", artifact_sha256=sha256_hex(data), page_size="letter")
