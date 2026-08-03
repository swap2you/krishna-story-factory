import { expect, test } from "@playwright/test";

test.describe("Home journey UX", () => {
  test("hero has one primary journey CTA and how-to link", async ({ page }) => {
    await page.goto("/");
    const ctas = page.getByTestId("home-story-primary-ctas");
    await expect(ctas.getByRole("link", { name: /Begin the Krishna Story Journey/i })).toBeVisible();
    await expect(ctas.getByRole("link", { name: /Continue with Story/i })).toBeVisible();
    const primaryLinks = ctas.locator("a");
    expect(await primaryLinks.count()).toBeLessThanOrEqual(2);
    await expect(page.getByRole("link", { name: /See how the weekly story journey works/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Five gentle steps each week/i })).toBeVisible();
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
