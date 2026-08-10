"""Hand-reviewed source boundaries and verified Vedabase URLs for Stories 001–020.

URLs follow the Vedabase KB / SB library pattern used for 001–009. Do not invent links.
Private local PDF page ranges stay optional and are never served publicly.
Never claim “used with permission.”
"""
from __future__ import annotations

from typing import Any

# Reviewer identity for published portal attribution.
REVIEWER = "Svarna Gauranga Das"
REVIEWED_DATE = "2026-07-23"
REVIEWED_DATE_010_020 = "2026-08-01"
REVIEWED_DATE_021 = "2026-08-03"
REVIEWED_DATE_022 = "2026-08-03"
REVIEWED_DATE_023_025 = "2026-08-10"

# Vedabase URLs — same host/path pattern as Stories 001–009.
KB_1 = "https://vedabase.io/en/library/kb/1/"
KB_2 = "https://vedabase.io/en/library/kb/2/"
KB_3 = "https://vedabase.io/en/library/kb/3/"
KB_4 = "https://vedabase.io/en/library/kb/4/"
KB_5 = "https://vedabase.io/en/library/kb/5/"
KB_6 = "https://vedabase.io/en/library/kb/6/"
KB_7 = "https://vedabase.io/en/library/kb/7/"
KB_8 = "https://vedabase.io/en/library/kb/8/"
KB_9 = "https://vedabase.io/en/library/kb/9/"
KB_10 = "https://vedabase.io/en/library/kb/10/"
KB_11 = "https://vedabase.io/en/library/kb/11/"
KB_12 = "https://vedabase.io/en/library/kb/12/"
KB_13 = "https://vedabase.io/en/library/kb/13/"
KB_14 = "https://vedabase.io/en/library/kb/14/"
KB_15 = "https://vedabase.io/en/library/kb/15/"
KB_16 = "https://vedabase.io/en/library/kb/16/"
KB_17 = "https://vedabase.io/en/library/kb/17/"
SB_10_1 = "https://vedabase.io/en/library/sb/10/1/"
SB_10_2 = "https://vedabase.io/en/library/sb/10/2/"
SB_10_3 = "https://vedabase.io/en/library/sb/10/3/"
SB_10_4 = "https://vedabase.io/en/library/sb/10/4/"
SB_10_5 = "https://vedabase.io/en/library/sb/10/5/"
SB_10_6 = "https://vedabase.io/en/library/sb/10/6/"
SB_10_7 = "https://vedabase.io/en/library/sb/10/7/"
SB_10_8 = "https://vedabase.io/en/library/sb/10/8/"
SB_10_9 = "https://vedabase.io/en/library/sb/10/9/"
SB_10_10 = "https://vedabase.io/en/library/sb/10/10/"
SB_10_11 = "https://vedabase.io/en/library/sb/10/11/"
SB_10_12 = "https://vedabase.io/en/library/sb/10/12/"
SB_10_13 = "https://vedabase.io/en/library/sb/10/13/"
SB_10_14 = "https://vedabase.io/en/library/sb/10/14/"
SB_10_15 = "https://vedabase.io/en/library/sb/10/15/"
SB_10_16 = "https://vedabase.io/en/library/sb/10/16/"
SB_10_17 = "https://vedabase.io/en/library/sb/10/17/"

_WORK_KB = "Kṛṣṇa, the Supreme Personality of Godhead (Krishna Book)"
_AUTHOR = "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda"
_PERMS_NOTE_BOUNDS = (
    "Chapter/verse bounds follow the package scripture reference. "
    "Open Vedabase for the published text; Bhāva does not mirror it."
)
_PERMS_NOTE_CHAPTER = (
    "Story maps to Krishna Book chapter with SB companion scripture. "
    "Open Vedabase for published text; Bhāva does not mirror it."
)
_PERMS_NOTE_CHAPTER_DEFERRED = (
    "Story maps to Krishna Book chapter with SB companion scripture (chapter URL). "
    "Exact SB verse start/end deferred — not pinned in series_plan.csv or "
    "docs/editorial/; open Vedabase for published text; Bhāva does not mirror it."
)


def _sb_companion(
    *,
    chapter: int,
    vedabase_url: str,
    verse_start: int | None = None,
    verse_end: int | None = None,
    central_event: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "work": "Śrīmad-Bhāgavatam",
        "canto": 10,
        "chapter": chapter,
        "verse_start": verse_start,
        "verse_end": verse_end,
        "vedabase_url": vedabase_url,
    }
    if central_event:
        row["central_event"] = central_event
    return row


