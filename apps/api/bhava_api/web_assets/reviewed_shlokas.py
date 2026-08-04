"""Hand-reviewed śloka / companion-verse records for Stories 001–021.

Rules:
- Never invent Sanskrit, transliteration, BBT translation, or purport text.
- Prefer null Sanskrit/transliteration over unverified text.
- Use chapter-framed Vedabase URLs when exact verse pins are not verified
  in local editorial docs (docs/editorial/).
- Every published story returns a reviewed row or an explicit not_applicable
  decision the UI can render honestly.
"""
from __future__ import annotations

from typing import Any

from .reviewed_sources import REVIEWER

REVIEWED_DATE = "2026-07-23"
REVIEWED_DATE_008_009 = "2026-07-27"
REVIEWED_DATE_010_020 = "2026-08-01"
REVIEWED_DATE_021 = "2026-08-03"

_CHAPTER_NOTE = (
    "Reviewed chapter-framed companion reference. Exact verse start/end deferred — "
    "not pinned in series_plan.csv scripture_reference or docs/editorial/; "
    "chapter Vedabase URL retained. Sanskrit and transliteration intentionally "
    "null (not invented)."
)


def _chapter_row(
    *,
    reference: str,
    url: str,
    child_explanation: str,
    reviewed_date: str,
    note: str = _CHAPTER_NOTE,
) -> dict[str, Any]:
    return {
        "reference": reference,
        "url": url,
        "sanskrit": None,
        "transliteration": None,
        "child_explanation": child_explanation,
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": reviewed_date,
        "note": note,
        "provenance": "bhava-original-explanation",
    }


def _not_applicable(
    *,
    reason: str,
    child_explanation: str,
    reviewed_date: str,
) -> dict[str, Any]:
    return {
        "reference": "No separate verse selected for this bedtime adaptation",
        "url": None,
        "sanskrit": None,
        "transliteration": None,
        "child_explanation": child_explanation,
        "review_status": "not_applicable",
        "reviewer": REVIEWER,
        "reviewed_date": reviewed_date,
        "note": reason,
        "decision": "no-separate-verse",
        "provenance": "bhava-reviewed-decision",
    }


