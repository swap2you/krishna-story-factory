import { expect, test } from "@playwright/test";

test.describe("Home journey UX", () => {
  test("hero shows device-aware CTA (Begin with Story 001 when no progress)", async ({ page }) => {
    await page.goto("/");
    const ctas = page.getByTestId("home-story-primary-ctas");
    await expect(ctas.getByRole("link", { name: /Begin with Story 001/i })).toBeVisible();
    await expect(ctas.getByRole("link", { name: /Browse all stories/i })).toBeVisible();
    const primaryLinks = ctas.locator("a");
    expect(await primaryLinks.count()).toBeLessThanOrEqual(2);
    await expect(page.getByRole("link", { name: /How the weekly journey works/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Five gentle steps each week/i })).toBeVisible();
  });

  test("Continue CTA appears after visiting a story", async ({ page }) => {
    await page.goto("/stories/001");
    await page.waitForTimeout(500);
    await page.goto("/");
    const ctas = page.getByTestId("home-story-primary-ctas");
    await expect(ctas.getByRole("link", { name: /Continue Story 001/i })).toBeVisible();
  });

  test("how-to-use page renders five stages and sitemap entry", async ({ page, request }) => {
    await page.goto("/library/krishna-book/how-to-use");
    await expect(page.getByRole("heading", { name: /How to use Krishna Book stories/i })).toBeVisible();
    for (const title of ["Listen tonight", "Read tomorrow", "Create and color", "Read the source", "Reflect and share"]) {
      await expect(page.getByRole("heading", { name: title })).toBeVisible();
    }
    await expect(page.locator(".how-to-storyboard svg").first()).toBeVisible();

    const sitemap = await request.get("/sitemap.xml");
    expect(sitemap.ok()).toBeTruthy();
    const body = await sitemap.text();
    expect(body).toContain("/library/krishna-book/how-to-use");
  });
});
