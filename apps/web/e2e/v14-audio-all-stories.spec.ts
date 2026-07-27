import { expect, test } from "@playwright/test";

const STORIES = ["001", "002", "003", "004", "005", "006", "007", "008"];

test.describe("v1.5 audio — all released stories", () => {
  for (const storyNo of STORIES) {
    test(`story ${storyNo} play advances currentTime`, async ({ page }, testInfo) => {
      test.skip(
        testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"),
        "iOS WebKit autoplay policy",
      );
      await page.goto(`/stories/${storyNo}`);
      await page.getByRole("tab", { name: /Listen/i }).click().catch(() => undefined);
      await expect(page.locator(".audio-player")).toBeVisible({ timeout: 20_000 });
      await page
        .waitForFunction(() => {
          const root = document.querySelector(".audio-player");
          const audio = document.querySelector("audio");
          const path = root?.getAttribute("data-playback-path") || "";
          const src = audio?.currentSrc || audio?.src || "";
          const readyHint = /Narration ready|press Play/i.test(root?.textContent || "");
          return (
            path === "blob_ready" ||
            path === "blob_playing" ||
            path === "native_playing" ||
            (path === "idle" && (/narration\.mp3/i.test(src) || readyHint))
          );
        }, undefined, { timeout: 30_000 })
        .catch(() => undefined);
      const play = page.locator(".audio-player").getByRole("button", { name: /^(Play|Loading…)$/i });
      await expect(play).toBeVisible({ timeout: 20_000 });
      for (let attempt = 0; attempt < 3; attempt++) {
        const advanced = await page.evaluate(() => {
          const audio = document.querySelector("audio");
          return !!audio && !audio.paused && audio.currentTime > 0.15;
        });
        if (advanced) break;
        const pauseVisible = await page
          .locator(".audio-player")
          .getByRole("button", { name: /^Pause$/i })
          .isVisible()
          .catch(() => false);
        if (pauseVisible) break;
        const playVisible = await page
          .locator(".audio-player")
          .getByRole("button", { name: /^(Play|Loading…)$/i })
          .isVisible()
          .catch(() => false);
        if (playVisible) {
          await page
            .locator(".audio-player")
            .getByRole("button", { name: /^(Play|Loading…)$/i })
            .click({ timeout: 5_000 })
            .catch(() => undefined);
        }
        await page.waitForTimeout(700);
      }
      await page.waitForFunction(() => {
        const audio = document.querySelector("audio");
        return !!audio && audio.readyState >= 2 && audio.currentTime > 0.15 && !audio.paused;
      }, undefined, { timeout: 45_000 });
      // Firefox can briefly desync the Pause label while audio is already advancing.
      const pause = page.locator(".audio-player").getByRole("button", { name: /^Pause$/i });
      const pauseVisible = await pause.isVisible().catch(() => false);
      if (!pauseVisible) {
        await page
          .locator(".audio-player")
          .getByRole("button", { name: /^(Play|Loading…)$/i })
          .click({ timeout: 3_000 })
          .catch(() => undefined);
        await page.waitForTimeout(500);
      }
      await expect
        .poll(async () => {
          const playing = await page.evaluate(() => {
            const audio = document.querySelector("audio");
            return !!audio && !audio.paused && audio.currentTime > 0.15;
          });
          const labelOk = await pause.isVisible().catch(() => false);
          return playing || labelOk;
        }, { timeout: 15_000 })
        .toBeTruthy();
      const state = await page.evaluate(() => {
        const root = document.querySelector(".audio-player");
        const audio = document.querySelector("audio");
        return {
          path: root?.getAttribute("data-playback-path") || "",
          currentSrc: audio?.currentSrc || "",
          readyState: audio?.readyState ?? 0,
          currentTime: audio?.currentTime ?? 0,
          paused: audio?.paused ?? true,
        };
      });
      expect(state.readyState).toBeGreaterThanOrEqual(2);
      expect(state.currentTime).toBeGreaterThan(0.15);
      expect(state.paused).toBeFalsy();
      expect(state.currentSrc.length).toBeGreaterThan(0);
      expect(["blob_playing", "native_playing"]).toContain(state.path);
    });
  }

  test("story 007 links to published 008", async ({ page }) => {
    await page.goto("/stories/007");
    await expect(page.getByRole("link", { name: /Story 008/i })).toBeVisible();
  });
});
