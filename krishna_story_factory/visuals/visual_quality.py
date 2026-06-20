from __future__ import annotations

from pathlib import Path

from PIL import Image

from .models import VisualPaths


def check_prompt_requirements(prompt: str, *, kind: str) -> list[str]:
    lower = prompt.lower().replace("\u2013", "-").replace("\u2014", "-")
    errors: list[str] = []
    if kind == "line_art":
        required = [
            ("portrait", "portrait"),
            ("ages 6-13", ("ages 6-13", "ages 6", "children ages")),
            ("outline", ("outline", "outlines")),
            ("white background", "white background"),
            ("large colorable spaces", ("large colorable spaces", "colorable spaces")),
            ("expressive faces", ("expressive faces", "expressive")),
            ("safe print margins", ("safe print margins", "safe margins")),
            ("no cropping", ("no cropping", "cropped at page edges")),
            ("no gray shading", ("no gray shading", "no shading", "no color fills")),
            ("no modern objects", "no modern objects"),
            ("central scene", "central scene"),
        ]
    else:
        required = [
            ("portrait poster", "portrait"),
            ("ultra-realistic", ("ultra-realistic", "ultra realistic")),
            ("3d", "3d"),
            ("devotional", "devotional"),
            ("cinematic", "cinematic"),
            ("focal hierarchy", ("focal hierarchy", "clear focal")),
            ("expressive indian faces", ("expressive indian faces", "indian faces")),
            ("ancient indian", ("ancient indian", "historically inspired ancient indian")),
            ("no modern objects", "no modern objects"),
            ("no generated typography", ("do not generate final typography", "no text fragments")),
            ("child-safe", ("child-safe", "child safe")),
            ("central hero scene", ("central hero scene", "central scene")),
        ]
    for label, terms in required:
        if isinstance(terms, str):
            terms = (terms,)
        if not any(term in lower for term in terms):
            errors.append(f"{kind} prompt missing required element: {label}")
    return errors


def score_visual_outputs(paths: VisualPaths, *, line_prompt: str, poster_prompt: str, threshold: int = 80) -> tuple[int, list[str]]:
    issues: list[str] = []
    issues.extend(check_prompt_requirements(line_prompt, kind="line_art"))
    issues.extend(check_prompt_requirements(poster_prompt, kind="poster"))

    checks = [
        (paths.line_art_portrait, "line_art_portrait.png"),
        (paths.coloring_page, "coloring_page.png"),
        (paths.story_poster, "story_poster.png"),
        (paths.coloring_page_print_pdf, "coloring_page_print.pdf"),
    ]
    for path, label in checks:
        if not path.exists() or path.stat().st_size <= 0:
            issues.append(f"Missing or empty file: {label}")

    if paths.line_art_raw.exists() and paths.poster_art_raw.exists():
        if paths.line_art_raw.read_bytes() == paths.poster_art_raw.read_bytes():
            issues.append("Line art and poster raw images are identical.")

    for label, path in (("line_art", paths.line_art_portrait), ("poster", paths.story_poster)):
        if path.exists():
            img = Image.open(path)
            w, h = img.size
            if w > h:
                issues.append(f"{label} should be portrait orientation.")
            if min(w, h) < 1024:
                issues.append(f"{label} short side below 1024px.")
            if label == "line_art":
                gray = img.convert("L")
                avg = sum(gray.get_flattened_data()) / (w * h)
                if avg < 180:
                    issues.append("Line art is too dark for coloring.")

    score = max(0, 100 - len(issues) * 8)
    if score < threshold:
        issues.append(f"Quality score {score} below threshold {threshold}.")
    return score, issues
