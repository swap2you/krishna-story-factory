"""Load the single authoritative publication identity configuration."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PublicationIdentity:
    copyright_owner: str
    public_author_name: str
    public_display_credit: str
    publisher: str
    publisher_role: str
    project: str
    location: str
    contact_email: str
    phone: None
    website_copyright_year: int
    rights_page_path: str
    rights_page_label: str
    rights_limitation: str
    registration_disclaimer: str
    classroom_license_enabled_default: bool
    classroom_license_line: str
    claimable_elements: tuple[str, ...]
    excluded_categories: tuple[str, ...]
    embed_contact_in_printables: bool
    raw: dict[str, Any]

    @property
    def owner(self) -> str:
        return self.copyright_owner


def identity_path(root: Path | None = None) -> Path:
    return (root or _REPO_ROOT) / "config" / "publication_identity.yaml"


def load_identity(root: Path | None = None) -> PublicationIdentity:
    path = identity_path(root)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid publication identity file: {path}")
    phone = data.get("phone")
    if phone not in (None, "", "null"):
        raise ValueError("publication_identity.phone must be null")
    owner = str(data["copyright_owner"]).strip()
    if "Swarna" in owner or owner != "Svarna Gauranga Das":
        raise ValueError(f"Unexpected copyright_owner spelling: {owner!r}")
    email = str(data["contact_email"]).strip()
    if email and email != "svarnagaurangdas@gmail.com":
        raise ValueError(f"Unexpected contact_email: {email!r}")
    publisher = str(data["publisher"]).strip()
    if publisher != "Dauji Publication":
        raise ValueError(f"Unexpected publisher: {publisher!r}")
    display = str(data.get("public_display_credit") or owner).strip()
    if "Swapnil Patil" in display:
        raise ValueError("public_display_credit must not include civil/professional identity.")
    return PublicationIdentity(
        copyright_owner=owner,
        public_author_name=str(data.get("public_author_name") or owner).strip(),
        public_display_credit=display,
        publisher=publisher,
        publisher_role=str(data.get("publisher_role") or "publishing imprint").strip(),
        project=str(data["project"]).strip(),
        location=str(data["location"]).strip(),
        contact_email=email,
        phone=None,
        website_copyright_year=int(data["website_copyright_year"]),
        rights_page_path=str(data.get("rights_page_path") or "/rights").strip(),
        rights_page_label=str(data.get("rights_page_label") or "Copyright & Permissions").strip(),
        rights_limitation=str(data["rights_limitation"]).strip(),
        registration_disclaimer=str(data["registration_disclaimer"]).strip(),
        classroom_license_enabled_default=bool(data.get("classroom_license_enabled_default", False)),
        classroom_license_line=str(data.get("classroom_license_line") or "").strip(),
        claimable_elements=tuple(data.get("claimable_elements") or ()),
        excluded_categories=tuple(data.get("excluded_categories") or ()),
        embed_contact_in_printables=bool(data.get("embed_contact_in_printables", False)),
        raw=data,
    )


@lru_cache(maxsize=1)
def get_identity() -> PublicationIdentity:
    return load_identity()
