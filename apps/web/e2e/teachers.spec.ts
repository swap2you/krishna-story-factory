import { expect, test } from "@playwright/test";

test.describe("teachers toolkit", () => {
  test("playlist save and class-pack preview", async ({ page }) => {
    await page.goto("/teachers");
    await page.getByRole("button", { name: /save to classroom playlist/i }).click();
    await expect(page.getByText(/saved to my classroom playlist/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: /my classroom playlist/i })).toBeVisible();
    await expect(page.locator(".playlist-list li").first()).toBeVisible();
    await expect(page.getByRole("heading", { name: /class-pack preview/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /export as text/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /print class-pack preview/i })).toBeVisible();
  });
});
