import { expect, test } from "@playwright/test";
import { fetchStories } from "./helpers";

test.describe("activity PDF embed headers", () => {
  test("activity PDF is inline, application/pdf, and PDF.js canvas-ready via API headers", async ({ page, request }) => {
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

    const shell = page.locator('[data-pdf-viewer="pdfjs"]');
    await expect(shell).toBeVisible();
    await expect(page.locator('iframe[src*="activity_sheet.pdf"]')).toHaveCount(0);

    const canvas = page.getByTestId("pdfjs-canvas");
    await expect(canvas).toBeVisible({ timeout: 30_000 });
    await expect
      .poll(async () => {
        return canvas.evaluate((el) => {
          const c = el as HTMLCanvasElement;
          return c.width > 0 && c.height > 0;
        });
      }, { timeout: 30_000 })
      .toBeTruthy();

    await expect(page.getByRole("link", { name: /download pdf/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /open full tab|open.*tab/i }).or(page.getByRole("link", { name: /open/i }))).toBeVisible();
  });
});