REVIEWED_SOURCES: dict[str, dict[str, Any]] = {
    "001": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "Opening through Brahmā receiving the Lord's message",
        "passage_end": "Earth's prayer and the Lord's reply (story boundary)",
        "vedabase_url": KB_1,
        "scripture_secondary": _sb_companion(
            chapter=1,
            vedabase_url=SB_10_1,
            central_event="Earth's prayer / advent framing (KB Ch.1 ↔ SB 10.1)",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "KB Ch.1 maps to SB 10.1 companion (chapter URL). Exact verse start/end "
            "not pinned in series_plan.csv for Story 001; Bhāva does not republish BBT text."
        ),
    },
    "002": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.27",
        "passage_end": "SB 10.1.55",
        "vedabase_url": KB_1,
        "scripture_secondary": _sb_companion(
            chapter=1,
            vedabase_url=SB_10_1,
            verse_start=27,
            verse_end=55,
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": _PERMS_NOTE_BOUNDS,
    },
    "003": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.56",
        "passage_end": "SB 10.1.61",
        "vedabase_url": KB_1,
        "scripture_secondary": _sb_companion(
            chapter=1,
            vedabase_url=SB_10_1,
            verse_start=56,
            verse_end=61,
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": _PERMS_NOTE_BOUNDS,
    },
    "004": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 1,
        "chapter_title": "Advent of Lord Kṛṣṇa",
        "passage_start": "SB 10.1.62",
        "passage_end": "SB 10.1.69",
        "vedabase_url": KB_1,
        "scripture_secondary": _sb_companion(
            chapter=1,
            vedabase_url=SB_10_1,
            verse_start=62,
            verse_end=69,
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": _PERMS_NOTE_BOUNDS,
    },
    "005": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 2,
        "chapter_title": "Prayers by the Demigods for Lord Kṛṣṇa in the Womb",
        "passage_start": "Beginning of Krishna Book Chapter 2",
        "passage_end": "End of Krishna Book Chapter 2",
        "vedabase_url": KB_2,
        "scripture_secondary": _sb_companion(
            chapter=2,
            vedabase_url=SB_10_2,
            central_event="demigod prayers in the womb (KB Ch.2 ↔ SB 10.2)",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "KB Ch.2 maps to SB 10.2 companion (chapter URL). Exact verse start/end "
            "not pinned in series_plan.csv; Bhāva adaptations remain separate from BBT text."
        ),
    },
    "006": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 3,
        "chapter_title": "The Birth of Lord Kṛṣṇa",
        "passage_start": "Beginning of Krishna Book Chapter 3",
        "passage_end": "End of Krishna Book Chapter 3",
        "vedabase_url": KB_3,
        "scripture_secondary": _sb_companion(
            chapter=3,
            vedabase_url=SB_10_3,
            central_event="birth of Lord Kṛṣṇa (KB Ch.3 ↔ SB 10.3)",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": (
            "KB Ch.3 maps to SB 10.3 companion (chapter URL). Exact verse start/end "
            "not pinned in series_plan.csv; Bhāva adaptations remain separate from BBT text."
        ),
    },
    "007": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 4,
        "chapter_title": "Kaṁsa Begins His Persecutions",
        "passage_start": "Beginning of Krishna Book Chapter 4 / SB 10.4",
        "passage_end": "End of Krishna Book Chapter 4",
        "vedabase_url": KB_4,
        "scripture_secondary": _sb_companion(chapter=4, vedabase_url=SB_10_4),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "008": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 5,
        "chapter_title": "The Meeting of Nanda and Vasudeva",
        "passage_start": "Opening of Krishna Book Chapter 5",
        "passage_end": "Conclusion of Krishna Book Chapter 5",
        "vedabase_url": KB_5,
        "scripture_secondary": _sb_companion(chapter=5, vedabase_url=SB_10_5),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": "2026-07-27",
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "009": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 6,
        "chapter_title": "Pūtanā Killed",
        "passage_start": "Nanda takes shelter; Kaṁsa sends Pūtanā",
        "passage_end": "Fragrant pyre and motherly destination teaching",
        "vedabase_url": KB_6,
        "scripture_secondary": _sb_companion(
            chapter=6,
            vedabase_url=SB_10_6,
            central_event="Pūtanā",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": "2026-07-27",
        "permissions_note": (
            "V1.7.2 repair: Story 009 must narrate the full Pūtanā pastime (KB Ch.6 / SB 10.6). "
            "Exact verse start/end deferred — chapter URL retained. "
            "Open Vedabase for published text; Bhāva does not mirror it."
        ),
    },
    "010": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 7,
        "chapter_title": "The Salvation of Tṛṇāvarta",
        "passage_start": "Childhood turning / first birthday ceremony begins",
        "passage_end": "Protective rites and charity after the cart collapses",
        "vedabase_url": KB_7,
        "scripture_secondary": _sb_companion(
            chapter=7,
            vedabase_url=SB_10_7,
            central_event="cart-breaking (utthāna / handcart)",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "011": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 7,
        "chapter_title": "The Salvation of Tṛṇāvarta",
        "passage_start": "Kṛṣṇa becomes heavy in Yaśodā's lap",
        "passage_end": "Residents recover Kṛṣṇa; Nanda remembers Vasudeva",
        "vedabase_url": KB_7,
        "scripture_secondary": _sb_companion(
            chapter=7,
            vedabase_url=SB_10_7,
            central_event="Tṛṇāvarta whirlwind",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "012": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 7,
        "chapter_title": "The Salvation of Tṛṇāvarta",
        "passage_start": "Yaśodā nurses Kṛṣṇa after Tṛṇāvarta",
        "passage_end": "First vision of the universe in His mouth while yawning",
        "vedabase_url": KB_7,
        "scripture_secondary": _sb_companion(
            chapter=7,
            vedabase_url=SB_10_7,
            central_event="yawn / first universal-mouth vision",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "013": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 8,
        "chapter_title": "Vision of the Universal Form",
        "passage_start": "Garga Muni arrives at Nanda's home",
        "passage_end": "Garga returns; Nanda feels most fortunate",
        "vedabase_url": KB_8,
        "scripture_secondary": _sb_companion(
            chapter=8,
            vedabase_url=SB_10_8,
            central_event="Garga Muni secret name-giving",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "014": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 8,
        "chapter_title": "Vision of the Universal Form",
        "passage_start": "Boys begin crawling after name-giving",
        "passage_end": "Mothers' protection as the boys begin to walk",
        "vedabase_url": KB_8,
        "scripture_secondary": _sb_companion(
            chapter=8,
            vedabase_url=SB_10_8,
            central_event="crawling pastimes",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "015": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 8,
        "chapter_title": "Vision of the Universal Form",
        "passage_start": "Gopīs assemble to lodge complaints",
        "passage_end": "Yaśodā smiles and withholds harsh chastisement",
        "vedabase_url": KB_8,
        "scripture_secondary": _sb_companion(
            chapter=8,
            vedabase_url=SB_10_8,
            central_event="butter and yogurt mischief complaints",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "016": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 8,
        "chapter_title": "Vision of the Universal Form",
        "passage_start": "Boys complain that Kṛṣṇa ate clay",
        "passage_end": "Droṇa-Dharā benediction; yoga-māyā restores motherly love",
        "vedabase_url": KB_8,
        "scripture_secondary": _sb_companion(
            chapter=8,
            vedabase_url=SB_10_8,
            central_event="dirt-eating second universal-form vision",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "017": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 9,
        "chapter_title": "Mother Yaśodā Binds Lord Kṛṣṇa",
        "passage_start": "Opening of Krishna Book Chapter 9",
        "passage_end": "Conclusion of Krishna Book Chapter 9",
        "vedabase_url": KB_9,
        "scripture_secondary": _sb_companion(
            chapter=9,
            vedabase_url=SB_10_9,
            central_event="Dāmodara rope-binding",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "018": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 10,
        "chapter_title": "The Deliverance of Nalakūvara and Maṇigrīva",
        "passage_start": "Opening of Krishna Book Chapter 10",
        "passage_end": "Conclusion of Krishna Book Chapter 10",
        "vedabase_url": KB_10,
        "scripture_secondary": _sb_companion(
            chapter=10,
            vedabase_url=SB_10_10,
            central_event="Nalakūvara and Maṇigrīva deliverance",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "019": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 11,
        "chapter_title": "Killing the Demons Vatsāsura and Bakāsura",
        "passage_start": "Opening of Krishna Book Chapter 11",
        "passage_end": "Conclusion of Krishna Book Chapter 11",
        "vedabase_url": KB_11,
        "scripture_secondary": _sb_companion(
            chapter=11,
            vedabase_url=SB_10_11,
            central_event="Vatsāsura and Bakāsura",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "020": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 12,
        "chapter_title": "The Killing of the Aghāsura Demon",
        "passage_start": "Opening of Krishna Book Chapter 12",
        "passage_end": "Conclusion of Krishna Book Chapter 12",
        "vedabase_url": KB_12,
        "scripture_secondary": _sb_companion(
            chapter=12,
            vedabase_url=SB_10_12,
            central_event="Aghāsura",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_010_020,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "021": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 13,
        "chapter_title": "The Stealing of the Boys and Calves by Brahmā",
        "passage_start": "Opening of Krishna Book Chapter 13",
        "passage_end": "Conclusion of Krishna Book Chapter 13",
        "vedabase_url": KB_13,
        "scripture_secondary": _sb_companion(
            chapter=13,
            vedabase_url=SB_10_13,
            central_event="Brahmā steals the boys and calves",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_021,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "022": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 14,
        "chapter_title": "Prayers Offered by Lord Brahmā to Lord Kṛṣṇa",
        "passage_start": "Opening of Krishna Book Chapter 14",
        "passage_end": "Conclusion of Krishna Book Chapter 14",
        "vedabase_url": KB_14,
        "scripture_secondary": _sb_companion(
            chapter=14,
            vedabase_url=SB_10_14,
            central_event="Brahmā offers prayers to Kṛṣṇa",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_022,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "023": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 15,
        "chapter_title": "The Killing of Dhenukāsura",
        "passage_start": "Opening of Krishna Book Chapter 15",
        "passage_end": "Conclusion of Krishna Book Chapter 15",
        "vedabase_url": KB_15,
        "scripture_secondary": _sb_companion(
            chapter=15,
            vedabase_url=SB_10_15,
            central_event="Dhenukāsura",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_023_025,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "024": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 16,
        "chapter_title": "Subduing Kāliya",
        "passage_start": "Opening of Krishna Book Chapter 16",
        "passage_end": "Conclusion of Krishna Book Chapter 16",
        "vedabase_url": KB_16,
        "scripture_secondary": _sb_companion(
            chapter=16,
            vedabase_url=SB_10_16,
            central_event="Kāliya",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_023_025,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
    "025": {
        "work": _WORK_KB,
        "author": _AUTHOR,
        "chapter_number": 17,
        "chapter_title": "Extinguishing the Forest Fire",
        "passage_start": "Opening of Krishna Book Chapter 17",
        "passage_end": "Conclusion of Krishna Book Chapter 17",
        "vedabase_url": KB_17,
        "scripture_secondary": _sb_companion(
            chapter=17,
            vedabase_url=SB_10_17,
            central_event="Forest fire",
        ),
        "permissions_status": "excerpt-needs-review",
        "provenance": "bbt-source-derived",
        "content_type": "bedtime adaptation boundary",
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_date": REVIEWED_DATE_023_025,
        "permissions_note": _PERMS_NOTE_CHAPTER_DEFERRED,
    },
}


def source_links_for_story(story_no: str, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return public source_links.json rows for a story."""
    reviewed = REVIEWED_SOURCES.get(story_no)
    if reviewed:
        reviewed_date = reviewed["reviewed_date"]
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
                "reviewed_date": reviewed_date,
                "permissions_note": reviewed["permissions_note"],
            }
        ]
        secondary = reviewed.get("scripture_secondary")
        if isinstance(secondary, dict) and secondary.get("vedabase_url"):
            verse_bit = ""
            if secondary.get("verse_start") and secondary.get("verse_end"):
                verse_bit = f", texts {secondary['verse_start']}–{secondary['verse_end']}"
            event_bit = ""
            if secondary.get("central_event"):
                event_bit = f" — {secondary['central_event']}"
            rows.append(
                {
                    "label": "Companion scripture",
                    "reference": (
                        f"{secondary['work']} Canto {secondary.get('canto')} "
                        f"Chapter {secondary.get('chapter')}{verse_bit}{event_bit}"
                    ),
                    "work": secondary["work"],
                    "vedabase_url": secondary["vedabase_url"],
                    "permissions_status": "excerpt-needs-review",
                    "provenance": "bbt-source-derived",
                    "content_type": "scripture companion link",
                    "review_status": "reviewed",
                    "reviewer": REVIEWER,
                    "reviewed_date": reviewed_date,
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
                "reviewed_date": reviewed_date,
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
