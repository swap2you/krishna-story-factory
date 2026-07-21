"""Verify Story 005 Format V2 package metrics."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pypdfium2 as pdfium
from mutagen.mp3 import MP3

p = Path("output/005_prayers-by-the-demigods-for-lord-krishna-in-the-womb")
print("poster", hashlib.sha256((p / "story_poster.png").read_bytes()).hexdigest().upper())
print("coloring", hashlib.sha256((p / "coloring_page.png").read_bytes()).hexdigest().upper())
md = (p / "story.md").read_text(encoding="utf-8")
for section in [
    "## Recap",
    "## Devotional Meaning",
    "## Five Lessons",
    "## Think About It",
    "## Bedtime Prayer",
    "## Next Story Preview",
    "## Parent/Teacher Note",
]:
    print(section, section in md)
main = re.search(r"## Main Story\n(.*?)(?=\n## )", md, re.S).group(1)
print("main_words", len(re.findall(r"\b[\w']+\b", main)))
print("audio_s", round(float(MP3(p / "narration.mp3").info.length), 1))
manifest = json.loads((p / "manifest.json").read_text(encoding="utf-8"))
print("parent_key", manifest["activity"].get("parent_answer_key", {}).keys())
print("matching", manifest["activity"].get("matching_coverage"))
print("activity_qa", manifest["activity"].get("qa_score"), "pages", manifest["activity"].get("page_count"))
doc = pdfium.PdfDocument(str(p / "activity_sheet.pdf"))
p1 = doc[0].get_textpage().get_text_range().lower()
p3 = doc[2].get_textpage().get_text_range().lower()
doc.close()
print("p1_lotus_leak", "lotus petal" in p1)
print("p1_dup", "younger: younger" in p1)
print("p3_my_lotus", "my lotus" in p3)
print("recap_snip", re.search(r"## Recap\n(.*?)(?=\n## )", md, re.S).group(1)[:180].replace("\n", " "))
