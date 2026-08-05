import { expect, test } from "@playwright/test";

test.describe("Home journey UX", () => {
  test("hero shows device-aware CTA and journey chip", async ({ page }) => {
    await page.goto("/");
    const ctas = page.getByTestId("home-story-primary-ctas");
    await expect(ctas.getByRole("link", { name: /Begin with Story 001/i })).toBeVisible();
    await expect(ctas.getByRole("link", { name: /Browse all stories/i })).toBeVisible();
    const primaryLinks = ctas.locator("a");
    expect(await primaryLinks.count()).toBeLessThanOrEqual(2);
    await expect(page.getByTestId("hero-journey-chip")).toBeVisible();
    await expect(page.getByRole("link", { name: /See the five-step family journey/i })).toBeVisible();
    await expect(page.getByText(/Latest published/i)).toHaveCount(0);
    await expect(page.getByRole("heading", { name: /Five gentle steps each week/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Continue the Krishna Book journey/i })).toBeVisible();
  });

  test("Continue CTA appears after visiting a story", async ({ page }) => {
    await page.goto("/stories/001");
    await page.waitForFunction(() => {
      try {
        const raw = localStorage.getItem("bhava:last-story");
        if (!raw) return false;
        const parsed = JSON.parse(raw) as { storyNo?: string };
        return parsed?.storyNo === "001";
      } catch {
        return false;
      }
    });
    await page.goto("/");
    const ctas = page.getByTestId("home-story-primary-ctas");
    await expect(ctas.getByRole("link", { name: /Continue Story 001/i })).toBeVisible();
  });

  test("audience pathway cards replace pills", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Little Listeners" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Young Explorers" })).toBeVisible();
    await expect(page.getByText("Pathway growing").first()).toBeVisible();
    await expect(page.locator(".audience-chips")).toHaveCount(0);
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

test.describe("Post-v4 navigation and footer", () => {
  test("Library two-panel menu opens and switches categories", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/");
    await page.getByRole("button", { name: "Library", exact: true }).click();
    await expect(page.getByRole("button", { name: "Books & Stories" })).toBeVisible();
    await page.getByRole("button", { name: "Prayer & Practice" }).click();
    await expect(page.getByRole("link", { name: /Prayers & Mantras/i })).toBeVisible();
    await expect(page.getByText("Planned").first()).toBeVisible();
  });

  test("story sidebar how-to button has high-contrast styles", async ({ page }) => {
    await page.goto("/stories/001");
    const button = page.locator(".sidebar-how-to");
    await expect(button).toBeVisible();
    const styles = await button.evaluate((el) => {
      const cs = getComputedStyle(el);
      return { color: cs.color, backgroundImage: cs.backgroundImage, minHeight: cs.minHeight };
    });
    expect(styles.color).toMatch(/rgb\(\s*6,\s*22,\s*40\s*\)/);
    expect(styles.backgroundImage).toMatch(/linear-gradient/i);
    expect(Number.parseFloat(styles.minHeight)).toBeGreaterThanOrEqual(44);
    await expect(page.getByRole("link", { name: /How to use these stories/i })).toHaveCount(1);
  });

  test("compact footer trust links and version control", async ({ page }) => {
    await page.goto("/");
    const footer = page.locator("footer.site-footer");
    await expect(footer.getByRole("link", { name: "About" })).toBeVisible();
    await expect(footer.getByRole("link", { name: "Copyright" })).toBeVisible();
    await expect(footer.getByText(/Svarna Gauranga Das \(Swapnil Patil\)/)).toBeVisible();
    await expect(footer.getByRole("link", { name: "Home" })).toHaveCount(0);
    await footer.locator("summary", { hasText: "Version" }).click();
    await expect(footer.locator("dt", { hasText: /^Content$/ })).toBeVisible();
    await expect(footer.locator("dd").filter({ hasText: /bhava-content|001-020|v4|unknown/i }).first()).toBeVisible();
  });
});
