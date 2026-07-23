import { expect, test } from "@playwright/test";

const viewports = [
  { width: 390, height: 844 },
  { width: 430, height: 932 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1366, height: 768 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
];

test.describe("responsive", () => {
  for (const viewport of viewports) {
    test(`${viewport.width}x${viewport.height} home has no horizontal overflow`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto("/");
      const overflow = await page.evaluate(() => {
        const doc = document.documentElement;
        return doc.scrollWidth > doc.clientWidth + 1;
      });
      expect(overflow).toBeFalsy();
      await expect(page.locator("header .wordmark")).toBeVisible();
    });
  }
});
