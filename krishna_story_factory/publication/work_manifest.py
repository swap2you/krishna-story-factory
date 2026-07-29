"""Versioned original-work manifest schema helpers."""
from __future__ import annotations

from datetime import date
from typing import Any

WORK_MANIFEST_SCHEMA_VERSION = "1.0"

REQUIRED_FIELDS = (
    "schema_version",
    "work_id",
    "title",
    "work_type",
    "version",
    "status",
    "author",
    "copyright_owner",
    "publisher",
    "project",
    "location",
    "contact_email",
    "registration_status",
    "sound_recording_claim_status",
    "copyright_notice",
    "rights_limitation",
    "human_authorship_claim",
    "ai_assistance",
)

ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "review",
        "privately_shared",
        "publicly_available_unreviewed",
        "published",
        "withdrawn",
        "superseded",
    }
)

ALLOWED_REGISTRATION = frozenset(
    {
        "not_reviewed",
        "registration_planned",
        "application_prepared",
        "submitted",
        "registered",
        "refused",
        "supplementary_registration_needed",
    }
)

ALLOWED_SOUND = frozenset(
    {"not_applicable", "needs_manual_review", "approved", "declined"}
)


def first_publication_year(manifest: dict[str, Any] | None) -> int | None:
    """Return a year only when first_publication_date is reviewed and present.

    A work is treated as reviewed for year emission only when status is
    ``published`` and ``first_publication_date`` is an ISO date string.
    """
    data = manifest or {}
    if str(data.get("status") or "") != "published":
        return None
    raw = data.get("first_publication_date")
    if not raw:
        return None
    text = str(raw).strip()
    try:
        return date.fromisoformat(text[:10]).year
    except ValueError:
        return None


def validate_work_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in manifest or manifest[field] in (None, ""):
            errors.append(f"missing_required:{field}")
    status = str(manifest.get("status") or "")
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"invalid_status:{status}")
    reg = str(manifest.get("registration_status") or "")
    if reg and reg not in ALLOWED_REGISTRATION:
        errors.append(f"invalid_registration_status:{reg}")
    sound = str(manifest.get("sound_recording_claim_status") or "")
    if sound and sound not in ALLOWED_SOUND:
        errors.append(f"invalid_sound_recording_claim_status:{sound}")
    if status == "published" and not manifest.get("first_publication_date"):
        errors.append("published_requires_first_publication_date")
    if reg == "registered" and not manifest.get("registration_number"):
        errors.append("registered_requires_registration_number")
    owner = str(manifest.get("copyright_owner") or "")
    if owner and ("Swarna" in owner or owner != "Svarna Gauranga Das"):
        errors.append("invalid_copyright_owner_spelling")
    email = str(manifest.get("contact_email") or "")
    if email and email != "svarnagaurangdas@gmail.com":
        errors.append("invalid_contact_email")
    if manifest.get("phone") not in (None, "", "null"):
        errors.append("phone_must_be_null")
    year = first_publication_year(manifest)
    notice = str(manifest.get("copyright_notice") or "")
    if year is None and any(token in notice for token in ("© 20", "Copyright © 20")):
        # Compact notices without a reviewed year must not invent a calendar year.
        if "© 20" in notice or "Copyright © 20" in notice:
            errors.append("year_emitted_without_reviewed_first_publication")
    return errors


def build_story_rights_block(
    *,
    story_no: str,
    title: str,
    version: str,
    supersedes: str | None,
    source_reference: str | None,
    scripture_reference: str | None,
    file_sha256: dict[str, str],
    prior_sha256: dict[str, str],
    identity,
    ai_assistance: dict[str, Any],
    human_authorship_claim: str,
    sound_recording_claim_status: str = "needs_manual_review",
    status: str = "publicly_available_unreviewed",
    first_publication_date: str | None = None,
    classroom_license_enabled: bool = False,
) -> dict[str, Any]:
    from .notices import compact_footer, standard_visual_notice

    year = first_publication_year(
        {"status": status, "first_publication_date": first_publication_date}
    )
    work_id = f"bhava-kb-bedtime-{story_no}"
    block = {
        "schema_version": WORK_MANIFEST_SCHEMA_VERSION,
        "work_id": work_id,
        "title": title,
        "work_type": "bedtime_story_package",
        "version": version,
        "status": status,
        "author": identity.public_author_name,
        "contributors": [],
        "copyright_owner": identity.copyright_owner,
        "publisher": identity.publisher,
        "publisher_role": identity.publisher_role,
        "project": identity.project,
        "location": identity.location,
        "contact_email": identity.contact_email,
        "phone": None,
        "creation_date": None,
        "private_share_date": None,
        "public_availability_date": None,
        "first_publication_date": first_publication_date,
        "publication_country": "US",
        "source_dossier": {
            "source_reference": source_reference,
            "scripture_reference": scripture_reference,
        },
        "scriptural_references": [scripture_reference] if scripture_reference else [],
        "preexisting_material": [
            "Krishna Book narrative source",
            "scriptural tradition referenced by source dossier",
        ],
        "third_party_assets": [],
        "asset_licenses": [],
        "font_licenses": [],
        "ai_assistance": ai_assistance,
        "human_authorship_claim": human_authorship_claim,
        "sound_recording_claim_status": sound_recording_claim_status,
        "files": sorted(file_sha256.keys()),
        "sha256": file_sha256,
        "prior_version_sha256": prior_sha256,
        "publication_channels": ["local_portal", "whatsapp_caption"],
        "copyright_notice": standard_visual_notice(year=year, identity=identity),
        "compact_footer": compact_footer(year=year, identity=identity),
        "rights_limitation": identity.rights_limitation,
        "registration_disclaimer": identity.registration_disclaimer,
        "review_approvals": [],
        "correction_history": [
            {
                "change": "versioned_copyright_retrofit",
                "note": "Added rights sidecar and artifact notices without regenerating narrative content.",
            }
        ],
        "supersedes": supersedes,
        "superseded_by": None,
        "registration_status": "not_reviewed",
        "classroom_license_enabled": classroom_license_enabled,
    }
    return block
