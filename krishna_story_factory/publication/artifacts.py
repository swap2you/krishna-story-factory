"""Safe artifact notice application for versioned copyright retrofit.

Does not regenerate narrative content, TTS audio, or image pixels beyond a
bottom credit strip / PDF footer stamp / ID3 metadata.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

from mutagen.id3 import ID3, COMM, TALB, TIT2, TPE1, TCOP, TXXX, error as id3_error
from mutagen.mp3 import MP3
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas

from .fonts import get_reportlab_font_names, resolve_unicode_fonts
from .identity import PublicationIdentity
from .notices import (
    audio_notice_lines,
    compact_footer,
    image_credit_line,
    rights_and_credits_markdown,
)

_RIGHTS_HEADING_RE = re.compile(
    r"(^|\n)##\s+Rights and Credits\s*\n.*?(?=\n##\s|\n<!--|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest().lower()


def apply_story_md_rights(
    text: str,
    *,
    work_id: str,
    version: str,
    source_reference: str | None,
    scripture_reference: str | None,
    year: int | None,
    identity: PublicationIdentity,
) -> str:
    section = rights_and_credits_markdown(
        work_id=work_id,
        version=version,
        source_reference=source_reference,
        scripture_reference=scripture_reference,
        year=year,
        identity=identity,
    )
    if _RIGHTS_HEADING_RE.search(text):
        return _RIGHTS_HEADING_RE.sub(lambda m: f"{m.group(1)}{section.rstrip()}", text, count=1)
    comment = text.find("<!--")
    if comment >= 0:
        return text[:comment].rstrip() + "\n\n" + section + "\n" + text[comment:]
    return text.rstrip() + "\n\n" + section


def apply_caption_notice(text: str, *, year: int | None, identity: PublicationIdentity) -> str:
    line = compact_footer(year=year, identity=identity)
    short = (
        f"© {year} {identity.copyright_owner} · {identity.publisher} · {identity.project}"
        if year is not None
        else f"© {identity.copyright_owner} · {identity.publisher} · {identity.project}"
    )
    # Replace any prior compact notice to avoid duplicates across versions.
    cleaned = re.sub(
        r"\n*©[^\n]*(?:Dauji Publication|Bhāva)[^\n]*\n*$",
        "\n",
        text.rstrip(),
        flags=re.IGNORECASE,
    )
    if short in cleaned or line in cleaned:
        return cleaned if cleaned.endswith("\n") else cleaned + "\n"
    return cleaned.rstrip() + "\n\n" + short + "\n"


def append_image_credit_strip(
    image_path: Path,
    dest_path: Path,
    *,
    year: int | None,
    ai_image: bool,
    identity: PublicationIdentity,
) -> dict:
    """Extend canvas downward with a restrained Unicode credit strip."""
    fonts = resolve_unicode_fonts()
    credit = image_credit_line(year=year, ai_image=ai_image, identity=identity)
    with Image.open(image_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        strip_h = max(40, int(height * 0.05))
        canvas = Image.new("RGB", (width, height + strip_h), "#f7f1e6")
        canvas.paste(rgb, (0, 0))
        draw = ImageDraw.Draw(canvas)
        font = fonts.pillow_regular(max(14, strip_h // 3))
        draw.rectangle((0, height, width, height + strip_h), fill="#f7f1e6")
        draw.text(
            (width // 2, height + strip_h // 2),
            credit,
            fill="#3a2a18",
            font=font,
            anchor="mm",
        )
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest_path, format="PNG", optimize=True)
    return {
        "credit_line": credit,
        "strip_height_px": strip_h,
        "placement": "bottom_canvas_extension",
        "sacred_subject_overlay": False,
        "font": str(fonts.regular_path),
        "source_image": str(image_path),
    }


def stamp_pdf_footer(
    pdf_path: Path,
    dest_path: Path,
    *,
    year: int | None,
    identity: PublicationIdentity,
) -> dict:
    """Overlay a compact Unicode footer on every activity page and append rights page."""
    from pypdf import PdfReader, PdfWriter

    fonts = resolve_unicode_fonts()
    regular, bold = get_reportlab_font_names()
    footer = compact_footer(year=year, identity=identity)

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.clone_reader_document_root(reader)

    activity_count = len(reader.pages)
    for index in range(activity_count):
        page = writer.pages[index]
        box = page.mediabox
        page_w = float(box.width)
        page_h = float(box.height)
        overlay_buf = io.BytesIO()
        c = pdf_canvas.Canvas(overlay_buf, pagesize=(page_w, page_h))
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, page_w, 0.28 * inch, fill=1, stroke=0)
        c.setFillColorRGB(0.22, 0.16, 0.10)
        c.setFont(regular, 7.5)
        c.drawCentredString(page_w / 2, 0.14 * inch, footer[:120])
        c.save()
        overlay_buf.seek(0)
        overlay_page = PdfReader(overlay_buf).pages[0]
        page.merge_page(overlay_page)

    # Final detailed Rights and Credits page (Unicode embedded).
    rights_buf = io.BytesIO()
    c = pdf_canvas.Canvas(rights_buf, pagesize=letter)
    width, height = letter
    c.setTitle("Rights and Credits")
    c.setAuthor(identity.copyright_owner)
    c.setCreator(f"{identity.project} / {identity.publisher}")
    y = height - 72
    c.setFont(bold, 14)
    c.drawString(54, y, "Rights and Credits")
    y -= 28
    c.setFont(regular, 10)
    for line in (
        footer,
        "",
        f"Published by {identity.publisher}",
        f"A {identity.project} Project publication",
        identity.location,
        f"Contact: {identity.contact_email}",
        "",
        identity.rights_limitation,
        "",
        identity.registration_disclaimer,
    ):
        for wrapped in _wrap(line, 92):
            c.drawString(54, y, wrapped)
            y -= 14
            if y < 54:
                c.showPage()
                c.setFont(regular, 10)
                y = height - 72
    c.save()
    rights_buf.seek(0)
    rights_reader = PdfReader(rights_buf)
    for page in rights_reader.pages:
        writer.add_page(page)

    writer.add_metadata(
        {
            "/Author": identity.copyright_owner,
            "/Creator": identity.project,
            "/Producer": identity.publisher,
            "/Subject": footer,
        }
    )
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with dest_path.open("wb") as handle:
        writer.write(handle)
    return {
        "footer": footer,
        "method": "per_page_overlay_plus_rights_page",
        "activity_pages": len(reader.pages),
        "rights_pages_added": len(rights_reader.pages),
        "font": str(fonts.regular_path),
        "reportlab_font": regular,
    }


def write_audio_metadata(
    mp3_path: Path,
    dest_path: Path,
    *,
    title: str,
    year: int | None,
    identity: PublicationIdentity,
    sound_recording_claim_status: str,
    rights_url: str,
    rewrite_if_present: bool = False,
) -> dict:
    """Copy MP3 bytes and write ID3 metadata without re-encoding the audio stream."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(mp3_path.read_bytes())
    if not rewrite_if_present:
        try:
            existing = ID3(dest_path)
            if existing.get("TCOP") and identity.copyright_owner in str(existing.get("TCOP")):
                return {
                    "metadata_written": False,
                    "reencoded": False,
                    "skipped_existing": True,
                    "sound_recording_claim_status": sound_recording_claim_status,
                    "hash_changed_due_to_container_tags": False,
                }
        except id3_error:
            pass

    audio = MP3(dest_path)
    try:
        tags = ID3(dest_path)
    except id3_error:
        tags = ID3()
    tags.delall("TIT2")
    tags.add(TIT2(encoding=3, text=title))
    tags.delall("TPE1")
    tags.add(TPE1(encoding=3, text=identity.copyright_owner))
    tags.delall("TALB")
    tags.add(TALB(encoding=3, text=f"{identity.project} · {identity.publisher}"))
    notice = " | ".join(
        audio_notice_lines(
            year=year,
            sound_recording_claim_status=sound_recording_claim_status,
            identity=identity,
        )
    )
    tags.delall("TCOP")
    tags.add(TCOP(encoding=3, text=notice))
    tags.delall("COMM")
    tags.add(COMM(encoding=3, lang="eng", desc="Rights", text=notice))
    tags.delall("TXXX")
    tags.add(TXXX(encoding=3, desc="Publisher", text=identity.publisher))
    tags.add(TXXX(encoding=3, desc="Project", text=identity.project))
    tags.add(TXXX(encoding=3, desc="RightsURL", text=rights_url))
    tags.add(
        TXXX(
            encoding=3,
            desc="SoundRecordingClaimStatus",
            text=sound_recording_claim_status,
        )
    )
    if year is not None:
        tags.add(TXXX(encoding=3, desc="FirstPublicationYear", text=str(year)))
    tags.save(dest_path)
    _ = audio.info.length if audio.info else None
    return {
        "metadata_written": True,
        "reencoded": False,
        "sound_recording_claim_status": sound_recording_claim_status,
        "copyright_text": notice,
        "hash_changed_due_to_container_tags": True,
    }


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if len(trial) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