REVIEWED_SHLOKAS: dict[str, dict[str, Any]] = {
    "001": {
        "status": "reviewed",
        "shlokas": [
            _not_applicable(
                reason=(
                    "Story 001 is framed by Krishna Book Chapter 1 (Earth's prayer). "
                    "No single SB verse was curated for the Ślokas tab; see Source tab "
                    "for the verified KB chapter link."
                ),
                child_explanation=(
                    "This bedtime story follows Mother Earth's prayer for help. "
                    "Open the Source tab for the Krishna Book chapter study link."
                ),
                reviewed_date=REVIEWED_DATE,
            )
        ],
    },
    "002": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.1.27–55 (wedding and heavenly voice window)",
                url="https://vedabase.io/en/library/sb/10/1/",
                child_explanation=(
                    "During Devakī and Vasudeva's wedding procession, a heavenly voice "
                    "warns Kaṁsa about Devakī's eighth child. Vasudeva answers with calm truthfulness."
                ),
                reviewed_date=REVIEWED_DATE,
                note=(
                    "Package scripture range SB 10.1.27–55; chapter URL used because "
                    "a single central verse was not pinned in local editorial docs. "
                    "Sanskrit/transliteration null."
                ),
            )
        ],
    },
    "003": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.1.56–61 (Vasudeva keeps his word)",
                url="https://vedabase.io/en/library/sb/10/1/",
                child_explanation=(
                    "When Devakī's first son is born, Vasudeva keeps his difficult promise "
                    "and brings the child to Kaṁsa with honest courage."
                ),
                reviewed_date=REVIEWED_DATE,
                note=(
                    "Package scripture range SB 10.1.56–61; chapter URL used. "
                    "Sanskrit/transliteration null."
                ),
            )
        ],
    },
    "004": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.1.62–69 (Nārada's warning)",
                url="https://vedabase.io/en/library/sb/10/1/",
                child_explanation=(
                    "Nārada's warning frightens Kaṁsa, yet Devakī and Vasudeva stay faithful "
                    "to the Lord even when locked away."
                ),
                reviewed_date=REVIEWED_DATE,
                note=(
                    "Package scripture range SB 10.1.62–69; chapter URL used. "
                    "Sanskrit/transliteration null."
                ),
            )
        ],
    },
    "005": {
        "status": "reviewed",
        "shlokas": [
            _not_applicable(
                reason=(
                    "Story 005 maps to complete Krishna Book Chapter 2 (demigod prayers). "
                    "Candidate verse set is large; no separate verse was selected for the "
                    "Ślokas tab. See Source for the KB chapter link."
                ),
                child_explanation=(
                    "The demigods pray for Lord Kṛṣṇa while He is still in the womb. "
                    "Study the Krishna Book chapter from the Source tab."
                ),
                reviewed_date=REVIEWED_DATE,
            )
        ],
    },
    "006": {
        "status": "reviewed",
        "shlokas": [
            _not_applicable(
                reason=(
                    "Story 006 maps to complete Krishna Book Chapter 3 (birth of Kṛṣṇa). "
                    "High-visibility chapter requires explicit single-verse sign-off; "
                    "none selected yet. See Source for the KB chapter link."
                ),
                child_explanation=(
                    "Lord Kṛṣṇa appears in Mathurā and is carried safely to Vraja. "
                    "Open the Source tab for the Krishna Book chapter study link."
                ),
                reviewed_date=REVIEWED_DATE,
            )
        ],
    },
    "007": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.4 (Kaṁsa's persecutions)",
                url="https://vedabase.io/en/library/sb/10/4/",
                child_explanation=(
                    "After Kṛṣṇa's birth, Kaṁsa grows more fearful and cruel, "
                    "while the Lord's devotees hold onto faith."
                ),
                reviewed_date=REVIEWED_DATE,
            )
        ],
    },
    "008": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.5 (meeting of Nanda and Vasudeva)",
                url="https://vedabase.io/en/library/sb/10/5/",
                child_explanation=(
                    "Nanda and Vasudeva meet with loving friendship after the birth celebrations, "
                    "sharing news and care for the two boys."
                ),
                reviewed_date=REVIEWED_DATE_008_009,
            )
        ],
    },
    "009": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.6 (Pūtanā)",
                url="https://vedabase.io/en/library/sb/10/6/",
                child_explanation=(
                    "The witch Pūtanā comes disguised as a nurse, but baby Kṛṣṇa "
                    "protects everyone and even gives her a motherly destination."
                ),
                reviewed_date=REVIEWED_DATE_008_009,
            )
        ],
    },
    "010": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.7 — cart-breaking pastime",
                url="https://vedabase.io/en/library/sb/10/7/",
                child_explanation=(
                    "At His childhood turning ceremony, hungry baby Kṛṣṇa kicks the handcart "
                    "and it collapses — showing the Lord's power even as a tiny child."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "011": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.7 — Tṛṇāvarta whirlwind pastime",
                url="https://vedabase.io/en/library/sb/10/7/",
                child_explanation=(
                    "The whirlwind demon Tṛṇāvarta lifts baby Kṛṣṇa into the sky, "
                    "but Kṛṣṇa becomes heavy, catches the demon's neck, and stays safe."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "012": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.7 — yawn / first universal-mouth vision",
                url="https://vedabase.io/en/library/sb/10/7/",
                child_explanation=(
                    "While nursing, Kṛṣṇa yawns and Mother Yaśodā sees the whole universe "
                    "inside His mouth — God is always God, even as a nursing child."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "013": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.8 — Garga Muni name-giving",
                url="https://vedabase.io/en/library/sb/10/8/",
                child_explanation=(
                    "Garga Muni comes secretly to Nanda's home and gives sacred names "
                    "to Kṛṣṇa and Balarāma, with careful protection from Kaṁsa."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "014": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.8 — crawling pastimes",
                url="https://vedabase.io/en/library/sb/10/8/",
                child_explanation=(
                    "Kṛṣṇa and Balarāma crawl with ankle bells, play in clay, "
                    "and are lovingly guarded by Yaśodā and Rohiṇī."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "015": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.8 — butter and yogurt mischief",
                url="https://vedabase.io/en/library/sb/10/8/",
                child_explanation=(
                    "The gopīs lovingly complain that Kṛṣṇa steals butter and feeds monkeys — "
                    "and Yaśodā smiles instead of giving harsh punishment."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "016": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.8 — dirt-eating universal form",
                url="https://vedabase.io/en/library/sb/10/8/",
                child_explanation=(
                    "Friends say Kṛṣṇa ate dirt. When He opens His mouth, Yaśodā sees "
                    "the cosmic manifestation, then motherly love returns by yoga-māyā."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "017": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.9 — Dāmodara binding",
                url="https://vedabase.io/en/library/sb/10/9/",
                child_explanation=(
                    "Mother Yaśodā tries to bind mischievous Kṛṣṇa with a rope. "
                    "The rope is always too short — until He kindly allows Himself to be bound."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "018": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.10 — Nalakūvara and Maṇigrīva",
                url="https://vedabase.io/en/library/sb/10/10/",
                child_explanation=(
                    "Bound to the mortar, Kṛṣṇa uproots the twin arjuna trees and "
                    "delivers Nalakūvara and Maṇigrīva from Nārada's curse."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "019": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.11 — Vatsāsura and Bakāsura",
                url="https://vedabase.io/en/library/sb/10/11/",
                child_explanation=(
                    "Kṛṣṇa protects the calves and cowherd boys from the calf-demon "
                    "Vatsāsura and the crane-demon Bakāsura."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "020": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.12 — Aghāsura",
                url="https://vedabase.io/en/library/sb/10/12/",
                child_explanation=(
                    "The serpent-demon Aghāsura opens a cave-like mouth to swallow the boys. "
                    "Kṛṣṇa enters and protects everyone in a gentle, child-safe way."
                ),
                reviewed_date=REVIEWED_DATE_010_020,
            )
        ],
    },
    "021": {
        "status": "reviewed",
        "shlokas": [
            _chapter_row(
                reference="SB 10.13 — Brahmā steals the boys and calves",
                url="https://vedabase.io/en/library/sb/10/13/",
                child_explanation=(
                    "Lord Brahmā hides the cowherd boys and calves to test Kṛṣṇa. "
                    "Kṛṣṇa expands Himself into their forms, protects every family, "
                    "and gently shows Brahmā His loving supremacy."
                ),
                reviewed_date=REVIEWED_DATE_021,
            )
        ],
    },
}


def shlokas_payload_for_story(story_no: str) -> dict[str, Any]:
    """Return shlokas.json payload for a story (reviewed when available)."""
    padded = story_no.zfill(3)
    reviewed = REVIEWED_SHLOKAS.get(padded)
    if reviewed:
        return {
            "story_no": padded,
            "status": reviewed["status"],
            "shlokas": list(reviewed["shlokas"]),
        }
    return {
        "story_no": padded,
        "status": "pending",
        "shlokas": [],
        "note": "Śloka curation pending human review; no verse invented.",
    }
