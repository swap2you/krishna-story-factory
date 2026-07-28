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
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

from .identity import PublicationIdentity
from .notices import (
    audio_notice_lines,
    compact_footer,
    image_credit_line,
    rights_and_credits_markdown,
)
from .work_manifest import first_publication_year

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
    # Shorter caption form per contract.
    short = (
        f"© {year} {identity.copyright_owner} · {identity.publisher} · {identity.project}"
        if year is not None
        else f"© {identity.copyright_owner} · {identity.publisher} · {identity.project}"
    )
    if short in text or line in text:
        return text if text.endswith("\n") else text + "\n"
    return text.rstrip() + "\n\n" + short + "\n"


def append_image_credit_strip(
    image_path: Path,
    dest_path: Path,
    *,
    year: int | None,
    ai_image: bool,
    identity: PublicationIdentity,
) -> dict:
    """Extend canvas downward with a restrained credit strip (no overlay on subject)."""
    credit = image_credit_line(year=year, ai_image=ai_image, identity=identity)
    with Image.open(image_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        strip_h = max(36, int(height * 0.045))
        canvas = Image.new("RGB", (width, height + strip_h), "#f7f1e6")
        canvas.paste(rgb, (0, 0))
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("arial.ttf", max(12, strip_h // 3))
        except OSError:
            font = ImageFont.load_default()
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
    }


def stamp_pdf_footer(
    pdf_path: Path,
    dest_path: Path,
    *,
    year: int | None,
    identity: PublicationIdentity,
) -> dict:
    """Append a one-page notice sheet rather than overlaying activity content.

    Existing activity PDFs vary in layout; a final rights page avoids colliding
    with answers, page numbers, or craft cut-lines while still attaching the
    compact notice to every distributed package.
    """
    from pypdf import PdfReader, PdfWriter

    footer = compact_footer(year=year, identity=identity)
    packet = io.BytesIO()
    c = pdf_canvas.Canvas(packet, pagesize=letter)
    width, height = letter
    c.setTitle("Rights notice")
    c.setAuthor(identity.copyright_owner)
    c.setCreator(f"{identity.project} / {identity.publisher}")
    c.setFont("Helvetica", 10)
    y = height - 72
    for line in (
        "Rights and Credits",
        "",
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
        for wrapped in _wrap(line, 90):
            c.drawString(54, y, wrapped)
            y -= 14
            if y < 54:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 72
    c.save()
    packet.seek(0)
    notice_reader = PdfReader(packet)
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in notice_reader.pages:
        writer.add_page(page)
    if writer.metadata is None:
        writer.add_metadata({})
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
        "method": "appended_rights_page",
        "pages_added": len(notice_reader.pages),
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
) -> dict:
    """Copy MP3 bytes and write ID3 metadata without re-encoding the audio stream."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(mp3_path.read_bytes())
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
    # Touch length to keep mutagen happy if stream info missing.
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
