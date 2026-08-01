"""Public-safe rights helpers for derived web-assets.

Package manifests may contain operator contact fields. Public web_manifest.rights
and reader.md Rights sections must never expose contact_email.
"""
from __future__ import annotations

import copy
import json
import re
from typing import Any

_AUTHOR = "Svarna Gauranga Das"
_PUBLISHER = "Dauji Publication"
_PROJECT = "Bhāva"
_LOCATION = "Harrisburg, Pennsylvania, USA"

_RIGHTS_LIMITATION = (
    "The copyright claim applies only to the original writing, adaptation, "
    "selection, arrangement, educational activities, human-authored design, "
    "editing, narration, and production components created for this publication. "
    "Scriptural quotations, traditional texts, trademarks, licensed materials, "
    "third-party works, and other preexisting materials remain the property of "
    "their respective rights holders and are credited separately."
)

_REGISTRATION_DISCLAIMER = (
    "A copyright notice and evidence record are not the same as formal "
    "U.S. Copyright Office registration."
)

_CONTACT_EMAIL_KEYS = frozenset({"contact_email", "email", "contact"})
# Operator / package-only keys that must never appear in public web_manifest.rights.
_OPERATOR_ONLY_KEYS = frozenset(
    {
        "artifact_notes",
        "artifacts",
        "local_paths",
        "output_dir",
        "package_dir",
        "work_dir",
        "drive",
        "drive_folder_id",
        "package_link",
        "hashes",
        "qa",
        "quality",
        "internal_notes",
        "operator_notes",
    }
)
_PUBLIC_RIGHTS_KEYS = frozenset(
    {
        "work_id",
        "title",
        "version",
        "author",
        "copyright_owner",
        "publisher",
        "publisher_role",
        "project",
        "location",
        "copyright_notice",
        "rights_limitation",
        "registration_disclaimer",
        "status",
        "synthesized_for_public_web",
        "source_reference",
        "scripture_reference",
        "source_dossier",
        "first_publication_date",
        "first_publication_year",
        "classroom_license",
        "classroom_license_line",
    }
)
_CONTACT_LINE_RE = re.compile(
    r"(?im)^\s*Contact:\s*\S+@\S+\s*$|^\s*-\s*Contact:\s*\S+@\S+\s*$"
)
_RIGHTS_HEADING_RE = re.compile(r"(?im)^##\s+Rights and Credits\s*$")
_EMAIL_RE = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
_USED_WITH_PERMISSION_RE = re.compile(r"(?i)used\s+with\s+permission")
_FILESYSTEM_PATH_RE = re.compile(
    r"(?i)(?:[A-Z]:\\|\\\\|/Users/|/home/|/var/|/tmp/|C:\\\\Windows\\\\Fonts)"
)


def _copyright_notice(*, year: int | None = None) -> str:
    year_prefix = f"{year} " if year is not None else ""
    return (
        f"Copyright © {year_prefix}{_AUTHOR}\n"
        "All rights reserved.\n\n"
        f"Published by {_PUBLISHER}\n"
        f"A {_PROJECT} Project publication\n\n"
        f"{_LOCATION}"
    )


