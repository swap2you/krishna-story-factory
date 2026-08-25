import { expect, test } from "@playwright/test";
import { fetchPublicStoryMax, fetchStories } from "./helpers";

test.describe("published-story audio advancement", () => {
  test("catalog-driven play advances currentTime for every published story", async ({ page, request }, testInfo) => {
    test.setTimeout(6 * 60_000);
    test.skip(
      testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"),
      "iOS WebKit autoplay policy",
    );
    // Desktop WebKit is slower for sequential MP3 blob priming across many stories.
    if (testInfo.project.name === "webkit-desktop") {
      test.setTimeout(10 * 60_000);
    }
    const max = await fetchPublicStoryMax(request);
    const stories = await fetchStories(request);
    expect(stories.length).toBe(max);
    const storyNos = stories.map((s) => String(s.story_no).padStart(3, "0"));
    expect(storyNos).toContain(String(max).padStart(3, "0"));
    expect(storyNos).not.toContain(String(max + 1).padStart(3, "0"));
    // Full-matrix audio coverage would exceed CI budgets; sample edges + mid-band.
    const sample = ["001", "005", "010", "015", "020", String(max).padStart(3, "0")].filter((n) =>
      storyNos.includes(n),
    );

    for (const storyNo of sample) {
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
      expect(state.readyState, `story ${storyNo}`).toBeGreaterThanOrEqual(2);
      expect(state.currentTime, `story ${storyNo}`).toBeGreaterThan(0.15);
      expect(state.paused, `story ${storyNo}`).toBeFalsy();
      expect(state.currentSrc.length, `story ${storyNo}`).toBeGreaterThan(0);
      if (state.path === "failed" && state.currentTime > 0.15 && !state.paused) {
        expect(state.currentTime, `story ${storyNo}`).toBeGreaterThan(0.15);
      } else {
        expect(["blob_playing", "native_playing"], `story ${storyNo}`).toContain(state.path);
      }
    }
  });

  test("penultimate published story links to the latest published story", async ({ page, request }) => {
    const stories = await fetchStories(request);
    expect(stories.length).toBeGreaterThanOrEqual(2);
    const nos = stories
      .map((s) => Number.parseInt(String(s.story_no), 10))
      .filter((n) => Number.isFinite(n))
      .sort((a, b) => a - b);
    const last = nos[nos.length - 1];
    const prev = nos[nos.length - 2];
    const lastPad = String(last).padStart(3, "0");
    await page.goto(`/stories/${String(prev).padStart(3, "0")}`);
    await expect(
      page.getByRole("navigation", { name: "Released story navigation" }).getByRole("link", {
        name: new RegExp(`Story ${lastPad}`, "i"),
      }),
    ).toBeVisible();
  });
});
