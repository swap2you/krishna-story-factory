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

    await page.evaluate(() => {
      if (!document.getElementById("bhava-e2e-scroll-spacer")) {
        const spacer = document.createElement("div");
        spacer.id = "bhava-e2e-scroll-spacer";
        spacer.style.height = "220vh";
        spacer.setAttribute("aria-hidden", "true");
        document.body.appendChild(spacer);
      }
    });
    await page.locator(".persistent-player").scrollIntoViewIfNeeded();
    await page.evaluate(() => {
      const player = document.querySelector(".persistent-player");
      if (player) {
        const top = player.getBoundingClientRect().top + window.scrollY;
        window.scrollTo(0, top + window.innerHeight + 80);
      } else {
        window.scrollBy(0, window.innerHeight * 2);
      }
    });
    await page.waitForFunction(() => {
      const el = document.querySelector(".persistent-player");
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.bottom < 0 || rect.top > window.innerHeight;
    }, undefined, { timeout: 8_000 });
    const miniPlayer = page.locator(".mini-player--floating");
    await expect(miniPlayer).toBeVisible({ timeout: 8_000 });
    await expect(miniPlayer.getByRole("slider", { name: "Seek narration" })).toBeVisible();

    const hideFloating = miniPlayer.getByRole("button", { name: "Hide floating player" });
    await expect(hideFloating).toBeVisible();
    // Drive playback via the audio element so Playwright does not scroll the primary
    // player into view (which would dismiss the floating mini-player via IntersectionObserver).
    await page.locator("audio").evaluate(async (el) => {
      const audio = el as HTMLAudioElement;
      try {
        await audio.play();
      } catch {
        /* autoplay policies may block; dismiss still must work while paused */
      }
    });
    const timeBefore = await page.locator("audio").evaluate((el) => (el as HTMLAudioElement).currentTime);
    await hideFloating.click({ force: true });
    await expect(miniPlayer).toHaveCount(0);
    const timeAfter = await page.locator("audio").evaluate((el) => (el as HTMLAudioElement).currentTime);
    expect(timeAfter).toBeGreaterThanOrEqual(timeBefore);
    const restore = page.getByRole("button", { name: "Show floating player" });
    await expect(restore).toBeVisible();
    await restore.click({ force: true });
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await expect(page.locator(".mini-player--floating")).toBeVisible({ timeout: 8_000 });

    await selectStoryTab(page, /Coloring/i);
    await page.locator(".asset-tile").first().click({ force: true });
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.locator(".mini-player--floating")).toHaveCount(0);

    // Print uses isolated iframe document — not application DOM thumbnails.
    await page.evaluate(() => {
      const w = window as unknown as {
        __BHAVA_SKIP_PRINT__?: boolean;
        __BHAVA_LAST_PRINT_HTML__?: string;
      };
      w.__BHAVA_SKIP_PRINT__ = true;
      w.__BHAVA_LAST_PRINT_HTML__ = "";
    });
    await page.getByRole("dialog").getByRole("button", { name: /^Print$/i }).click({ force: true });
    await page.waitForFunction(
      () => Boolean((window as unknown as { __BHAVA_LAST_PRINT_HTML__?: string }).__BHAVA_LAST_PRINT_HTML__),
      undefined,
      { timeout: 5_000 },
    );
    const printHtml = await page.evaluate(
      () => (window as unknown as { __BHAVA_LAST_PRINT_HTML__?: string }).__BHAVA_LAST_PRINT_HTML__ || "",
    );
    expect(printHtml).toMatch(/<img\b/i);
    expect(printHtml).not.toMatch(/carousel-thumb|asset-tile|site-header/i);

    await page.keyboard.press("Escape");
    await expectNoHorizontalOverflow(page);
  });

  test("Ślokas tab shows Vedabase button and chapter-reference honesty", async ({ page, request }) => {
    const stories = await fetchStories(request);
    const story = stories.find((item) => item.story_no === "011") ?? stories.find((item) => item.story_no === "020");
    test.skip(!story, "Need a published story with Ślokas");
    await page.goto(`/stories/${story!.story_no}`);
    await selectStoryTab(page, /Ślok|Shlok/i);
    const panel = page.getByRole("tabpanel");
    await expect(panel).toBeVisible();
    const vedabaseCount = await panel.getByRole("link", { name: /Read this passage on Vedabase/i }).count();
    const honestyCount = await panel.getByText(/No separate verse|Companion reference|Chapter reference|Pending review/i).count();
    expect(vedabaseCount + honestyCount).toBeGreaterThan(0);
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
