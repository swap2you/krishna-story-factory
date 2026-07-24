import { expect, test } from "@playwright/test";

const STORIES = ["001", "002", "003", "004", "005", "006", "007"];

test.describe("v1.4 audio — all released stories", () => {
  for (const storyNo of STORIES) {
    test(`story ${storyNo} play advances currentTime`, async ({ page }, testInfo) => {
      test.skip(
        testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"),
        "iOS WebKit autoplay policy",
      );
      const seen: string[] = [];
      page.on("request", (req) => {
        if (req.url().includes("narration.mp3") || req.url().includes("blob:")) {
          seen.push(req.url());
        }
      });
      await page.goto(`/stories/${storyNo}`);
      await page.getByRole("tab", { name: /Listen/i }).click().catch(() => undefined);
      const play = page.locator(".audio-player").getByRole("button", { name: /^Play$/i });
      await expect(play).toBeVisible({ timeout: 20_000 });
      await play.click();
      await expect(page.locator(".audio-player").getByRole("button", { name: /^Pause$/i })).toBeVisible({
        timeout: 20_000,
      });
      await page.waitForFunction(() => {
        const audio = document.querySelector("audio");
        return !!audio && audio.readyState >= 2 && audio.currentTime > 0.15;
      }, undefined, { timeout: 30_000 });
      const state = await page.evaluate(() => {
        const audio = document.querySelector("audio");
        return {
          currentSrc: audio?.currentSrc || "",
          readyState: audio?.readyState ?? 0,
          currentTime: audio?.currentTime ?? 0,
        };
      });
      expect(state.readyState).toBeGreaterThanOrEqual(2);
      expect(state.currentTime).toBeGreaterThan(0.15);
      expect(state.currentSrc.length).toBeGreaterThan(0);
    });
  }

  test("story 007 does not link to unreleased 008", async ({ page }) => {
    await page.goto("/stories/007");
    await expect(page.getByRole("link", { name: /Story 008/i })).toHaveCount(0);
    await expect(page.getByText(/End of the current Bhāva release/i)).toBeVisible();
  });
});
