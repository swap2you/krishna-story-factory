import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("notes and bookmarks", () => {
  test("saves story-isolated notes", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(stories.length < 1, "No catalog stories available");
    const storyNo = stories[0].story_no;
    await page.goto(`/stories/${storyNo}`);
    await page.getByRole("tab", { name: "Notes" }).click();
    const note = `UAT note ${Date.now()}`;
    await page.locator("textarea.notes").fill(note);
    await page.getByRole("button", { name: /save notes/i }).click();
    await expect(page.getByText(/notes saved/i)).toBeVisible();
    await page.reload();
    await page.getByRole("tab", { name: "Notes" }).click();
    await expect(page.locator("textarea.notes")).toHaveValue(note);
  });
});
