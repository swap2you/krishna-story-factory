import { expect, test } from "@playwright/test";
import { expectNoCriticalAxe } from "./helpers";

async function studioLogin(page: import("@playwright/test").Page) {
  await page.goto("/studio/knowledge");
  const token = page.getByLabel(/Bootstrap token/i);
  if (await token.count()) {
    await token.fill(process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "bhava-local-studio");
    await page.getByLabel(/Studio role/i).selectOption("steward");
    await page.getByRole("button", { name: /Enter studio/i }).click();
    await expect(page.getByRole("heading", { name: "Roadmap total" })).toBeVisible({
      timeout: 20000,
    });
  }
}

test.describe("P01C knowledge studio foundation", () => {
  test("studio knowledge paginates roadmap beyond 200 and lists package", async ({ page }) => {
    test.skip(process.env.BHAVA_E2E_MODE === "public", "studio routes 404 on public site");
    await studioLogin(page);
    await expect(page.getByText(/Page 1 of/i)).toBeVisible();
    await expect(page.getByRole("link", { name: /P01C Structural Learning-Page Fixture/i })).toBeVisible();
    await expect(
      page.getByText(/mutations, reviewer workflows, scheduling, and publication actions are not implemented/i),
    ).toBeVisible();
  });

  test("private preview renders lenses, keyboard radiogroup, and blocked banner", async ({ page }) => {
    test.skip(process.env.BHAVA_E2E_MODE === "public", "studio routes 404 on public site");
    await studioLogin(page);
    await page.goto("/studio/knowledge/preview/p01c-structural-fixture?lens=explorer");
    await expect(page.getByRole("heading", { name: /P01C Structural Learning-Page Fixture/i })).toBeVisible();
    await expect(page.getByText(/SOURCE_BLOCKED/i).first()).toBeVisible();
    await expect(page.getByText(/TEST FIXTURE/i).first()).toBeVisible();
    const explorer = page.getByRole("radio", { name: "Explorer" });
    await expect(explorer).toBeVisible();
    await explorer.focus();
    await page.keyboard.press("ArrowRight");
    await expect(page.getByRole("radio", { name: "Teen" })).toHaveAttribute("aria-checked", "true");
    await page.getByRole("radio", { name: "Study" }).click();
    await expect(page.getByRole("radio", { name: "Study" })).toHaveAttribute("aria-checked", "true");
    await page.getByRole("button", { name: /Focus mode/i }).click();
    await expect(page.getByRole("button", { name: /Exit focus mode/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Download PDF/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Download DOCX/i })).toBeVisible();
  });

  test("private preview has no serious axe violations and supports reduced motion", async ({ page }) => {
    test.skip(process.env.BHAVA_E2E_MODE === "public", "studio routes 404 on public site");
    await page.emulateMedia({ reducedMotion: "reduce" });
    await studioLogin(page);
    await page.goto("/studio/knowledge/preview/p01c-structural-fixture?lens=explorer");
    await expect(page.getByRole("heading", { name: /P01C Structural Learning-Page Fixture/i })).toBeVisible();
    await expectNoCriticalAxe(page);
  });
});
