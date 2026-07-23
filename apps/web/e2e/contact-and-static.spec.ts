import { expect, test } from "@playwright/test";

test.describe("contact and static", () => {
  test("contact shows steward name and mailto CTA", async ({ page }) => {
    await page.goto("/contact");
    await expect(page.getByText(/Svarna Gauranga Das/i).first()).toBeVisible();
    await expect(page.locator('a[href^="mailto:svarnagaurangdas"]').first()).toBeVisible();
  });

  test("vanani redirects to prabhupada-vani", async ({ page }) => {
    await page.goto("/vanani");
    await expect(page).toHaveURL(/\/prabhupada-vani\/?$/);
    await expect(page.getByText(/Prabhupāda Vāṇī|timeless instruction/i).first()).toBeVisible();
  });
});
