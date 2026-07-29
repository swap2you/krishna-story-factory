import { expect, test } from "@playwright/test";

test.describe("story sequence preview", () => {
  test("Story 009 Read tab preview resolves to cart-breaking Story 010", async ({ page }) => {
    await page.goto("/stories/009");
    await page.getByRole("tab", { name: /Read/i }).click();
    await expect(page.getByRole("heading", { name: /Next Story Preview/i })).toBeVisible({ timeout: 20_000 });
    const body = await page.locator(".story-main").innerText();
    expect(body).toMatch(/Story 010/i);
    expect(body).toMatch(/Breaks the Cart|cart/i);
    expect(body).not.toMatch(/Salvation of Trinavarta/i);
    expect(body).not.toMatch(/Tṛṇāvarta|Trinavarta/i);
  });

  test("Story 010 remains unpublished placeholder", async ({ page }) => {
    await page.goto("/stories/010");
    await expect(page.getByRole("heading", { level: 1, name: /in preparation/i })).toBeVisible();
    const text = await page.locator("body").innerText();
    expect(text).toMatch(/not published|in preparation/i);
    expect(text).not.toMatch(/Baby Kṛṣṇa Breaks the Cart/);
  });
});
