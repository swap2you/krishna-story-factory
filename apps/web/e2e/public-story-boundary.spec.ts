import { expect, test } from "@playwright/test";
import { fetchPublicStoryMax, fetchStories, storyNumbers } from "./helpers";

/**
 * Public catalog and routes must match the governed production ceiling from /api/v1/version.
 * The first story above the ceiling must remain invisible: no catalog entry, no route,
 * and no next-preview teaser for unreleased titles.
 */
test.describe("public story boundary", () => {
  test("catalog publishes only released stories through the public ceiling", async ({ request }) => {
    const max = await fetchPublicStoryMax(request);
    const stories = await fetchStories(request);
    const numbers = stories.map((story) => String(story.story_no).padStart(3, "0"));
    expect(numbers).toEqual(storyNumbers(max));
  });

  test("latest released story is public and the next story has no public route", async ({
    page,
    request,
  }) => {
    const max = await fetchPublicStoryMax(request);
    const latest = String(max).padStart(3, "0");
    const next = String(max + 1).padStart(3, "0");
    const ok = await page.goto(`/stories/${latest}`);
    expect(ok?.status(), `/stories/${latest} must be served`).toBe(200);

    for (const path of [
      `/stories/${next}`,
      `/stories/${max + 1}`,
      `/stories/${String(max + 2).padStart(3, "0")}`,
    ]) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} must not be served`).toBe(404);
    }
  });

  test("penultimate story Next Story Preview does not advertise the unreleased successor", async ({
    page,
    request,
  }) => {
    const max = await fetchPublicStoryMax(request);
    if (max < 2) {
      test.skip(true, "Need at least two published stories");
    }
    const penultimate = String(max - 1).padStart(3, "0");
    const next = String(max + 1).padStart(3, "0");
    const reader = await request.get(`/api/v1/stories/${penultimate}/reader`);
    expect(reader.ok()).toBeTruthy();
    const md = await reader.text();
    const idx = md.indexOf("## Next Story Preview");
    expect(idx).toBeGreaterThanOrEqual(0);
    const window = md.slice(idx, idx + 320);
    expect(window).not.toMatch(new RegExp(`Story ${next}`, "i"));

    await page.goto(`/stories/${penultimate}`);
    await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("sitemap lists released stories only through the public ceiling", async ({
    request,
    baseURL,
  }) => {
    const max = await fetchPublicStoryMax(request);
    const next = String(max + 1).padStart(3, "0");
    const response = await request.get(`${baseURL}/sitemap.xml`);
    expect(response.ok()).toBeTruthy();
    const xml = await response.text();
    for (let n = 1; n <= max; n += 1) {
      expect(xml).toContain(`/stories/${String(n).padStart(3, "0")}`);
    }
    expect(xml).not.toContain(`/stories/${next}`);
    expect(xml).not.toContain(`/stories/${String(max + 2).padStart(3, "0")}`);
    for (const priv of ["/studio", "/dev", "/api/studio"]) {
      expect(xml).not.toContain(priv);
    }
  });
});
