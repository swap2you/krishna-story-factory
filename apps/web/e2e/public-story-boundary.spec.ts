import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

/**
 * Stories 001-009 are the governed public release. Story 010 exists on the
 * operator workstation but must be invisible to the site: no catalog entry, no
 * route, and no teaser text quoting its title. The former "Next Story Preview"
 * band was removed for exactly this reason.
 */
test.describe("public story boundary", () => {
  test("catalog publishes Stories 001-009 only", async ({ request }) => {
    const stories = await fetchStories(request);
    const numbers = stories.map((story) => String(story.story_no).padStart(3, "0"));
    expect(numbers).toEqual(["001", "002", "003", "004", "005", "006", "007", "008", "009"]);
  });

  test("Story 010 has no public route", async ({ page }) => {
    for (const path of ["/stories/010", "/stories/10", "/stories/011"]) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} must not be served`).toBe(404);
    }
  });

  test("Story 009 page leaks no unreleased Story 010 content", async ({ page }) => {
    await page.goto("/stories/009");
    await expect(page.getByRole("heading", { name: /Pūtanā/i }).first()).toBeVisible({ timeout: 20_000 });
    await page.getByRole("tab", { name: /Read/i }).click().catch(() => undefined);
    const body = await page.locator("body").innerText();
    expect(body).not.toMatch(/Breaks the Cart/i);
    expect(body).not.toMatch(/Tṛṇāvarta|Trinavarta/i);
    expect(body).not.toMatch(/Story 010/i);
  });

  test("sitemap lists Stories 001-009 only", async ({ request, baseURL }) => {
    const response = await request.get(`${baseURL}/sitemap.xml`);
    expect(response.ok()).toBeTruthy();
    const xml = await response.text();
    for (let n = 1; n <= 9; n += 1) {
      expect(xml).toContain(`/stories/${String(n).padStart(3, "0")}`);
    }
    expect(xml).not.toMatch(/\/stories\/0*(1[0-9]|[1-9]\d\d)/);
    for (const priv of ["/studio", "/dev", "/api/studio"]) {
      expect(xml).not.toContain(priv);
    }
  });
});
