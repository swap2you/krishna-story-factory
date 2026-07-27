import { expect, type Page, test } from "@playwright/test";

async function selectStoryTab(page: Page, name: RegExp) {
  const tab = page.getByRole("tab", { name });
  await tab.scrollIntoViewIfNeeded();
  await expect(tab).toBeVisible();
  await tab.click();
  await expect(tab).toHaveAttribute("aria-selected", "true", { timeout: 10_000 });
}

test.describe("Story 008 full-tab UAT", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/stories/008");
    await expect(page.getByRole("heading", { name: /Meeting of Nanda/i }).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("Listen tab exposes player controls", async ({ page }) => {
    await selectStoryTab(page, /Listen/i);
    await expect(page.locator(".audio-player")).toBeVisible();
    await expect(page.locator(".audio-player").getByRole("button", { name: /Play|Loading/i })).toBeVisible();
    await expect(page.getByLabel("Playback speed")).toBeVisible();
    await expect(page.getByRole("link", { name: /Download/i })).toBeVisible();
  });

  test("Read tab shows story body without internal markers", async ({ page }) => {
    await selectStoryTab(page, /Read/i);
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    await expect(panel.locator("article, .story-body, .prose, p").first()).toBeVisible({ timeout: 15_000 });
    const text = await panel.innerText();
    expect(text.length).toBeGreaterThan(80);
    expect(text).not.toMatch(/SSML|Audio Narration|Poster Visual Brief|OPENAI_|API_KEY/i);
  });

  test("Activities tab embeds or offers activity PDF", async ({ page }) => {
    await selectStoryTab(page, /Activities/i);
    const panel = page.getByRole("tabpanel");
    const embed = panel.locator("iframe, embed, object, a[href*='activity_sheet']");
    await expect(embed.first()).toBeVisible({ timeout: 15_000 });
  });

  test("Coloring tab opens lightbox assets", async ({ page }) => {
    await selectStoryTab(page, /Coloring/i);
    const panel = page.getByRole("tabpanel");
    await expect(panel.locator("img, .asset-tile, a[href*='coloring'], a[href*='poster']").first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Source tab is honest about review state", async ({ page }) => {
    await selectStoryTab(page, /Source/i);
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text.length).toBeGreaterThan(20);
    expect(text).toMatch(/Krishna Book|Bhāgavatam|source|review|Vedabase|pending|chapter/i);
  });

  test("Notes tab persists local reflection text", async ({ page }) => {
    await selectStoryTab(page, /Notes/i);
    const area = page.getByRole("tabpanel").locator("textarea").first();
    await expect(area).toBeVisible({ timeout: 15_000 });
    const marker = `v16-note-${Date.now()}`;
    await area.fill(marker);
    await selectStoryTab(page, /Listen/i);
    await selectStoryTab(page, /Notes/i);
    await expect(area).toHaveValue(marker);
  });

  test("Ślokas tab is reviewed-only or honest pending", async ({ page }) => {
    await selectStoryTab(page, /Ślok|Shlok/i);
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text).toMatch(/pending|reviewed|not invent|curated|Ślok|placeholder/i);
  });

  test("Story 009 is not linked from Story 008 navigation", async ({ page }) => {
    await expect(page.getByRole("link", { name: /Story 009/i })).toHaveCount(0);
  });
});
