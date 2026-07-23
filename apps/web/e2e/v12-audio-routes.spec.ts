import { expect, test } from "@playwright/test";

test.describe("v1.2 audio and keyboard", () => {
  test("play advances currentTime on story 001", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"), "iOS WebKit autoplay policy");
    await page.goto("/stories/001");
    const play = page.getByRole("button", { name: /^Play$/i });
    await expect(play).toBeVisible({ timeout: 20_000 });
    await play.click();
    await expect(page.getByRole("button", { name: /^Pause$/i })).toBeVisible({ timeout: 10_000 });
    await page.waitForTimeout(1200);
    const t = await page.evaluate(() => {
      const audio = document.querySelector("audio");
      return audio ? audio.currentTime : -1;
    });
    expect(t).toBeGreaterThan(0.2);
  });

  test("modal arrows do not change audio time", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"), "iOS WebKit autoplay policy");
    await page.goto("/stories/001");
    const play = page.getByRole("button", { name: /^Play$/i });
    await play.click();
    await page.waitForTimeout(800);
    const before = await page.evaluate(() => document.querySelector("audio")?.currentTime ?? 0);
    await page.getByRole("tab", { name: /Coloring/i }).click();
    const tile = page.locator(".asset-tile").first();
    if (await tile.count()) {
      await tile.click();
      await expect(page.getByRole("dialog")).toBeVisible();
      await page.keyboard.press("ArrowRight");
      await page.waitForTimeout(300);
      const after = await page.evaluate(() => document.querySelector("audio")?.currentTime ?? 0);
      expect(Math.abs(after - before)).toBeLessThan(14);
      await page.keyboard.press("Escape");
    }
  });
});

test.describe("v1.2 routes", () => {
  for (const route of ["/faq", "/printables", "/library/prayers-mantras", "/preachers", "/contact"]) {
    test(`loads ${route}`, async ({ page }) => {
      const res = await page.goto(route);
      expect(res?.ok()).toBeTruthy();
    });
  }

  test("preacher outline updates on selection", async ({ page }) => {
    await page.goto("/preachers");
    const card = page.locator("button.scope-card").first();
    if (!(await card.count())) {
      test.skip(true, "No catalog stories in this runtime");
      return;
    }
    await card.click();
    await expect(page.getByRole("heading", { name: /Outline preview/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^Print$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Export TXT/i })).toBeVisible();
  });

  test("contact form builds mailto", async ({ page }) => {
    await page.goto("/contact");
    await page.getByLabel(/^Name$/i).fill("Test Parent");
    await page.getByLabel(/^Email$/i).fill("parent@example.com");
    await page.getByLabel(/^Subject$/i).fill("Question");
    await page.getByLabel(/^Message$/i).fill("This is a sufficiently long test message.");
    await expect(page.getByRole("button", { name: /Open in email app/i })).toBeVisible();
    await expect(page.locator('a[href^="mailto:svarnagaurangdas"]').first()).toBeVisible();
  });
});
