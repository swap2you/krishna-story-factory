import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("stories", () => {
  test("lists every discovered story and opens each detail page", async ({ page, request }) => {
    const stories = await fetchStories(request);
    expect(stories.length).toBeGreaterThan(0);

    await page.goto("/library/krishna-book");
    await expect(page.getByRole("heading", { name: /chapter timeline/i })).toBeVisible();
    await expect(page.locator(".story-card").first()).toBeVisible({ timeout: 15_000 });
    await expect(page.locator(".story-card")).toHaveCount(stories.length);

    for (const story of stories) {
      const response = await page.goto(`/stories/${story.story_no}`);
      expect(response?.ok()).toBeTruthy();
      await expect(page.getByRole("heading", { level: 1 }).first()).toContainText(story.title);
    }
  });
});
