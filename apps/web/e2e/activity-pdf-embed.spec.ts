import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("activity PDF embed headers", () => {
  test("activity PDF is inline, application/pdf, and iframe-ready via API headers", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(!stories.length, "No catalog stories available");
    const storyNo = stories[0].story_no;
    const asset = await request.get(`/api/v1/stories/${storyNo}/assets/activity_sheet.pdf`);
    expect(asset.ok()).toBeTruthy();
    expect(asset.headers()["content-type"] || "").toMatch(/application\/pdf/i);
    expect(asset.headers()["content-disposition"] || "").toMatch(/^inline/i);

    const download = await request.get(`/api/v1/stories/${storyNo}/assets/activity_sheet.pdf?download=1`);
    expect(download.ok()).toBeTruthy();
    expect(download.headers()["content-disposition"] || "").toMatch(/^attachment/i);

    await page.goto(`/stories/${storyNo}`);
    await page.getByRole("tab", { name: "Activities" }).click();
    const frame = page.locator('iframe[src*="activity_sheet.pdf"], embed[src*="activity_sheet.pdf"]');
    await expect(frame.first()).toBeVisible();
    await expect(page.getByRole("link", { name: /download pdf/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /open full tab|open.*tab/i }).or(page.getByRole("link", { name: /open/i }))).toBeVisible();
  });
});
