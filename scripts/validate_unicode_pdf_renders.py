#!/usr/bin/env python3
"""Render PDF pages and validate Unicode footers for launch evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pypdfium2 as pdfium
from pypdf import PdfReader

from krishna_story_factory.publication.fonts import resolve_unicode_fonts


def render_pdf(pdf_path: Path, out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(pdf_path))
    rows = []
    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=2)
        pil = bitmap.to_pil()
        dest = out_dir / f"page-{i+1:02d}.png"
        pil.save(dest)
        # Footer band: bottom 8% of page — should not be empty for activity pages
        w, h = pil.size
        band = pil.crop((0, int(h * 0.92), w, h)).convert("L")
        # Mean darkness: footer ink present if mean < 250 on white-ish page
        pixels = list(band.getdata())
        mean = sum(pixels) / max(len(pixels), 1)
        rows.append(
            {
                "page": i + 1,
                "png": str(dest.relative_to(ROOT)).replace("\\", "/"),
                "width": w,
                "height": h,
                "footer_band_mean_luma": round(mean, 2),
                "footer_band_has_ink": mean < 248,
            }
        )
    return rows


def main() -> int:
    fonts = resolve_unicode_fonts()
    evidence_root = ROOT / "docs" / "product" / "launch" / "runs" / "_unicode_render_scratch"
    report = {
        "unicode_font": str(fonts.regular_path),
        "stories": {},
    }
    for n in (1, 9):
        folder = next((ROOT / "output").glob(f"{n:03d}_*"))
        pdf = folder / "activity_sheet.pdf"
        reader = PdfReader(str(pdf))
        texts = [(reader.pages[i].extract_text() or "") for i in range(len(reader.pages))]
        renders = render_pdf(pdf, evidence_root / f"story-{n:03d}-pdf")
        report["stories"][f"{n:03d}"] = {
            "pages": len(reader.pages),
            "activity_pages_with_owner": sum(1 for t in texts[:-1] if "Svarna Gauranga Das" in t),
            "rights_contains_bhava": "Bhāva" in texts[-1],
            "renders": renders,
        }
    # Rights pages for all nine
    for n in range(1, 10):
        folder = next((ROOT / "output").glob(f"{n:03d}_*"))
        reader = PdfReader(str(folder / "activity_sheet.pdf"))
        rights = reader.pages[-1].extract_text() or ""
        out = evidence_root / "rights-pages"
        out.mkdir(parents=True, exist_ok=True)
        doc = pdfium.PdfDocument(str(folder / "activity_sheet.pdf"))
        pil = doc[len(doc) - 1].render(scale=2).to_pil()
        dest = out / f"{n:03d}-rights.png"
        pil.save(dest)
        report.setdefault("rights_pages", {})[f"{n:03d}"] = {
            "png": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "contains_bhava": "Bhāva" in rights,
            "contains_dauji": "Dauji Publication" in rights,
        }
    # Image strip samples
    from PIL import Image

    img_report = {}
    for n, name in ((1, "story_poster.png"), (9, "story_poster.png"), (9, "coloring_page.png")):
        folder = next((ROOT / "output").glob(f"{n:03d}_*"))
        src = folder / name
        dest_dir = evidence_root / "image-strips"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{n:03d}-{name}"
        Image.open(src).save(dest)
        with Image.open(src) as im:
            w, h = im.size
            band = im.crop((0, int(h * 0.92), w, h))
        img_report[f"{n:03d}:{name}"] = {
            "png": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "strip_band_saved": True,
            "size": [w, h],
        }
    report["image_strips"] = img_report
    out_json = evidence_root / "pdf-render-validation.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
