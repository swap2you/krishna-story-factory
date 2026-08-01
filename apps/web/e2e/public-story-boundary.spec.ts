import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

/**
 * Stories 001-020 are the governed public release. Story 021+ must remain
 * invisible: no catalog entry, no route, and no next-preview teaser for unreleased titles.
 */
test.describe("public story boundary", () => {
  test("catalog publishes Stories 001-020 only", async ({ request }) => {
    const stories = await fetchStories(request);
    const numbers = stories.map((story) => String(story.story_no).padStart(3, "0"));
    expect(numbers).toEqual(
      Array.from({ length: 20 }, (_, index) => String(index + 1).padStart(3, "0")),
    );
  });

  test("Story 021 has no public route", async ({ page }) => {
    for (const path of ["/stories/021", "/stories/21", "/stories/022"]) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} must not be served`).toBe(404);
    }
  });

  test("Story 020 Next Story Preview does not advertise Story 021", async ({ page, request }) => {
    const reader = await request.get("/api/v1/stories/020/reader");
    expect(reader.ok()).toBeTruthy();
    const md = await reader.text();
    const idx = md.indexOf("## Next Story Preview");
    expect(idx).toBeGreaterThanOrEqual(0);
    const window = md.slice(idx, idx + 320);
    expect(window).not.toMatch(/Story 021/i);
    expect(window).not.toMatch(/Brahmā|Brahma steals|stealing of the boys/i);

    await page.goto("/stories/020");
    await expect(page.getByRole("heading", { name: /Aghasura|Aghāsura|Protects Everyone/i }).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("sitemap lists Stories 001-020 only", async ({ request, baseURL }) => {
    const response = await request.get(`${baseURL}/sitemap.xml`);
    expect(response.ok()).toBeTruthy();
    const xml = await response.text();
    for (let n = 1; n <= 20; n += 1) {
      expect(xml).toContain(`/stories/${String(n).padStart(3, "0")}`);
    }
    expect(xml).not.toContain("/stories/021");
    expect(xml).not.toContain("/stories/022");
    for (const priv of ["/studio", "/dev", "/api/studio"]) {
      expect(xml).not.toContain(priv);
    }
  });
});
