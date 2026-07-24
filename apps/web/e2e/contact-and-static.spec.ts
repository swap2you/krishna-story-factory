import { expect, test } from "@playwright/test";

test.describe("contact and static", () => {
  test("contact shows steward name and mailto CTA", async ({ page }) => {
    await page.goto("/contact");
    await expect(page.getByText(/Svarna Gauranga Das/i).first()).toBeVisible();
    await expect(page.locator('a[href^="mailto:svarnagaurangdas"]').first()).toBeVisible();
  });

  test("vanani redirects to prabhupada-vani", async ({ page }) => {
    await page.goto("/vanani", { waitUntil: "networkidle" });
    await expect(page).toHaveURL(/\/prabhupada-vani\/?$/, { timeout: 15_000 });
    await expect(page.getByRole("heading", { name: /Prabhupāda Vāṇī/i }).first()).toBeVisible({ timeout: 15_000 });
  });
});
