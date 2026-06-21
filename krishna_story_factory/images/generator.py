from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import Settings
from ..models import StoryContent
from ..prompts_loader import load_master_section
from .client import ImageClient
from .vision_qa import COLORING_RUBRIC, POSTER_RUBRIC, review_image, save_review


def generate_poster(
    settings: Settings,
    *,
    story_md: str,
    content: StoryContent,
    output_path: Path,
    work_candidates: Path,
    work_reviews: Path,
    mode: str = "prod",
) -> tuple[int, bool]:
    if mode == "test" or not settings.openai_image_enabled:
        _placeholder_poster(output_path, content.title, content.poster_one_liner or content.takeaway)
        return 90, False
    client = ImageClient(settings)
    ref = settings.image_reference_poster
    ref_used = bool(ref and ref.exists())
    if not ref_used:
        import logging

        logging.getLogger(__name__).warning("Poster reference image not found; continuing without reference.")
    section = load_master_section(settings.project_root, "POSTER_VISUAL")
    base_prompt = f"{section}\n\n{content.poster_visual_brief or content.hero_image_prompt or content.image_prompt}"
    best_score = 0
    best_path: Path | None = None
    rounds = settings.image_max_repair_rounds + 1
    candidates_n = max(2, settings.image_candidates_per_type)
    prompt = base_prompt
    for round_idx in range(rounds):
        for idx in range(candidates_n):
            cand = work_candidates / f"poster_r{round_idx}_c{idx}.png"
            client.generate(prompt, cand, reference_path=ref if ref_used else None)
            review = review_image(settings, story_md=story_md, image_path=cand, kind="poster", rubric=POSTER_RUBRIC)
            save_review(work_reviews, f"poster_r{round_idx}_c{idx}", review)
            if review.score > best_score:
                best_score = review.score
                best_path = cand
            if review.score >= settings.image_min_acceptance_score:
                best_path = cand
                best_score = review.score
                break
        if best_score >= settings.image_min_acceptance_score and best_path:
            break
        prompt = f"{base_prompt}\n\nREPAIR: Fix these issues from vision review: {review.issues[:5]}"
    if not best_path:
        raise RuntimeError("No poster candidate generated.")
    compose_poster(best_path, output_path, content.title, content.poster_one_liner or content.takeaway)
    if best_score < settings.image_min_acceptance_score:
        raise RuntimeError(f"Poster vision score {best_score} below threshold {settings.image_min_acceptance_score}.")
    return best_score, ref_used


def generate_coloring(
    settings: Settings,
    *,
    story_md: str,
    content: StoryContent,
    output_path: Path,
    work_candidates: Path,
    work_reviews: Path,
    poster_path: Path,
    mode: str = "prod",
    max_candidates: int | None = None,
) -> tuple[int, bool, bool, int]:
    if mode == "test" or not settings.openai_image_enabled:
        _placeholder_coloring(output_path, content.title)
        return 90, True, False, 90
    client = ImageClient(settings)
    if not poster_path.exists():
        raise RuntimeError(f"Approved story poster is required for coloring generation: {poster_path}")
    work_candidates.mkdir(parents=True, exist_ok=True)
    work_reviews.mkdir(parents=True, exist_ok=True)
    style_ref = settings.image_reference_line_art
    style_ref_used = bool(style_ref and style_ref.exists())
    section = load_master_section(settings.project_root, "COLORING_VISUAL")
    base_prompt = f"{section}\n\n{_identity_constraints(content.title)}\n\n{content.coloring_visual_brief or content.line_art_prompt or content.coloring_page_prompt}"
    acceptance_score = max(90, settings.image_min_acceptance_score)
    candidate_limit = max_candidates or min(3, settings.image_max_repair_rounds + 1)
    prompt = base_prompt
    last_review = None
    for candidate_idx in range(candidate_limit):
        cand = work_candidates / f"coloring_candidate_{candidate_idx + 1}.png"
        client.generate(
            prompt, cand, reference_path=poster_path, reference_required=True,
            style_reference_path=style_ref if style_ref_used else None,
            story_title=content.title, max_api_attempts=2, requested_size="1024x1536",
        )
        cleaned = work_candidates / f"coloring_candidate_{candidate_idx + 1}_clean.png"
        _clean_line_art(cand, cleaned)
        review = review_image(
            settings, story_md=story_md, image_path=cleaned, kind="coloring",
            rubric=COLORING_RUBRIC, comparison_path=poster_path,
        )
        save_review(work_reviews, f"coloring_candidate_{candidate_idx + 1}", review)
        last_review = review
        accepted = (
            review.score >= acceptance_score
            and review.identity_consistency_score >= 90
            and not review.hard_rejection
        )
        if accepted:
            cleaned.replace(output_path)
            return review.score, True, style_ref_used, review.identity_consistency_score
        repair_reasons = review.hard_rejection_reasons + review.issues
        prompt = f"{base_prompt}\n\nREPAIR: Fix these issues: {repair_reasons[:8]}"

    if last_review is None:
        raise RuntimeError("No coloring candidate generated.")
    raise RuntimeError(
        "COLORING_QA_FAILED: "
        f"score={last_review.score}, identity={last_review.identity_consistency_score}, "
        f"hard_rejection={last_review.hard_rejection}, issues={last_review.hard_rejection_reasons + last_review.issues}"
    )


