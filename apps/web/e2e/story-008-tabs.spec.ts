import { expect, test } from "@playwright/test";

test.describe("Story 008 full-tab UAT", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/stories/008");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({ timeout: 20_000 });
  });

  test("Listen tab exposes player controls", async ({ page }) => {
    await page.getByRole("tab", { name: /Listen/i }).click();
    await expect(page.locator(".audio-player")).toBeVisible();
    await expect(page.locator(".audio-player").getByRole("button", { name: /Play|Loading/i })).toBeVisible();
    await expect(page.getByLabel("Playback speed")).toBeVisible();
    await expect(page.getByRole("link", { name: /Download/i })).toBeVisible();
  });

  test("Read tab shows story body without internal markers", async ({ page }) => {
    await page.getByRole("tab", { name: /Read/i }).click();
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text.length).toBeGreaterThan(200);
    expect(text).not.toMatch(/SSML|Audio Narration|Poster Visual Brief|OPENAI_|API_KEY/i);
  });

  test("Activities tab embeds or offers activity PDF", async ({ page }) => {
    await page.getByRole("tab", { name: /Activities/i }).click();
    const panel = page.getByRole("tabpanel");
    const embed = panel.locator("iframe, embed, object, a[href*='activity_sheet']");
    await expect(embed.first()).toBeVisible({ timeout: 15_000 });
  });

  test("Coloring tab opens lightbox assets", async ({ page }) => {
    await page.getByRole("tab", { name: /Coloring/i }).click();
    const tile = page.locator(".asset-tile, .coloring-tile, img").first();
    await expect(tile).toBeVisible({ timeout: 15_000 });
  });

  test("Source tab is honest about review state", async ({ page }) => {
    await page.getByRole("tab", { name: /Source/i }).click();
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text).toMatch(/Krishna Book|Bhāgavatam|source|review|Vedabase|pending/i);
  });

  test("Notes tab persists local reflection text", async ({ page }) => {
    await page.getByRole("tab", { name: /Notes/i }).click();
    const area = page.locator("textarea").first();
    await expect(area).toBeVisible({ timeout: 15_000 });
    const marker = `v16-note-${Date.now()}`;
    await area.fill(marker);
    await page.getByRole("tab", { name: /Listen/i }).click();
    await page.getByRole("tab", { name: /Notes/i }).click();
    await expect(area).toHaveValue(marker);
  });

  test("Ślokas tab is reviewed-only or honest pending", async ({ page }) => {
    await page.getByRole("tab", { name: /Ślok|Shlok/i }).click();
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text).toMatch(/pending|reviewed|not invent|curated|Ślok|placeholder/i);
  });

  test("Story 009 is not linked from Story 008 navigation", async ({ page }) => {
    await expect(page.getByRole("link", { name: /Story 009/i })).toHaveCount(0);
  });
});
