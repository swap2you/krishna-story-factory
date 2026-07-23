import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("pdf and images", () => {
  test("activity PDF and coloring lightbox work", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(!stories.length, "No catalog stories available");
    await page.goto(`/stories/${stories[0].story_no}`);

    await page.getByRole("tab", { name: "Activities" }).click();
    await expect(page.getByRole("link", { name: /download pdf/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^print$/i })).toBeVisible();

    await page.getByRole("tab", { name: "Coloring" }).click();
    const tile = page.locator(".asset-tile").first();
    await expect(tile).toBeVisible();
    await tile.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);
  });
});
