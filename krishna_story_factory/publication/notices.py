"""Copyright notice rendering from the centralized publication identity."""
from __future__ import annotations

from .identity import PublicationIdentity, get_identity
from .work_manifest import first_publication_year


def _year_prefix(year: int | None) -> str:
    return f"{year} " if year is not None else ""


def standard_visual_notice(
    *,
    year: int | None = None,
    identity: PublicationIdentity | None = None,
) -> str:
    ident = identity or get_identity()
    y = _year_prefix(year)
    lines = [
        f"Copyright © {y}{ident.copyright_owner}",
        "All rights reserved.",
        "",
        f"Published by {ident.publisher}",
        f"A {ident.project} Project publication",
        "",
        ident.location,
    ]
    if ident.embed_contact_in_printables and ident.contact_email:
        lines.append(f"Contact: {ident.contact_email}")
    return "\n".join(lines)


def compact_footer(
    *,
    year: int | None = None,
    identity: PublicationIdentity | None = None,
) -> str:
    ident = identity or get_identity()
    y = _year_prefix(year)
    # Printables use devotional copyright owner only — never civil/professional identity.
    credit = ident.copyright_owner or ident.public_display_credit
    return (
        f"© {y}{credit} · {ident.publisher} · {ident.project}"
    ).replace("©  ", "© ").strip()


def website_footer_lines(*, identity: PublicationIdentity | None = None) -> list[str]:
    ident = identity or get_identity()
    return [
        f"© {ident.website_copyright_year} {ident.public_display_credit} · {ident.publisher} · {ident.project}",
    ]


def image_credit_line(
    *,
    year: int | None = None,
    ai_image: bool = False,
    identity: PublicationIdentity | None = None,
) -> str:
    ident = identity or get_identity()
    y = _year_prefix(year)
    if ai_image:
        return (
            f"{ident.project} design and publication © {y}{ident.copyright_owner} · "
            f"{ident.publisher}"
        ).replace("©  ", "© ").strip()
    return (
        f"© {y}{ident.copyright_owner} · {ident.publisher} · {ident.project}"
    ).replace("©  ", "© ").strip()


def audio_notice_lines(
    *,
    year: int | None = None,
    sound_recording_claim_status: str = "needs_manual_review",
    identity: PublicationIdentity | None = None,
) -> list[str]:
    ident = identity or get_identity()
    y = _year_prefix(year)
    lines = [
        f"Text © {y}{ident.copyright_owner}".replace("©  ", "© ").strip(),
        f"Published by {ident.publisher}, a {ident.project} Project publication",
    ]
    if sound_recording_claim_status == "approved" and year is not None:
        lines.insert(1, f"Sound recording ℗ {year} {ident.copyright_owner}")
    else:
        lines.insert(
            1,
            "Sound recording ℗ claim: deferred pending manual rights review "
            f"(status={sound_recording_claim_status})",
        )
    return lines


def draft_watermark(*, identity: PublicationIdentity | None = None, year: int | None = None) -> str:
    ident = identity or get_identity()
    y = _year_prefix(year)
    return (
        f"DRAFT — NOT FOR DISTRIBUTION\n"
        f"Copyright © {y}{ident.copyright_owner}".replace("©  ", "© ").strip()
    )


def rights_and_credits_markdown(
    *,
    work_id: str,
    version: str,
    source_reference: str | None,
    scripture_reference: str | None,
    year: int | None = None,
    identity: PublicationIdentity | None = None,
    classroom_license: bool = False,
) -> str:
    ident = identity or get_identity()
    y = first_publication_year({"first_publication_date": f"{year}-01-01"} if year else {})
    notice = standard_visual_notice(year=y, identity=ident)
    lines = [
        "## Rights and Credits",
        "",
        notice,
        "",
        ident.rights_limitation,
        "",
        f"- Work ID: `{work_id}`",
        f"- Version: `{version}`",
        f"- Author / copyright owner: {ident.copyright_owner}",
        f"- Publisher / imprint: {ident.publisher} ({ident.publisher_role})",
        f"- Project: {ident.project}",
        f"- Contact: {ident.contact_email}",
    ]
    if source_reference:
        lines.append(f"- Source reference: {source_reference}")
    if scripture_reference:
        lines.append(f"- Scripture reference: {scripture_reference}")
    lines.extend(
        [
            "",
            "Scriptural quotations and preexisting source texts are not claimed as original "
            f"{ident.project} authorship.",
            "",
            ident.registration_disclaimer,
        ]
    )
    if classroom_license and ident.classroom_license_line:
        lines.extend(["", ident.classroom_license_line])
    return "\n".join(lines).rstrip() + "\n"
