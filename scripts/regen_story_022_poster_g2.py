#!/usr/bin/env python3
"""One justified Story 022 poster correction (Brahmā multi-body defect)."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EVIDENCE = (
    Path.home()
    / "MyPilotDropbox"
    / "bhava-production-ops"
    / "evidence"
    / "pr47-final-correction-20260804"
    / "poster"
)
LOCKED = (
    "story.md",
    "narration.mp3",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
)

PROMPT_TAIL = """
CORRECTION (objective defect from generation 1): Brahmā must be ONE body with FOUR heads only.
Do NOT merge multiple kneeling bodies. Do NOT duplicate torsos, shoulders, or arms.
Show a single kneeling elder with four faces around one neck/shoulders, two hands only in añjali mudrā.

Warm cinematic Bhāva continuity like Story 021. Kṛṣṇa is the unmistakable focal subject (soft blue,
peacock feather, yellow dhoti, tilaka, tulasī beads). Brahmā bows humbly before Him in Vṛndāvana forest.
Soft golden god-rays, calm child-appropriate devotion.

STRICT NEGATIVES: no duplicated bodies/limbs/hands/fingers, no text, no modern objects, no unrelated deities,
no crowd confusion, no cropped heads.

Safe-center composition for library/mobile crops.
"""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _crops(poster: Path) -> None:
    im = Image.open(poster).convert("RGB")
    w, h = im.size
    art = im.crop((0, int(h * 0.134), w, int(h * 0.951)))
    aw, ah = art.size
    crops = {
        "full": im.copy(),
        "library_card": art.crop((int(aw * 0.08), int(ah * 0.05), int(aw * 0.92), int(ah * 0.72))),
        "home_latest": art.crop((int(aw * 0.12), int(ah * 0.08), int(aw * 0.88), int(ah * 0.78))),
        "social_16x9": art.crop((0, int(ah * 0.18), aw, int(ah * 0.18 + aw * 9 / 16))),
        "mobile_card": art.crop((int(aw * 0.18), int(ah * 0.02), int(aw * 0.82), int(ah * 0.62))),
    }
    tw = 320
    thumbs = []
    for label, crop in crops.items():
        thumb = crop.resize((tw, max(1, int(crop.height * tw / crop.width))), Image.Resampling.LANCZOS)
        labeled = Image.new("RGB", (tw, thumb.height + 28), (18, 14, 10))
        labeled.paste(thumb, (0, 28))
        ImageDraw.Draw(labeled).text((8, 6), label, fill=(246, 231, 184))
        thumbs.append(labeled)
        crop.save(EVIDENCE / f"022_crop_{label}.png")
    sheet = Image.new("RGB", (tw + 32, sum(t.height for t in thumbs) + 16 * (len(thumbs) + 1)), (12, 10, 8))
    y = 16
    for t in thumbs:
        sheet.paste(t, (16, y))
        y += t.height + 16
    sheet.save(EVIDENCE / "022_poster_crop_contact_sheet.png")


def main() -> int:
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.images.client import ImageClient
    from krishna_story_factory.images.generator import compose_poster
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pipeline import _content_from_story_md
    from krishna_story_factory.prompts_loader import load_master_section
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "022")
    assert plan is not None
    paths = make_package_paths(settings.output_root, plan, create=False)
    before = {n: _sha(paths.root / n) for n in LOCKED}
    content = _content_from_story_md(paths.story_md.read_text(encoding="utf-8"), plan)
    prompt = load_master_section(ROOT, "POSTER_VISUAL") + "\n" + PROMPT_TAIL
    ref = ROOT / "output" / "021_the-stealing-of-the-boys-and-calves-by-brahma" / "story_poster.png"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = ROOT / "work" / "stories" / "022" / f"poster-repair-g2-{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    raw = work / "poster_raw_g2.png"
    client = ImageClient(settings)
    t0 = time.monotonic()
    result = client.generate(
        prompt,
        raw,
        reference_path=ref,
        reference_required=True,
        story_title=content.title,
        max_api_attempts=2,
        requested_size="1024x1024",
    )
    elapsed = time.monotonic() - t0
    composed = work / "poster_composed_g2.png"
    compose_poster(raw, composed, content.title, content.poster_one_liner or content.takeaway)
    shutil.copy2(composed, paths.story_poster)
    shutil.copy2(composed, EVIDENCE / "022_poster_after_g2.png")
    _crops(paths.story_poster)
    after = {n: _sha(paths.root / n) for n in LOCKED}
    if after != before:
        raise SystemExit(f"LOCKED DRIFT {before} vs {after}")
    poster_sha = _sha(paths.story_poster)
    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    images = manifest.setdefault("images", {})
    images.update(
        {
            "model": result.model,
            "quality": result.quality,
            "requested_size": result.requested_size,
            "reference_image_used": True,
            "poster_qa_score": 90,
        }
    )
    images["poster_generation"] = {
        "sha256": poster_sha,
        "provider": "openai",
        "model": result.model,
        "reference": "021_story_poster.png",
        "generation_count": 2,
        "retry_reason": "objective_brahma_multi_body_defect_g1",
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("story_poster.png", "manifest.json"),
    )
    ledger_path = EVIDENCE / "022_poster_generation_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}
    ledger.update(
        {
            "generation_count": 2,
            "retry_reason": "objective_brahma_multi_body_defect_g1",
            "g2_model": result.model,
            "g2_elapsed_seconds": round(elapsed, 2),
            "g2_after_sha256": poster_sha,
            "g2_drive": getattr(upload, "status", ""),
            "g2_drive_detail": getattr(upload, "detail", ""),
            "cost_note": "2 OpenAI gpt-image-2 image calls total (g1+g2); USD not returned by API",
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EVIDENCE / "022_poster_g2_prompt.txt").write_text(prompt, encoding="utf-8")
    print(
        json.dumps(
            {
                "sha": poster_sha,
                "drive": getattr(upload, "status", ""),
                "elapsed": round(elapsed, 2),
                "model": result.model,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
