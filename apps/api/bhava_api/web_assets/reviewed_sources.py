"""Hand-reviewed source boundaries and verified Vedabase URLs for Stories 001–007.

URLs were opened and confirmed on vedabase.io before recording. Do not invent links.
Private local PDF page ranges stay optional and are never served publicly.
"""
from __future__ import annotations

from typing import Any

# Reviewer identity for published portal attribution.
REVIEWER = "Svarna Gauranga Das"
REVIEWED_DATE = "2026-07-23"

# Vedabase URLs verified live before inclusion.
KB_1 = "https://vedabase.io/en/library/kb/1/"
KB_2 = "https://vedabase.io/en/library/kb/2/"
KB_3 = "https://vedabase.io/en/library/kb/3/"
KB_4 = "https://vedabase.io/en/library/kb/4/"
SB_10_1 = "https://vedabase.io/en/library/sb/10/1/"
SB_10_4 = "https://vedabase.io/en/library/sb/10/4/"


REVIEWED_SOURCES: dict[str, dict[str, Any]] = {
    "001": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "Opening through Brahmā receiving the Lord's message",
        "passage_end": "Earth's prayer and the Lord's reply (story boundary)",
        "vedabase_url": KB_1,
        "scripture_secondary": None,
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Bhāva cites chapter boundaries and links to Vedabase for study. "
            "It does not republish BBT books and does not claim a blanket license."
        ),
    },
    "002": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.27",
        "passage_end": "SB 10.1.55",
        "vedabase_url": KB_1,
        "scripture_secondary": {
            "work": "Śrīmad-Bhāgavatam",
            "canto": 10,
            "chapter": 1,
            "verse_start": 27,
            "verse_end": 55,
            "vedabase_url": SB_10_1,
        },
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Chapter/verse bounds follow the package scripture reference. "
            "Open Vedabase for the published text; Bhāva does not mirror it."
        ),
    },
    "003": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.56",
        "passage_end": "SB 10.1.61",
        "vedabase_url": KB_1,
        "scripture_secondary": {
            "work": "Śrīmad-Bhāgavatam",
            "canto": 10,
            "chapter": 1,
            "verse_start": 56,
            "verse_end": 61,
            "vedabase_url": SB_10_1,
        },
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Chapter/verse bounds follow the package scripture reference. "
            "Open Vedabase for the published text; Bhāva does not mirror it."
        ),
    },
    "004": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.62",
        "passage_end": "SB 10.1.69",
        "vedabase_url": KB_1,
        "scripture_secondary": {
            "work": "Śrīmad-Bhāgavatam",
            "canto": 10,
            "chapter": 1,
            "verse_start": 62,
            "verse_end": 69,
            "vedabase_url": SB_10_1,
        },
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Chapter/verse bounds follow the package scripture reference. "
            "Open Vedabase for the published text; Bhāva does not mirror it."
        ),
    },
    "005": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 2,
        "chapter_title": "Prayers by the Demigods for Lord Kṛṣṇa in the Womb",
        "passage_start": "Beginning of Krishna Book Chapter 2",
        "passage_end": "End of Krishna Book Chapter 2",
        "vedabase_url": KB_2,
        "scripture_secondary": None,
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Story maps to complete Krishna Book Chapter 2. "
            "Bhāva adaptations remain separate from the BBT publication."
        ),
    },
    "006": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 3,
        "chapter_title": "The Birth of Lord Kṛṣṇa",
        "passage_start": "Beginning of Krishna Book Chapter 3",
        "passage_end": "End of Krishna Book Chapter 3",
        "vedabase_url": KB_3,
        "scripture_secondary": None,
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Story maps to complete Krishna Book Chapter 3. "
            "Bhāva adaptations remain separate from the BBT publication."
        ),
    },
    "007": {
        "work": "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)",
        "author": "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda",
        "chapter_number": 4,
        "chapter_title": "Kaṁsa Begins His Persecutions",
        "passage_start": "Beginning of Krishna Book Chapter 4 / SB 10.4",
        "passage_end": "End of Krishna Book Chapter 4",
        "vedabase_url": KB_4,
        "scripture_secondary": {
            "work": "Śrīmad-Bhāgavatam",
            "canto": 10,
            "chapter": 4,
            "verse_start": None,
            "verse_end": None,
            "vedabase_url": SB_10_4,
        },
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "Story maps to Krishna Book Chapter 4 with SB 10.4 as companion scripture. "
            "Open Vedabase for published text; Bhāva does not mirror it."
        ),
    },
}


def source_links_for_story(story_no: str, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return public source_links.json rows for a story."""
    reviewed = REVIEWED_SOURCES.get(story_no)
    if reviewed:
        rows: list[dict[str, Any]] = [
            {
                "label": "Primary work",
                "reference": f"{reviewed['work']} — Chapter {reviewed['chapter_number']}: {reviewed['chapter_title']}",
                "work": reviewed["work"],
                "author": reviewed["author"],
                "chapter_number": reviewed["chapter_number"],
                "chapter_title": reviewed["chapter_title"],
                "passage_start": reviewed["passage_start"],
                "passage_end": reviewed["passage_end"],
                "vedabase_url": reviewed["vedabase_url"],
                "permissions_status": reviewed["permissions_status"],
                "provenance": reviewed["provenance"],
                "content_type": reviewed["content_type"],
                "review_status": reviewed["review_status"],
                "reviewer": reviewed["reviewer"],
                "reviewed_date": reviewed["reviewed_date"],
                "permissions_note": reviewed["permissions_note"],
            }
        ]
        secondary = reviewed.get("scripture_secondary")
        if isinstance(secondary, dict) and secondary.get("vedabase_url"):
            verse_bit = ""
            if secondary.get("verse_start") and secondary.get("verse_end"):
                verse_bit = f", texts {secondary['verse_start']}–{secondary['verse_end']}"
            rows.append(
                {
                    "label": "Companion scripture",
                    "reference": (
                        f"{secondary['work']} Canto {secondary.get('canto')} "
                        f"Chapter {secondary.get('chapter')}{verse_bit}"
                    ),
                    "work": secondary["work"],
                    "vedabase_url": secondary["vedabase_url"],
                    "permissions_status": "excerpt-needs-review",
                    "provenance": "bbt-source-derived",
                    "content_type": "scripture companion link",
                    "review_status": "reviewed",
                    "reviewer": REVIEWER,
                    "reviewed_date": REVIEWED_DATE,
                    "permissions_note": reviewed["permissions_note"],
                }
            )
        rows.append(
            {
                "label": "Bhāva original elements",
                "reference": "Bedtime narration adaptation, activities, and portal presentation",
                "permissions_status": "needs-review",
                "provenance": "bhava-original",
                "content_type": "portal adaptation",
                "review_status": "reviewed",
                "reviewer": REVIEWER,
                "reviewed_date": REVIEWED_DATE,
                "permissions_note": (
                    "Software, design, and original adaptations are Bhāva stewardship work. "
                    "They do not transfer ownership of BBT source publications."
                ),
            }
        )
        return rows

    # Future / unreviewed stories: honest needs-review seed from package facts only.
    links: list[dict[str, Any]] = []
    for key in ("source_reference", "scripture_reference"):
        val = manifest.get(key)
        if val:
            links.append(
                {
                    "label": key.replace("_", " ").title(),
                    "reference": val,
                    "permissions_status": "needs-review",
                    "provenance": "bbt-source-derived",
                    "review_status": "needs_review",
                    "vedabase_url": None,
                    "permissions_note": (
                        "Source boundary recorded from package metadata; "
                        "Vedabase link pending human verification."
                    ),
                }
            )
    return links
