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
    await page.evaluate(() => {
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, 480);
    });
    await page.waitForFunction(() => window.scrollY >= 400, undefined, { timeout: 5_000 });

    const tile = page.locator(".asset-tile").first();
    await expect(tile).toBeVisible({ timeout: 15_000 });
    // Avoid scrollIntoView side-effects that would change the locked scroll origin.
    await tile.click({ force: true });

    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    const topClose = page.getByRole("button", { name: "Close image viewer" });
    await expect(topClose).toBeVisible();

    const dialogScrollTop = await dialog.evaluate((el) => el.scrollTop);
    expect(dialogScrollTop).toBe(0);

    const lockedScrollY = await page.evaluate(() => {
      const top = document.body.style.top || "0";
      const fromTop = Math.abs(Number.parseInt(top, 10) || 0);
      return fromTop || window.scrollY || document.documentElement.scrollTop || 0;
    });
    expect(lockedScrollY).toBeGreaterThan(100);

    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);

    await page.waitForFunction(
      (before) => {
        const y = window.scrollY || document.documentElement.scrollTop || 0;
        return Math.abs(y - before) <= Math.max(24, before * 0.2);
      },
      lockedScrollY,
      { timeout: 8_000 },
    );

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    const miniPlayer = page.locator(".mini-player--floating");
    await expect(miniPlayer).toBeVisible({ timeout: 8_000 });
    await expect(miniPlayer.getByRole("slider", { name: "Seek narration" })).toBeVisible();

    const hideFloating = miniPlayer.getByRole("button", { name: "Hide floating player" });
    await expect(hideFloating).toBeVisible();
    const wasPlaying = await page.locator("audio").evaluate((el) => !(el as HTMLAudioElement).paused);
    if (!wasPlaying) {
      await page.getByRole("button", { name: /^Play$/i }).first().click();
    }
    const timeBefore = await page.locator("audio").evaluate((el) => (el as HTMLAudioElement).currentTime);
    await hideFloating.click();
    await expect(miniPlayer).toHaveCount(0);
    const timeAfter = await page.locator("audio").evaluate((el) => (el as HTMLAudioElement).currentTime);
    expect(timeAfter).toBeGreaterThanOrEqual(timeBefore);
    await expect(page.getByRole("button", { name: "Show floating player" })).toBeVisible();
    await page.getByRole("button", { name: "Show floating player" }).click();
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await expect(page.locator(".mini-player--floating")).toBeVisible({ timeout: 8_000 });

    await selectStoryTab(page, /Coloring/i);
    await page.locator(".asset-tile").first().click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.locator(".mini-player--floating")).toHaveCount(0);

    // Print uses isolated iframe document — not application DOM thumbnails.
    await page.evaluate(() => {
      (window as unknown as { __BHAVA_SKIP_PRINT__?: boolean }).__BHAVA_SKIP_PRINT__ = true;
    });
    await page.getByRole("button", { name: /^Print$/i }).click();
    await page.waitForFunction(
      () => {
        const frame = document.querySelector('iframe[title="Print selected image"]') as HTMLIFrameElement | null;
        if (!frame?.contentDocument) return false;
        const html = frame.contentDocument.documentElement.outerHTML;
        return /<img\b/i.test(html) && !/carousel-thumb|asset-tile|site-header/i.test(html);
      },
      undefined,
      { timeout: 5_000 },
    );

    await page.keyboard.press("Escape");
    await expectNoHorizontalOverflow(page);
  });

  test("Ślokas tab shows Vedabase button and chapter-reference honesty", async ({ page, request }) => {
    const stories = await fetchStories(request);
    const story = stories.find((item) => item.story_no === "011") ?? stories.find((item) => item.story_no === "020");
    test.skip(!story, "Need a published story with Ślokas");
    await page.goto(`/stories/${story!.story_no}`);
    await selectStoryTab(page, /Ślok|Shlok/i);
    const vedabase = page.getByRole("link", { name: /Read this passage on Vedabase/i });
    await expect(vedabase.or(page.getByText(/No separate verse|Companion|Chapter reference|pending/i))).toBeVisible({
      timeout: 15_000,
    });
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
