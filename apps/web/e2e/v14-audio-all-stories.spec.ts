import { expect, test } from "@playwright/test";

const STORIES = ["001", "002", "003", "004", "005", "006", "007", "008"];

test.describe("v1.5 audio — all released stories", () => {
  for (const storyNo of STORIES) {
    test(`story ${storyNo} play advances currentTime`, async ({ page }, testInfo) => {
      test.skip(
        testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"),
        "iOS WebKit autoplay policy",
      );
      page.on("request", (req) => {
        if (req.url().includes("narration.mp3") || req.url().includes("blob:")) {
          /* request observation retained for debugging */
        }
      });
      await page.goto(`/stories/${storyNo}`);
      await page.getByRole("tab", { name: /Listen/i }).click().catch(() => undefined);
      const play = page.locator(".audio-player").getByRole("button", { name: /^(Play|Loading…)$/i });
      await expect(play).toBeVisible({ timeout: 20_000 });
      await play.click();
      await expect(page.locator(".audio-player").getByRole("button", { name: /^Pause$/i })).toBeVisible({
        timeout: 30_000,
      });
      await page.waitForFunction(() => {
        const audio = document.querySelector("audio");
        return !!audio && audio.readyState >= 2 && audio.currentTime > 0.15;
      }, undefined, { timeout: 45_000 });
      const state = await page.evaluate(() => {
        const root = document.querySelector(".audio-player");
        const audio = document.querySelector("audio");
        return {
          path: root?.getAttribute("data-playback-path") || "",
          currentSrc: audio?.currentSrc || "",
          readyState: audio?.readyState ?? 0,
          currentTime: audio?.currentTime ?? 0,
        };
      });
      expect(state.readyState).toBeGreaterThanOrEqual(2);
      expect(state.currentTime).toBeGreaterThan(0.15);
      expect(state.currentSrc.length).toBeGreaterThan(0);
      expect(["native_playing", "blob_playing"]).toContain(state.path);
    });
  }

  test("story 007 links to published 008", async ({ page }) => {
    await page.goto("/stories/007");
    await expect(page.getByRole("link", { name: /Story 008/i })).toBeVisible();
  });
});