def _identity_constraints(title: str) -> str:
    universal = """IDENTITY RULES: Only Krishna may wear a peacock feather or be associated with a flute. Ordinary humans have two arms. No random halos, unrelated deity symbols, childlike adult faces, or identical faces. Vishnu has four arms only when explicitly shown; Brahma has multiple heads only when explicitly shown."""
    if "Earth Prays" in title:
        return universal + " Mother Earth is a gentle sacred cow with devotional expression. Brahma leads the prayer. Vishnu, Brahma, and supporting demigods must remain distinct; do not crowd the scene. Vishnu must have NO peacock feather, feather plume, or feather-shaped ornament on, beside, or behind His crown."
    if "Wedding" in title or "Heavenly Voice" in title:
        return universal + " Devaki is an adult royal bride; Vasudeva is an adult noble bridegroom, calm and protective; Kamsa is an adult warrior prince driving the chariot, shocked and fearful. Devaki and Vasudeva sit behind him. No peacock feathers, Krishna-like crowns, toddler faces, or cheerful Kamsa."
    return universal


def compose_poster(raw_path: Path, output_path: Path, title: str, one_liner: str) -> None:
    base = Image.open(raw_path).convert("RGB")
    width, height = base.size
    title_band = max(int(height * 0.08), 72)
    footer_band = max(int(height * 0.06), 56)
    canvas = Image.new("RGB", (width, height + title_band + footer_band), "#120c06")
    canvas.paste(base, (0, title_band))
    draw = ImageDraw.Draw(canvas)
    title_font = _font(42)
    body_font = _font(24)
    margin = int(width * 0.06)
    max_w = width - margin * 2
    y = 16
    for line in _wrap(draw, title, title_font, max_w)[:2]:
        draw.text((width // 2, y), line, font=title_font, fill="#f6e7b8", anchor="ma")
        y += title_font.size + 4
    footer_y = height + title_band + 14
    for line in _wrap(draw, one_liner, body_font, max_w)[:2]:
        draw.text((width // 2, footer_y), line, font=body_font, fill="#efe2c0", anchor="ma")
        footer_y += body_font.size + 4
    canvas.save(output_path, "PNG")


def _clean_line_art(src: Path, dest: Path) -> None:
    from PIL import ImageOps

    img = Image.open(src).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    bw = img.point(lambda p: 255 if p > 210 else (0 if p < 120 else p)).convert("RGB")
    bw.save(dest, "PNG")


def _font(size: int):
    for name in ("Segoe UI Bold", "Arial Bold", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    if not text.strip():
        return []
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _placeholder_poster(output_path: Path, title: str, one_liner: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    raw = output_path.with_suffix(".raw.png")
    img = Image.new("RGB", (1024, 1536), "#1a1208")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((512, 700), title[:50], fill="#f6e7b8", anchor="ma", font=font)
    img.save(raw)
    compose_poster(raw, output_path, title, one_liner)
    raw.unlink(missing_ok=True)


def _placeholder_coloring(output_path: Path, title: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1024, 1536), "white")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((80, 160, 944, 1380), radius=24, outline="black", width=4)
    font = ImageFont.load_default()
    draw.text((512, 760), title[:40], fill="black", anchor="ma", font=font)
    img.save(output_path, "PNG")
