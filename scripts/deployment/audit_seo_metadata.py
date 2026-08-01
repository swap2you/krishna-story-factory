from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "web" / "app"

# First public release surface: P0/P1 only. Broader marketing/knowledge pages
# inherit root layout metadata and are tracked as P2 content work.
P0_PAGES = {
    "page.tsx": "home",
    "stories/[storyNo]/page.tsx": "story",
    "library/krishna-book/page.tsx": "krishna-book",
    "privacy/page.tsx": "privacy",
    "rights/page.tsx": "rights",
}

failures: list[str] = []

robots = APP / "robots.ts"
sitemap = APP / "sitemap.ts"
layout = APP / "layout.tsx"
seo_lib = ROOT / "apps" / "web" / "lib" / "seo.ts"

for required in (robots, sitemap, layout, seo_lib):
    if not required.is_file():
        failures.append(f"P0 missing SEO file: {required.relative_to(ROOT).as_posix()}")

if layout.is_file():
    layout_text = layout.read_text(encoding="utf-8")
    for token in ("metadataBase", "Organization", "WebSite", "alternates", "openGraph"):
        if token not in layout_text:
            failures.append(f"P0 layout missing {token}")

if sitemap.is_file():
    sitemap_text = sitemap.read_text(encoding="utf-8")
    if "PUBLIC_STORY_MAX" not in sitemap_text:
        failures.append("P0 sitemap must pin Stories via PUBLIC_STORY_MAX")
    if "PUBLIC_STORY_COUNT = 21" in sitemap_text:
        failures.append("P0 sitemap may expose Story 021")

if robots.is_file():
    robots_text = robots.read_text(encoding="utf-8")
    for private_path in ("/studio", "/dev", "/stories/021"):
        if private_path not in robots_text:
            failures.append(f"P0 robots missing disallow for {private_path}")
    if '"/stories/011"' in robots_text or "'/stories/011'" in robots_text:
        failures.append("P0 robots still treats Story 011 as private")

for relative, label in P0_PAGES.items():
    page = APP / Path(relative)
    if not page.is_file():
        failures.append(f"P0 missing page: {relative}")
        continue
    text = page.read_text(encoding="utf-8")
    has_metadata = "generateMetadata" in text or "export const metadata" in text
    # Home may rely on root layout metadata when it sets sitewide defaults.
    if label != "home" and not has_metadata:
        failures.append(f"P1 missing route metadata: {relative}")
    if label == "story":
        for token in ("Article", "AudioObject", "BreadcrumbList", "pageMetadata"):
            if token not in text:
                failures.append(f"P0 story page missing {token}")
        if "PUBLIC_STORY_MAX" not in text:
            failures.append("P0 story page must hard-stop above the public story maximum")
        if "numeric > 10" in text or "Number(padded) > 10" in text:
            failures.append("P0 story page still hard-stops at Story 010")
    # h1 may live in a child component imported by the page.
    if "<h1" not in text and label in {"home", "story"}:
        # Accept child-component heading for composed experiences.
        if label == "story" and "StoryExperience" in text:
            experience = ROOT / "apps" / "web" / "components" / "story-experience.tsx"
            if experience.is_file() and "<h1" not in experience.read_text(encoding="utf-8"):
                failures.append("P1 story experience missing h1")
        elif label == "home":
            failures.append("P1 home page missing h1")

if failures:
    print("\n".join(f"FAIL: {item}" for item in failures))
    raise SystemExit(1)

print("SEO metadata audit passed (P0/P1 public release surface).")
