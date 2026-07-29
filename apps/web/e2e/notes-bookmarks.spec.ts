import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("notes and bookmarks", () => {
  test("saves story-isolated notes", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(stories.length < 1, "No catalog stories available");
    const storyNo = stories[0].story_no;
    await page.goto(`/stories/${storyNo}`);
    const notesTab = page.getByRole("tab", { name: /Notes/i });
    await notesTab.scrollIntoViewIfNeeded();
    await notesTab.click();
    await expect(notesTab).toHaveAttribute("aria-selected", "true", { timeout: 10_000 });
    const area = page.getByRole("tabpanel").locator("textarea").first();
    await expect(area).toBeVisible({ timeout: 15_000 });
    const note = `UAT note ${Date.now()}`;
    await area.fill(note);
    const save = page.getByRole("button", { name: /save notes/i });
    if (await save.isVisible().catch(() => false)) {
      await save.click();
      await expect(
        page.getByText(/notes saved|saved on this device/i).first(),
      ).toBeVisible({ timeout: 15_000 });
    }
    await page.reload();
    await notesTab.scrollIntoViewIfNeeded();
    await page.getByRole("tab", { name: /Notes/i }).click();
    await expect(page.getByRole("tabpanel").locator("textarea").first()).toHaveValue(note);
  });
});
