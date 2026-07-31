import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

/**
 * Stories 001-010 are the governed public release. Story 011+ must remain
 * invisible: no catalog entry, no route, and no teaser text for unreleased titles.
 */
test.describe("public story boundary", () => {
  test("catalog publishes Stories 001-010 only", async ({ request }) => {
    const stories = await fetchStories(request);
    const numbers = stories.map((story) => String(story.story_no).padStart(3, "0"));
    expect(numbers).toEqual([
      "001",
      "002",
      "003",
      "004",
      "005",
      "006",
      "007",
      "008",
      "009",
      "010",
    ]);
  });

  test("Story 011 has no public route", async ({ page }) => {
    for (const path of ["/stories/011", "/stories/11", "/stories/012"]) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} must not be served`).toBe(404);
    }
  });

  test("Story 010 page leaks no unreleased Story 011 content", async ({ page }) => {
    await page.goto("/stories/010");
    await expect(page.getByRole("heading", { name: /Breaks the Cart|Cart/i }).first()).toBeVisible({
      timeout: 20_000,
    });
    await page.getByRole("tab", { name: /Read/i }).click().catch(() => undefined);
    const body = await page.locator("body").innerText();
    expect(body).not.toMatch(/Tṛṇāvarta|Trinavarta|Salvation of/i);
    expect(body).not.toMatch(/Story 011/i);
  });

  test("sitemap lists Stories 001-010 only", async ({ request, baseURL }) => {
    const response = await request.get(`${baseURL}/sitemap.xml`);
    expect(response.ok()).toBeTruthy();
    const xml = await response.text();
    for (let n = 1; n <= 10; n += 1) {
      expect(xml).toContain(`/stories/${String(n).padStart(3, "0")}`);
    }
    expect(xml).not.toMatch(/\/stories\/0*(1[1-9]|[2-9]\d|\d{3,})/);
    for (const priv of ["/studio", "/dev", "/api/studio"]) {
      expect(xml).not.toContain(priv);
    }
  });
});
