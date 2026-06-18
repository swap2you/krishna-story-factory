from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .phone import normalize_phone_e164


@dataclass(frozen=True, slots=True)
class WhatsAppRecipient:
    name: str
    phone_e164: str
    opt_in: bool
    status: str
    notes: str = ""

    @property
    def phone_digits(self) -> str:
        return normalize_phone_e164(self.phone_e164)


def load_active_recipients(csv_path: Path) -> list[WhatsAppRecipient]:
    if not csv_path.exists():
        return []

    recipients: list[WhatsAppRecipient] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            opt_in = str(row.get("opt_in", "")).strip().lower() in {"1", "true", "yes", "y", "on"}
            status = str(row.get("status", "")).strip().lower()
            if not opt_in or status != "active":
                continue
            phone = normalize_phone_e164(str(row.get("phone_e164", "")).strip())
            if not phone:
                continue
            recipients.append(
                WhatsAppRecipient(
                    name=str(row.get("name", "")).strip(),
                    phone_e164=phone,
                    opt_in=opt_in,
                    status=status,
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return recipients
