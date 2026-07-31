import { expect, test } from "@playwright/test";

test.describe("learning navigation", () => {
  test("desktop Learning opens on click and lists required destinations", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/");
    const learning = page.getByRole("button", { name: /^Learning$/i });
    await expect(learning).toBeVisible();
    await expect(learning).toHaveAttribute("aria-expanded", "false");
    await learning.click();
    await expect(learning).toHaveAttribute("aria-expanded", "true");
    const menu = page.getByRole("group", { name: "Learning links" });
    await expect(menu).toBeVisible();
    for (const label of ["Children & Youth", "Sunday School", "For Teachers", "For Preachers", "Printables"]) {
      await expect(menu.getByRole("link", { name: label })).toBeVisible();
    }
    await page.keyboard.press("Escape");
    await expect(learning).toHaveAttribute("aria-expanded", "false");
  });

  test("desktop Learning opens on hover without relying on overflow clipping", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto("/");
    const learning = page.getByRole("button", { name: /^Learning$/i });
    await learning.hover();
    await expect(learning).toHaveAttribute("aria-expanded", "true");
    await expect(page.getByRole("link", { name: "For Teachers" })).toBeVisible();
    const overflowX = await page.locator("#primary-nav").evaluate((el) => getComputedStyle(el).overflowX);
    expect(overflowX).toBe("visible");
  });

  test("mobile Learning is an inline accordion under the menu", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await page.getByRole("button", { name: /^Menu$/i }).click();
    const learning = page.getByRole("button", { name: /^Learning$/i });
    await learning.click();
    const teachers = page.getByRole("navigation", { name: "Primary navigation" }).getByRole("link", {
      name: "For Teachers",
    });
    await expect(teachers).toBeVisible();
    const box = await teachers.boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
    const position = await page.locator(".nav-learning__menu").evaluate((el) => getComputedStyle(el).position);
    expect(position).toBe("static");
    await teachers.click();
    await expect(page).toHaveURL(/\/teachers/);
  });
});
