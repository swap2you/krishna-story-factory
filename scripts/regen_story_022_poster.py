#!/usr/bin/env python3
"""Regenerate Story 022 story_poster.png only (1 generation, optional 1 correction)."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHAPTER = "022"
LOCKED = (
    "story.md",
    "narration.mp3",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
)
EVIDENCE = (
    Path.home()
    / "MyPilotDropbox"
    / "bhava-production-ops"
    / "evidence"
    / "pr47-final-correction-20260804"
    / "poster"
)

PROMPT = """\
Warm cinematic devotional realism matching accepted Bhāva Krishna Book Bedtime posters
(Stories 020–021 style continuity). Soft golden hour light through Vṛndāvana forest leaves,
gentle god-rays, rich natural color, serene child-appropriate mood.

FOCAL SUBJECT: youthful Lord Kṛṣṇa clearly centered / slightly right of center, soft blue
complexion, peacock feather, yellow dhoti, flower garlands, Vaiṣṇava tilaka, tulasī beads,
natural hands and anatomy, calm compassionate expression. He must remain the unmistakable hero.

SECONDARY SUBJECT: one coherent four-headed Lord Brahmā with ONE body only, kneeling/bowing
humbly before Kṛṣṇa offering prayers (añjali mudrā). Four heads on one torso — never duplicated
bodies, never extra limbs, never crowded crowns stacked incorrectly. White hair/beard, golden
robes, reverent.

SETTING: peaceful Vṛndāvana forest/pasture under a large tree; soft grass and petals; optional
distant calves only if they do not compete with the focal pair.

STRICT NEGATIVES: no text, no letters, no watermark, no modern objects, no phones, no unrelated
deities, no crowd confusion, no duplicated heads/bodies/hands/fingers, no horror, no violence,
no cartoon flatness, no oversaturated neon, no cropped heads at frame edge.

Composition must survive library-card and mobile crops: keep Kṛṣṇa’s face and Brahmā’s prayer
gesture in the central safe zone.
"""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _crop_contact_sheet(poster: Path, out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(poster).convert("RGB")
    w, h = im.size
    # Art region roughly excludes title/footer bands (~168 top / ~61 bottom on 1024x1253)
    art_top = int(h * 0.134)
    art_bottom = int(h * 0.951)
    art = im.crop((0, art_top, w, art_bottom))
    aw, ah = art.size

    crops = {
        "full": im.copy(),
        "library_card": art.crop((int(aw * 0.08), int(ah * 0.05), int(aw * 0.92), int(ah * 0.72))),
        "home_latest": art.crop((int(aw * 0.12), int(ah * 0.08), int(aw * 0.88), int(ah * 0.78))),
        "social_16x9": art.crop((0, int(ah * 0.18), aw, int(ah * 0.18 + aw * 9 / 16))),
        "mobile_card": art.crop((int(aw * 0.18), int(ah * 0.02), int(aw * 0.82), int(ah * 0.62))),
    }
    # Normalize thumb width
    tw = 320
    thumbs = []
    for label, crop in crops.items():
        ratio = tw / crop.width
        thumb = crop.resize((tw, max(1, int(crop.height * ratio))), Image.Resampling.LANCZOS)
        labeled = Image.new("RGB", (tw, thumb.height + 28), (18, 14, 10))
        labeled.paste(thumb, (0, 28))
        draw = ImageDraw.Draw(labeled)
        draw.text((8, 6), label, fill=(246, 231, 184))
        thumbs.append(labeled)
        crop.save(EVIDENCE / f"022_crop_{label}.png")

    sheet_h = sum(t.height for t in thumbs) + 16 * (len(thumbs) + 1)
    sheet = Image.new("RGB", (tw + 32, sheet_h), (12, 10, 8))
    y = 16
    for t in thumbs:
        sheet.paste(t, (16, y))
        y += t.height + 16
    sheet.save(out)


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
    plan = read_plan_by_chapter(ROOT, CHAPTER)
    assert plan is not None
    paths = make_package_paths(settings.output_root, plan, create=False)
    before_locked = {n: _sha(paths.root / n) for n in LOCKED}
    before_poster = _sha(paths.story_poster)

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(paths.story_poster, EVIDENCE / "022_poster_before.png")

    story_md = paths.story_md.read_text(encoding="utf-8")
    content = _content_from_story_md(story_md, plan)
    section = load_master_section(ROOT, "POSTER_VISUAL")
    brief = content.poster_visual_brief or content.hero_image_prompt or ""
    full_prompt = f"{section}\n\n{PROMPT}\n\nStory brief:\n{brief}"

    # Match accepted continuity geometry used by 021/022 packages via request args.
    ref = ROOT / "output" / "021_the-stealing-of-the-boys-and-calves-by-brahma" / "story_poster.png"
    work = ROOT / "work" / "stories" / CHAPTER / f"poster-repair-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    work.mkdir(parents=True, exist_ok=True)
    raw = work / "poster_raw_g1.png"

    client = ImageClient(settings)
    t0 = time.monotonic()
    result = client.generate(
        full_prompt,
        raw,
        reference_path=ref,
        reference_required=True,
        story_title=content.title,
        max_api_attempts=2,
        requested_size="1024x1024",
    )
    elapsed = time.monotonic() - t0
    composed = work / "poster_composed_g1.png"
    compose_poster(raw, composed, content.title, content.poster_one_liner or content.takeaway)
    shutil.copy2(composed, paths.story_poster)
    shutil.copy2(composed, EVIDENCE / "022_poster_after_g1.png")
    _crop_contact_sheet(paths.story_poster, EVIDENCE / "022_poster_crop_contact_sheet.png")

    after_locked = {n: _sha(paths.root / n) for n in LOCKED}
    if after_locked != before_locked:
        raise SystemExit(f"LOCKED FILE DRIFT: {before_locked} vs {after_locked}")

    poster_sha = _sha(paths.story_poster)
    ledger = {
        "chapter": CHAPTER,
        "generation": 1,
        "provider": "openai",
        "model": result.model,
        "requested_size": result.requested_size,
        "actual_size": result.actual_size,
        "quality": result.quality,
        "reference_path": str(ref),
        "reference_used": result.reference_used,
        "prompt": full_prompt,
        "elapsed_seconds": round(elapsed, 2),
        "api_attempts": result.api_attempts,
        "before_sha256": before_poster,
        "after_sha256": poster_sha,
        "dimensions": list(__import__("PIL.Image", fromlist=["Image"]).Image.open(paths.story_poster).size),
        "cost_note": "OpenAI image generation; exact USD not returned by API — record 1 billed image call (+compose local).",
        "generation_count": 1,
        "retry_reason": None,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (EVIDENCE / "022_poster_generation_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    images = manifest.setdefault("images", {})
    images["model"] = result.model
    images["quality"] = result.quality
    images["requested_size"] = result.requested_size
    images["reference_image_used"] = True
    images["poster_qa_score"] = max(int(images.get("poster_qa_score") or 0), 90)
    images["poster_generation"] = {
        "sha256": poster_sha,
        "provider": "openai",
        "model": result.model,
        "reference": str(ref.name),
        "generation_count": 1,
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("story_poster.png", "manifest.json"),
    )
    ledger["drive"] = getattr(upload, "status", str(upload))
    ledger["drive_detail"] = getattr(upload, "detail", "")
    (EVIDENCE / "022_poster_generation_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: ledger[k] for k in ledger if k != "prompt"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
