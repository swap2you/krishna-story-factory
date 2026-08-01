#!/usr/bin/env python3
"""Normalize public IAST display titles in series_plan.csv and package manifests.

Does not rename filesystem slugs or package folder names.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IAST_TITLES = {
    "001": "The Earth Prays for Kṛṣṇa to Come",
    "004": "Nārada's Warning and Kaṁsa's Decision",
    "005": "Prayers by the Demigods for Lord Kṛṣṇa in the Womb",
    "006": "The Birth of Lord Kṛṣṇa",
    "007": "Kaṁsa Begins His Persecutions",
    "017": "Mother Yaśodā Binds Lord Kṛṣṇa",
    "018": "The Deliverance of Nalakūvara and Maṇigrīva",
    "019": "Kṛṣṇa Protects the Calves from Vatsāsura and Bakāsura",
    "020": "Kṛṣṇa Protects Everyone from the Aghāsura Demon",
}


def main() -> None:
    plan = ROOT / "input" / "series_plan.csv"
    with plan.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames is not None
    for row in rows:
        no = row["chapter_no"].zfill(3)
        if no in IAST_TITLES:
            row["title"] = IAST_TITLES[no]
    with plan.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    plan_titles = {row["chapter_no"].zfill(3): row["title"] for row in rows}
    updated: list[str] = []
    output = ROOT / "output"
    for n in range(1, 21):
        no = f"{n:03d}"
        packages = [p for p in sorted(output.glob(f"{no}_*")) if (p / "manifest.json").is_file()]
        if len(packages) != 1:
            continue
        package = packages[0]
        manifest_path = package / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        title = plan_titles[no]
        if manifest.get("title") != title:
            manifest["title"] = title
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            updated.append(f"{no}: {title}")
    print(f"series_plan IAST overrides: {len(IAST_TITLES)}")
    print(f"manifests updated: {len(updated)}")
    for line in updated:
        print(line)


if __name__ == "__main__":
    main()
