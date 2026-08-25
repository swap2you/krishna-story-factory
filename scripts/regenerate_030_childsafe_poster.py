"""Regenerate only Story 030 story_poster.png with child-safe constraints. No audio."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from krishna_story_factory.config import load_settings  # noqa: E402
from krishna_story_factory.images.client import ImageClient  # noqa: E402
from krishna_story_factory.images.generator import compose_poster  # noqa: E402
from krishna_story_factory.images.vision_qa import review_image, save_review  # noqa: E402

PKG = next((ROOT / "output").glob("030_*"))
WORK = ROOT / "work" / "_030_poster_childsafe"
TITLE = "Stealing the Garments of the Unmarried Gopi Girls"
ONE_LINER = "Krishna returns the garments from the kadamba tree by the Yamunā."

CHILD_SAFE_RUBRIC = """
Score 0-100 for a CHILD-SAFE Story 030 poster (ages 6–12).
Award points for: Krishna fully clothed in kadamba tree (20), returned cloth bundles on the branch (15),
Yamunā with lotuses/reeds (20), distant fully clothed/concealed figures OR landscape-only waterline (25),
gentle family-friendly mood (10), no text in art (10).
HARD REJECT (hard_rejection=true, score<=20) if ANY: bare backs, exposed bodies, bathing undress,
suggestive anatomy, garment-focused framing of undressed figures, or close-ups of bodies in water.
Prefer distant modest figures among reeds over close waterline figures.
""".strip()

CHILD_SAFE_PROMPT = """
Create a gentle family-friendly Krishna Book illustration for children ages 6–12.

Scene:
- Young blue Krishna, fully dressed in bright yellow dhoti and flower garlands, sits high in a leafy kadamba tree.
- Neatly folded colorful cloth bundles rest on the branch beside Him (simple laundry-like cloth piles).
- Below: calm Yamuna river with pink lotus flowers, lily pads, morning mist, and tall reeds filling the foreground.
- At a far distance near the reed bank, small fully dressed village figures in modest sarees stand among reeds, tiny in the frame, mostly hidden by lotus leaves and distance.
- Emphasize landscape: tree, river, lotuses, reeds, soft light. Keep people small and modest.

Style: reverent cartoon-realism, soft greens and blues, peaceful morning devotion, vertical portrait composition, no text or letters in the image.
""".strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    settings = load_settings(ROOT)
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY required to regenerate Story 030 poster")
    WORK.mkdir(parents=True, exist_ok=True)
    cands = WORK / "candidates"
    reviews = WORK / "reviews"
    cands.mkdir(exist_ok=True)
    reviews.mkdir(exist_ok=True)

    existing = sorted(cands.glob("raw_*.png"))
    client = ImageClient(settings)
    story_md = (PKG / "story.md").read_text(encoding="utf-8")
    best_path = None
    best_score = -1
    best_review = None

    # Prefer already-generated candidates first (avoid extra paid calls).
    paths = list(existing) if existing else []
    if not paths:
        for idx in range(3):
            cand = cands / f"raw_{idx}.png"
            client.generate(
                CHILD_SAFE_PROMPT,
                cand,
                story_title="Krishna by the kadamba tree",
                requested_size="1024x1536",
            )
            paths.append(cand)

    for cand in paths:
        review = review_image(
            settings,
            story_md=story_md,
            image_path=cand,
            kind="poster",
            rubric=CHILD_SAFE_RUBRIC,
        )
        save_review(reviews, f"childsafe_{cand.stem}", review)
        print(
            f"{cand.name}: score={review.score} hard_reject={review.hard_rejection} "
            f"issues={review.issues[:2]}"
        )
        if review.hard_rejection:
            continue
        if review.score > best_score:
            best_score = review.score
            best_path = cand
            best_review = review

    if best_path is None:
        raise SystemExit("No child-safe poster candidate passed vision hard-reject gate")
    if best_score < 70:
        raise SystemExit(f"Best poster score {best_score} below 70")

    out = PKG / "story_poster.png"
    compose_poster(best_path, out, TITLE, ONE_LINER)
    poster_sha = sha(out)
    print(f"wrote {out} sha={poster_sha} score={best_score}")

    evidence = {
        "story_no": "030",
        "poster_sha256": poster_sha,
        "vision_score": best_score,
        "hard_rejection": bool(best_review.hard_rejection) if best_review else None,
        "issues": list(best_review.issues) if best_review else [],
        "selected_candidate": best_path.name,
        "prompt_sha256": hashlib.sha256(CHILD_SAFE_PROMPT.encode()).hexdigest().upper(),
    }
    (WORK / "poster_evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
