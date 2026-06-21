from __future__ import annotations

import base64
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from ..config import Settings
from ..prompts_loader import load_master_section

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VisionReview:
    score: int
    issues: list[str]
    retry_recommended: bool
    raw: dict


def review_image(
    settings: Settings,
    *,
    story_md: str,
    image_path: Path,
    kind: str,
    rubric: str,
) -> VisionReview:
    if not settings.openai_api_key:
        return VisionReview(score=0, issues=["OpenAI not configured for vision QA"], retry_recommended=True, raw={})
    model = settings.openai_visual_qa_model or settings.openai_text_model
    section = load_master_section(settings.project_root, "VISUAL_REVIEW")
    prompt = (
        f"{section}\n\nKIND: {kind}\n\nRUBRIC:\n{rubric}\n\nSTORY.MD:\n{story_md}\n\n"
        "Return strict JSON only: {\"score\": 0, \"issues\": [], \"retry_recommended\": false}"
    )
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{b64}", "detail": "high"},
                    ],
                }
            ],
        )
        raw_text = getattr(response, "output_text", "") or ""
    except Exception as exc:
        logger.warning("Vision QA failed (%s); falling back to chat completions", type(exc).__name__)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}},
                    ],
                }
            ],
        )
        raw_text = response.choices[0].message.content or ""
    data = _parse_json(raw_text)
    score = int(data.get("score", 0))
    issues = [str(x) for x in data.get("issues", [])]
    return VisionReview(
        score=score,
        issues=issues,
        retry_recommended=bool(data.get("retry_recommended", score < settings.image_min_acceptance_score)),
        raw=data,
    )


def save_review(work_reviews: Path, name: str, review: VisionReview) -> None:
    work_reviews.mkdir(parents=True, exist_ok=True)
    (work_reviews / f"{name}.json").write_text(
        json.dumps({"score": review.score, "issues": review.issues, "raw": review.raw}, indent=2),
        encoding="utf-8",
    )


POSTER_RUBRIC = """Score 0-100:
story fidelity 20, facial expression 15, character-role correctness 15, composition 15,
anatomy 10, devotional mood 10, cinematic richness 10, child safety 5.
Reject below 86 for wrong roles, duplicated people, malformed hands, modern objects, cropped elements."""

COLORING_RUBRIC = """Score 0-100:
story fidelity 20, emotional expression 20, coloring usability 20, anatomy 15,
composition/safe margins 15, devotional appeal 10.
Reject below 86 for cropped characters, gray areas, faint lines, tiny coloring spaces."""


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"score": 0, "issues": ["Vision model did not return JSON"], "retry_recommended": True}
        return json.loads(match.group(0))
