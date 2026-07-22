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
    identity_consistency_score: int
    issues: list[str]
    hard_rejection: bool
    hard_rejection_reasons: list[str]
    retry_recommended: bool
    raw: dict


def review_image(
    settings: Settings,
    *,
    story_md: str,
    image_path: Path,
    kind: str,
    rubric: str,
    comparison_path: Path | None = None,
) -> VisionReview:
    if not settings.openai_api_key:
        return VisionReview(score=0, identity_consistency_score=0, issues=["OpenAI not configured for vision QA"],
            hard_rejection=True, hard_rejection_reasons=["Vision QA unavailable"], retry_recommended=True, raw={})
    model = settings.openai_visual_qa_model or settings.openai_text_model
    section = load_master_section(settings.project_root, "VISUAL_REVIEW")
    prompt = (
        f"{section}\n\nKIND: {kind}\n\nRUBRIC:\n{rubric}\n\nSTORY.MD:\n{story_md}\n\n"
        "Return strict JSON only: {\"score\": 0, \"identity_consistency_score\": 0, \"issues\": [], "
        "\"hard_rejection\": false, \"hard_rejection_reasons\": [], \"retry_recommended\": false}"
    )
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    image_content = [{"type": "input_image", "image_url": f"data:image/png;base64,{b64}", "detail": "high"}]
    if comparison_path:
        comparison_b64 = base64.b64encode(comparison_path.read_bytes()).decode("ascii")
        image_content.insert(0, {"type": "input_image", "image_url": f"data:image/png;base64,{comparison_b64}", "detail": "high"})
        prompt += "\n\nImage 1 is the approved poster. Image 2 is the generated coloring page. Compare them directly."
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, timeout=120.0, max_retries=0)
    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        *image_content,
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
                        *[{"type": "image_url", "image_url": {"url": item["image_url"], "detail": "high"}} for item in image_content],
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
        identity_consistency_score=int(data.get("identity_consistency_score", score)),
        issues=issues,
        hard_rejection=bool(data.get("hard_rejection", False)),
        hard_rejection_reasons=[str(x) for x in data.get("hard_rejection_reasons", [])],
        retry_recommended=bool(data.get("retry_recommended", score < settings.image_min_acceptance_score)),
        raw=data,
    )


def save_review(work_reviews: Path, name: str, review: VisionReview) -> None:
    work_reviews.mkdir(parents=True, exist_ok=True)
    (work_reviews / f"{name}.json").write_text(
        json.dumps({"score": review.score, "identity_consistency_score": review.identity_consistency_score,
            "issues": review.issues, "hard_rejection": review.hard_rejection,
            "hard_rejection_reasons": review.hard_rejection_reasons, "raw": review.raw}, indent=2),
        encoding="utf-8",
    )


POSTER_RUBRIC = """Score 0-100:
story fidelity 20, facial expression 15, character-role correctness 15, composition 15,
anatomy 10, devotional mood 10, cinematic richness 10, child safety 5.
Reject below 86 for wrong roles, duplicated people, malformed hands, modern objects, cropped elements.
Hard reject a separate visible sky Krishna/Vishnu figure when the story says Krishna remains unseen in the womb;
the sacred presence should be shown as effulgence around Devaki, not a distinct crowned sky deity.
When Brahma is present, he must be clearly four-headed."""

COLORING_RUBRIC = """Score 0-100 by comparing the approved poster with the coloring page:
character identity consistency 25, story accuracy 20, emotional expression 15, coloring usability 15,
composition and safe margins 10, anatomy/object coherence 10, devotional appeal 5.
Explicitly compare character count, identity, approximate age, clothing, role, position, expressions,
story event, and forbidden iconography. Hard reject for a peacock feather on a non-Krishna character,
wrong driver, adults rendered as children, smiling Kamsa during prophecy, missing main character,
duplicated limbs, cropped main figure, wrong deity identity, more than two gray regions, or failure to match poster composition.
Inspect every crown and the space behind it for feather-shaped ornaments; a peacock feather on Vishnu is a hard rejection.
Also return identity_consistency_score in the JSON."""

CHILD_SAFE_DIVERGENT_COLORING_RUBRIC = """Score 0-100 for a child-safe coloring page (ages 4–8):
faithfulness to the coloring visual brief 25, child safety 25, coloring usability 20,
devotional mood 15, anatomy/coherence 10, composition 5.
When the poster is a dramatic persecution/court scene, the coloring page MAY intentionally differ
into a gentler devotee, prison, or family scene. Do NOT hard-reject solely because composition differs
from the dramatic poster. Hard reject only for gore, graphic infant harm, peacock feather on non-Krishna,
duplicated limbs, or unusable line art.
Also return identity_consistency_score in the JSON (roles vs story/coloring brief, not poster clone)."""


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r",\s*}", "}", text)
    cleaned = re.sub(r",\s*]", "]", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return {"score": 0, "issues": ["Vision model did not return JSON"], "retry_recommended": True}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"score": 0, "issues": ["Vision model returned invalid JSON"], "retry_recommended": True}
