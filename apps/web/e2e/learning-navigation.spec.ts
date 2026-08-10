import { expect, test, type Page } from "@playwright/test";

async function openPrimaryNavIfNeeded(page: Page) {
  const menu = page.getByRole("button", { name: /^Menu$/i });
  if (await menu.isVisible().catch(() => false)) {
    await menu.click();
  }
}

async function isMobileLearning(page: Page) {
  return page.evaluate(() => {
    const el = document.querySelector(".nav-learning--mobile");
    return !!el && getComputedStyle(el).display !== "none";
  });
}

function learningButton(page: Page) {
  return page
    .getByRole("navigation", { name: "Primary navigation" })
    .getByRole("button", { name: /^Learning$/i });
}

function learningLinks(page: Page, mobile: boolean) {
  return mobile
    ? page.locator(".nav-learning--mobile .nav-learning__menu")
    : page.locator(".nav-learning--desktop .nav-learning__menu");
}

test.describe("learning navigation", () => {
  test("Learning opens on click and lists required destinations", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const learning = learningButton(page);
    await expect(learning).toBeVisible();
    await expect(learning).toHaveAttribute("aria-expanded", "false");
    await learning.click();
    await expect(learning).toHaveAttribute("aria-expanded", "true");
    const menu = learningLinks(page, mobile);
    await expect(menu).toBeVisible();
    for (const label of [
      "Learning Hub",
      "Children & Youth",
      "Families",
      "Sunday School",
      "For Teachers",
      "For Preachers",
      "Gurukula / Homeschool",
      "Festival use",
      "Printables",
    ]) {
      await expect(menu.getByRole("link", { name: label })).toBeVisible();
    }
    await page.keyboard.press("Escape");
    await expect(learning).toHaveAttribute("aria-expanded", "false");
  });

  test("desktop Learning opens on hover without relying on overflow clipping", async ({ page }, testInfo) => {
    test.skip(!/desktop/i.test(testInfo.project.name), "Hover enhancement is desktop-only");
    await page.goto("/");
    const fineHover = await page.evaluate(
      () => window.matchMedia("(hover: hover) and (pointer: fine)").matches,
    );
    test.skip(!fineHover, "Browser/project does not advertise fine hover");

    const learning = learningButton(page);
    await page.locator(".nav-learning--desktop").hover();
    await expect(learning).toHaveAttribute("aria-expanded", "true");
    const menu = learningLinks(page, false);
    await expect(menu.getByRole("link", { name: "For Teachers" })).toBeVisible();
    const overflowX = await page.locator("#primary-nav").evaluate((el) => getComputedStyle(el).overflowX);
    expect(["visible", "clip"].includes(overflowX)).toBeTruthy();
  });

  test("mobile Learning is an inline accordion under the menu", async ({ page }, testInfo) => {
    test.skip(!/mobile/i.test(testInfo.project.name), "Accordion layout is mobile viewport");
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const learning = learningButton(page);
    await learning.click();
    const menu = learningLinks(page, true);
    const teachers = menu.getByRole("link", { name: "For Teachers" });
    await expect(teachers).toBeVisible();
    const box = await teachers.boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
    const position = await menu.evaluate((el) => getComputedStyle(el).position);
    expect(position).toBe("static");
    await teachers.click();
    await expect(page).toHaveURL(/\/teachers/);
  });
});
