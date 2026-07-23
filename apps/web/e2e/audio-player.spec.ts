import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("audio player", () => {
  test("exposes playback controls per story", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(!stories.length, "No catalog stories available");
    await page.goto(`/stories/${stories[0].story_no}`);
    await page.getByRole("tab", { name: "Listen" }).click();
    await expect(page.getByRole("button", { name: "Play" })).toBeVisible();
    await expect(page.getByLabel("Playback speed")).toBeVisible();
  });
});
