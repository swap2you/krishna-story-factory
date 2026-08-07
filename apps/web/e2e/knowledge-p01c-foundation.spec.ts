import { expect, test } from "@playwright/test";

test.describe("P01C knowledge studio foundation", () => {
  test("studio knowledge paginates roadmap beyond 200 and lists package", async ({ page }) => {
    test.skip(process.env.BHAVA_E2E_MODE === "public", "studio routes 404 on public site");
    await page.goto("/studio/knowledge");
    // bootstrap if login form present
  const token = page.getByLabel(/Bootstrap token/i);
    if (await token.count()) {
      await token.fill(process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "bhava-local-studio");
      await page.getByLabel(/Studio role/i).selectOption("steward");
      await page.getByRole("button", { name: /Enter studio/i }).click();
    }
    await expect(page.getByText(/Roadmap total/i)).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/Page 1 of/i)).toBeVisible();
    await expect(page.getByRole("link", { name: /P01C Structural Learning-Page Fixture/i })).toBeVisible();
  });

  test("private preview renders lenses and blocked banner", async ({ page }) => {
    test.skip(process.env.BHAVA_E2E_MODE === "public", "studio routes 404 on public site");
    await page.goto("/studio/knowledge");
  const token = page.getByLabel(/Bootstrap token/i);
    if (await token.count()) {
      await token.fill(process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "bhava-local-studio");
      await page.getByLabel(/Studio role/i).selectOption("steward");
      await page.getByRole("button", { name: /Enter studio/i }).click();
    }
    await page.goto("/studio/knowledge/preview/p01c-structural-fixture?lens=explorer");
    await expect(page.getByRole("heading", { name: /P01C Structural Learning-Page Fixture/i })).toBeVisible();
    await expect(page.getByText(/SOURCE_BLOCKED/i).first()).toBeVisible();
    await expect(page.getByText(/TEST FIXTURE/i).first()).toBeVisible();
    await expect(page.getByRole("radio", { name: "Explorer" })).toBeVisible();
    await page.getByRole("radio", { name: "Study" }).click();
    await expect(page.getByRole("radio", { name: "Study" })).toHaveAttribute("aria-checked", "true");
    await page.getByRole("button", { name: /Focus mode/i }).click();
    await expect(page.getByRole("button", { name: /Exit focus mode/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Download PDF/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Download DOCX/i })).toBeVisible();
  });
});
