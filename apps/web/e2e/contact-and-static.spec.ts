import { expect, test } from "@playwright/test";

test.describe("contact and static", () => {
  test("contact explains steward identity", async ({ page }) => {
    await page.goto("/contact");
    await expect(page.getByText(/devotional name of Swapnil Patil/i)).toBeVisible();
  });

  test("vanani redirects to prabhupada-vani", async ({ page }) => {
    await page.goto("/vanani");
    await expect(page).toHaveURL(/\/prabhupada-vani\/?$/);
    await expect(page.getByText(/Prabhupāda Vāṇī|timeless instruction/i).first()).toBeVisible();
  });
});
