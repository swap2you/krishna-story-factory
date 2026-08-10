"""Generate P01C synthetic fixture package (not for production scripture)."""
from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


MARKER = "TEST FIXTURE — NOT APPROVED DEVOTIONAL CONTENT"


def main() -> None:
    stanzas = [
        {
            "block_id": "st-1",
            "block_type": "stanza",
            "ord": 1,
            "devanagari": nfc("परीक्षण श्लोक एक — TEST FIXTURE"),
            "iast": nfc("parīkṣaṇa śloka eka — TEST FIXTURE"),
            "translation_en": f"Structural stanza one. {MARKER}",
            "translator": "TEST FIXTURE — not a real translator",
            "edition": "Synthetic structural fixture v1",
            "exact_locator": "fixture://KF-P01C-FIXTURE-001/st-1",
            "word_meanings": [{"term": "parīkṣaṇa", "meaning": "TEST FIXTURE gloss — not doctrinal"}],
            "lens_explanations": {
                "little_learner": "One short idea: this is a TEST FIXTURE placeholder.",
                "explorer": "Explorer note: TEST FIXTURE — practice finding Devanāgarī, IAST, and English.",
                "teen": "Teen note: TEST FIXTURE scaffolding only; no doctrinal claim.",
                "study": "Study note: TEST FIXTURE for schema/export/hash verification.",
            },
            "asset_refs": ["asset-placeholder-1"],
        },
        {
            "block_id": "st-2",
            "block_type": "stanza",
            "ord": 2,
            "devanagari": nfc("परीक्षण श्लोक द्वि — TEST FIXTURE"),
            "iast": nfc("parīkṣaṇa śloka dvi — TEST FIXTURE"),
            "translation_en": f"Structural stanza two. {MARKER}",
            "translator": "TEST FIXTURE — not a real translator",
            "edition": "Synthetic structural fixture v1",
            "exact_locator": "fixture://KF-P01C-FIXTURE-001/st-2",
            "word_meanings": [],
            "lens_explanations": {
                "little_learner": "Next idea: TEST FIXTURE only.",
                "explorer": "Explorer: second TEST FIXTURE stanza.",
                "teen": "Teen: TEST FIXTURE reflection prompt placeholder.",
                "study": "Study: TEST FIXTURE citation slot empty by design.",
            },
            "asset_refs": ["asset-placeholder-2"],
        },
    ]

    parts: list[str] = []
    for b in stanzas:
        parts.extend([b["devanagari"], b["iast"], b["translation_en"]])
    canonical = sha("\n".join(parts))

    content = {
        "blocks": [
            {
                "block_id": "purpose",
                "block_type": "purpose",
                "ord": 0,
                "body": f"Purpose sentence for engineering preview. {MARKER}",
            },
            *stanzas,
            {
                "block_id": "context",
                "block_type": "context",
                "ord": 80,
                "body": f"Context slot empty of real lore. {MARKER}",
            },
            {
                "block_id": "practice",
                "block_type": "practice",
                "ord": 90,
                "body": f"Practice prompt placeholder. {MARKER}",
            },
        ]
    }

    record = {
        "record_id": "KF-P01C-FIXTURE-001",
        "slug": "p01c-structural-fixture",
        "title": "P01C Structural Learning-Page Fixture",
        "title_iast": "P01C Structural Learning-Page Fixture",
        "content_type": "prayer",
        "pillar": "Prayer and Sloka",
        "cluster": "Phase1 Pilot Engineering",
        "pathway": "studio-preview",
        "source_tier_required": "A1",
        "lifecycle": "source_research",
        "package_status": "research_backlog",
        "visibility": "private",
        "source_status": "SOURCE_BLOCKED",
        "audience_default": "explorer",
        "min_age": 5,
        "max_age": 22,
        "purpose_sentence": f"Private preview shell for Phase 1 engineering. {MARKER}",
        "record_version": "1.0.0-fixture",
        "canonical_text_hash": canonical,
        "unicode_normalization": "NFC",
        "relationships": [],
        "roadmap_ref": "TOP-0147",
        "fixture": True,
        "fixture_label": MARKER,
    }

    root = Path("content/knowledge/packages/KF-P01C-FIXTURE-001")
    root.mkdir(parents=True, exist_ok=True)
    (root / "record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "source_dossier.json").write_text(
        json.dumps(
            {
                "decision": "SOURCE_BLOCKED",
                "summary": "No authorized production edition attached. Synthetic fixture only.",
                "sources": [],
                "gaps": ["Authorized golden edition pending OD-14"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "rights.json").write_text(
        json.dumps(
            {
                "quotation_right": "unknown",
                "adaptation_right": "unknown",
                "translation_right": "unknown",
                "download_right": "internal_fixture_only",
                "commercial_right": "no",
                "notes": "Synthetic fixture — not licensed third-party text.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "assets.json").write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "asset_id": "asset-placeholder-1",
                        "role": "decorative",
                        "status": "placeholder",
                        "alt_text": "",
                        "decorative": True,
                        "board": "B_editorial_gouache",
                        "notes": "Governed placeholder slot — no production artwork",
                    },
                    {
                        "asset_id": "asset-placeholder-2",
                        "role": "decorative",
                        "status": "placeholder",
                        "alt_text": "",
                        "decorative": True,
                        "board": "B_editorial_gouache",
                        "notes": "Governed placeholder slot — no production artwork",
                    },
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "reviews.json").write_text(json.dumps({"reviews": []}, indent=2) + "\n", encoding="utf-8")
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "package_version": "1.0.0-fixture",
                "schema": "knowledge_record_package.schema.json",
                "record_sha256": sha(json.dumps(record, ensure_ascii=False, sort_keys=True)),
                "content_sha256": sha(json.dumps(content, ensure_ascii=False, sort_keys=True)),
                "canonical_text_hash": canonical,
                "created_for": "P01C engineering foundation",
                "production_scripture": False,
                "production_artwork": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("canonical", canonical)
    print("written", root)


if __name__ == "__main__":
    main()
