import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

/**
 * Stories 001-025 are the governed public release. Story 026+ must remain
 * invisible: no catalog entry, no route, and no next-preview teaser for unreleased titles.
 */
test.describe("public story boundary", () => {
  test("catalog publishes Stories 001-025 only", async ({ request }) => {
    const stories = await fetchStories(request);
    const numbers = stories.map((story) => String(story.story_no).padStart(3, "0"));
    expect(numbers).toEqual(
      Array.from({ length: 25 }, (_, index) => String(index + 1).padStart(3, "0")),
    );
  });

  test("Story 025 is public and Story 026 has no public route", async ({ page }) => {
    const ok = await page.goto("/stories/025");
    expect(ok?.status(), "/stories/025 must be served").toBe(200);

    for (const path of ["/stories/026", "/stories/26", "/stories/027"]) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} must not be served`).toBe(404);
    }
  });

  test("Story 025 Next Story Preview does not advertise Story 026", async ({ page, request }) => {
    const reader = await request.get("/api/v1/stories/025/reader");
    expect(reader.ok()).toBeTruthy();
    const md = await reader.text();
    const idx = md.indexOf("## Next Story Preview");
    expect(idx).toBeGreaterThanOrEqual(0);
    const window = md.slice(idx, idx + 320);
    expect(window).not.toMatch(/Story 026/i);

    await page.goto("/stories/025");
    await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("sitemap lists Stories 001-025 only", async ({ request, baseURL }) => {
    const response = await request.get(`${baseURL}/sitemap.xml`);
    expect(response.ok()).toBeTruthy();
    const xml = await response.text();
    for (let n = 1; n <= 25; n += 1) {
      expect(xml).toContain(`/stories/${String(n).padStart(3, "0")}`);
    }
    expect(xml).not.toContain("/stories/026");
    expect(xml).not.toContain("/stories/027");
    for (const priv of ["/studio", "/dev", "/api/studio"]) {
      expect(xml).not.toContain(priv);
    }
  });
});