def _is_nonempty_rights(value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return False
    # Treat a dict that only has empty/null values as empty.
    for item in value.values():
        if item not in (None, "", [], {}):
            return True
    return False


def sanitize_public_rights(
    package_manifest: dict[str, Any],
    *,
    story_no: str,
) -> dict[str, Any]:
    """Build a public-safe rights block for web_manifest.json.

    Copies package rights/publication, always omits contact_email, and synthesizes
    a minimal public-safe block when the package has no rights payload.
    """
    source = package_manifest.get("rights") or package_manifest.get("publication") or {}
    if _is_nonempty_rights(source):
        rights = copy.deepcopy(source)
        if not isinstance(rights, dict):
            rights = {}
    else:
        rights = {}

    if not _is_nonempty_rights(rights):
        title = str(package_manifest.get("title") or f"Story {story_no}")
        version = str(package_manifest.get("version") or "unversioned")
        rights = {
            "work_id": f"bhava-kb-bedtime-{story_no}",
            "title": title,
            "version": version,
            "author": _AUTHOR,
            "copyright_owner": _AUTHOR,
            "publisher": _PUBLISHER,
            "project": _PROJECT,
            "location": _LOCATION,
            "copyright_notice": _copyright_notice(),
            "rights_limitation": _RIGHTS_LIMITATION,
            "registration_disclaimer": _REGISTRATION_DISCLAIMER,
            "status": "publicly_available_unreviewed",
            "synthesized_for_public_web": True,
        }

    # Always strip contact fields from the public payload.
    for key in list(rights.keys()):
        if key in _CONTACT_EMAIL_KEYS or str(key).lower() in _CONTACT_EMAIL_KEYS:
            rights.pop(key, None)
        elif key in _OPERATOR_ONLY_KEYS or str(key).lower() in _OPERATOR_ONLY_KEYS:
            rights.pop(key, None)
        elif key not in _PUBLIC_RIGHTS_KEYS and not str(key).startswith("source_"):
            # Drop unknown operator metadata (fonts, hashes, nested artifact notes).
            rights.pop(key, None)

    # Normalize attribution fields when missing / misspelled.
    rights.setdefault("author", _AUTHOR)
    rights.setdefault("copyright_owner", _AUTHOR)
    rights.setdefault("publisher", _PUBLISHER)
    project = str(rights.get("project") or "").strip()
    if not project or project in {"Bhava", "BHAVA", "bhava"}:
        rights["project"] = _PROJECT
    else:
        rights.setdefault("project", _PROJECT)
    if not str(rights.get("copyright_notice") or "").strip():
        rights["copyright_notice"] = _copyright_notice()
    if not str(rights.get("rights_limitation") or "").strip():
        rights["rights_limitation"] = _RIGHTS_LIMITATION

    notice = str(rights.get("copyright_notice") or "")
    if _USED_WITH_PERMISSION_RE.search(notice):
        rights["copyright_notice"] = _USED_WITH_PERMISSION_RE.sub("", notice).strip()
    limitation = str(rights.get("rights_limitation") or "")
    if _USED_WITH_PERMISSION_RE.search(limitation):
        rights["rights_limitation"] = _USED_WITH_PERMISSION_RE.sub("", limitation).strip()

    # Hard guard: no filesystem paths or emails in the public JSON blob.
    blob = json.dumps(rights, ensure_ascii=False)
    if _EMAIL_RE.search(blob) or _FILESYSTEM_PATH_RE.search(blob):
        # Rebuild a minimal safe block rather than leak operator paths.
        title = str(rights.get("title") or package_manifest.get("title") or f"Story {story_no}")
        version = str(rights.get("version") or package_manifest.get("version") or "unversioned")
        rights = {
            "work_id": str(rights.get("work_id") or f"bhava-kb-bedtime-{story_no}"),
            "title": title,
            "version": version,
            "author": _AUTHOR,
            "copyright_owner": _AUTHOR,
            "publisher": _PUBLISHER,
            "project": _PROJECT,
            "location": _LOCATION,
            "copyright_notice": _copyright_notice(),
            "rights_limitation": _RIGHTS_LIMITATION,
            "registration_disclaimer": _REGISTRATION_DISCLAIMER,
            "status": str(rights.get("status") or "publicly_available"),
            "sanitized_for_public_web": True,
        }

    return rights


def public_rights_and_credits_markdown(
    rights: dict[str, Any],
    *,
    story_no: str,
) -> str:
    """Render a public-safe Rights and Credits section (no contact_email)."""
    author = str(rights.get("author") or rights.get("copyright_owner") or _AUTHOR)
    owner = str(rights.get("copyright_owner") or author or _AUTHOR)
    publisher = str(rights.get("publisher") or _PUBLISHER)
    project = str(rights.get("project") or _PROJECT)
    notice = str(rights.get("copyright_notice") or "").strip() or _copyright_notice()
    # Strip any contact lines that may have been copied from package notices.
    notice = "\n".join(
        line for line in notice.splitlines() if not re.search(r"(?i)^\s*Contact:", line)
    ).strip()
    limitation = str(rights.get("rights_limitation") or _RIGHTS_LIMITATION).strip()
    disclaimer = str(rights.get("registration_disclaimer") or _REGISTRATION_DISCLAIMER).strip()
    work_id = str(rights.get("work_id") or f"bhava-kb-bedtime-{story_no}")
    version = str(rights.get("version") or "unversioned")

    lines = [
        "## Rights and Credits",
        "",
        notice,
        "",
        limitation,
        "",
        f"- Work ID: `{work_id}`",
        f"- Version: `{version}`",
        f"- Author / copyright owner: {owner}",
        f"- Publisher / imprint: {publisher}",
        f"- Project: {project}",
    ]

    source_ref = None
    dossier = rights.get("source_dossier")
    if isinstance(dossier, dict):
        source_ref = dossier.get("source_reference")
        scripture_ref = dossier.get("scripture_reference")
    else:
        scripture_ref = None
    source_ref = source_ref or rights.get("source_reference")
    scripture_ref = scripture_ref or rights.get("scripture_reference")
    if source_ref:
        lines.append(f"- Source reference: {source_ref}")
    if scripture_ref:
        lines.append(f"- Scripture reference: {scripture_ref}")

    lines.extend(
        [
            "",
            "Scriptural quotations and preexisting source texts are not claimed as original "
            f"{project} authorship.",
            "",
            disclaimer,
        ]
    )
    text = "\n".join(lines).rstrip() + "\n"
    # Final hard guard: never emit an email address in the public reader section.
    text = _CONTACT_LINE_RE.sub("", text)
    text = _EMAIL_RE.sub("", text)
    text = re.sub(r"(?im)^\s*contact_email\s*[:=].*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def ensure_reader_rights_section(
    reader_md: str,
    rights: dict[str, Any],
    *,
    story_no: str,
) -> str:
    """Ensure reader.md has a Rights and Credits section without contact_email."""
    section = public_rights_and_credits_markdown(rights, story_no=story_no)
    text = reader_md or ""

    if _RIGHTS_HEADING_RE.search(text):
        # Replace existing section and strip any contact/email lines that remain.
        pattern = re.compile(
            r"(^|\n)##\s+Rights and Credits\s*\n.*?(?=\n##\s|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        updated = pattern.sub(lambda m: f"{m.group(1)}{section.rstrip()}", text, count=1)
        # Strip residual Contact / email lines anywhere in the document that came
        # from a prior rights block copy (keep story body emails if any — none expected).
        updated = _CONTACT_LINE_RE.sub("", updated)
        # Remove bare contact_email key leakage if present as prose.
        updated = re.sub(r"(?im)^\s*contact_email\s*[:=].*$", "", updated)
        return re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"

    return text.rstrip() + "\n\n" + section
