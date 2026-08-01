import { expect, type Page, test } from "@playwright/test";
import { fetchStories } from "./helpers";

async function selectStoryTab(page: Page, name: RegExp) {
  const tab = page.getByRole("tab", { name });
  await tab.scrollIntoViewIfNeeded();
  await expect(tab).toBeVisible();
  for (let attempt = 0; attempt < 3; attempt += 1) {
    await tab.click({ force: attempt > 0 });
    const selected = await tab.getAttribute("aria-selected");
    if (selected === "true") return;
    await page.waitForTimeout(250);
  }
  await expect(tab).toHaveAttribute("aria-selected", "true", { timeout: 10_000 });
}

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return doc.scrollWidth > doc.clientWidth + 1;
  });
  expect(overflow).toBeFalsy();
}

test.describe("Story experience UX lock", () => {
  test("story page wallpaper, tabs, lightbox, mini-player, and overflow", async ({ page, request }) => {
    const stories = await fetchStories(request);
    test.skip(!stories.length, "No catalog stories available");

    const story = stories.find((item) => item.story_no === "001") ?? stories[0];
    const posterPath = story.poster_url ?? "story_poster";

    await page.goto(`/stories/${story.story_no}`);
    await expect(page.locator(".story-main h1").first()).toBeVisible({ timeout: 20_000 });

    const wash = page.locator(".story-poster-wash");
    await expect(wash).toBeVisible();
    await expect(wash.locator("img")).toHaveAttribute("src", new RegExp(posterPath.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));

    const tabNames = [/Listen/i, /Read/i, /Activities/i, /Coloring/i, /Source/i, /Notes/i, /Ślok|Shlok/i];
    for (const name of tabNames) {
      await selectStoryTab(page, name);
      await expect(page.getByRole("tabpanel")).toBeVisible();
    }

    if (story.story_no === "001") {
      await selectStoryTab(page, /Ślok|Shlok/i);
      const shlokaText = await page.getByRole("tabpanel").innerText();
      const withoutDashes = shlokaText.replace(/[—–\-]/g, " ").replace(/\s+/g, " ").trim();
      expect(withoutDashes.length).toBeGreaterThan(20);
      expect(shlokaText).toMatch(/companion|prayer|verse|Earth|Krishna|not invent|pending|reviewed/i);
    }

    await selectStoryTab(page, /Coloring/i);
    await page.evaluate(() => window.scrollTo(0, 480));
    await page.waitForFunction(() => window.scrollY >= 400, undefined, { timeout: 5_000 });
    const scrollBefore = await page.evaluate(() => window.scrollY);

    const tile = page.locator(".asset-tile").first();
    await expect(tile).toBeVisible({ timeout: 15_000 });
    await tile.click();

    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    const topClose = page.getByRole("button", { name: "Close image viewer" });
    await expect(topClose).toBeVisible();

    const dialogScrollTop = await dialog.evaluate((el) => el.scrollTop);
    expect(dialogScrollTop).toBe(0);

    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);

    await page.waitForFunction(
      (before) => Math.abs(window.scrollY - before) <= 8,
      scrollBefore,
      { timeout: 8_000 },
    );

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    const miniPlayer = page.locator(".mini-player--floating");
    await expect(miniPlayer).toBeVisible({ timeout: 8_000 });
    await expect(miniPlayer.getByRole("slider", { name: "Seek narration" })).toBeVisible();

    await selectStoryTab(page, /Coloring/i);
    await page.locator(".asset-tile").first().click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(miniPlayer).toHaveCount(0);

    await page.keyboard.press("Escape");
    await expectNoHorizontalOverflow(page);
  });

  test("Story 020 wallpaper uses a different poster than Story 001 when both are published", async ({
    page,
    request,
  }) => {
    const stories = await fetchStories(request);
    const story001 = stories.find((item) => item.story_no === "001");
    const story020 = stories.find((item) => item.story_no === "020");
    test.skip(!story001?.poster_url || !story020?.poster_url, "Stories 001 and 020 with posters required");

    await page.goto("/stories/001");
    await expect(page.locator(".story-poster-wash img")).toBeVisible({ timeout: 20_000 });
    const poster001 = await page.locator(".story-poster-wash img").getAttribute("src");

    await page.goto("/stories/020");
    await expect(page.locator(".story-poster-wash img")).toBeVisible({ timeout: 20_000 });
    const poster020 = await page.locator(".story-poster-wash img").getAttribute("src");

    expect(poster001).toBeTruthy();
    expect(poster020).toBeTruthy();
    expect(poster001).not.toEqual(poster020);
  });
});
