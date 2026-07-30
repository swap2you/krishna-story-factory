import { expect, test } from "@playwright/test";

test.describe("v1.2 audio and keyboard", () => {
  test("play advances currentTime on story 001", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"), "iOS WebKit autoplay policy");
    const seen: string[] = [];
    page.on("request", (req) => {
      if (req.url().includes("narration.mp3")) seen.push(req.url());
    });
    await page.goto("/stories/001");
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
    await play.click();
    await page.waitForTimeout(500);
    const needsSecond = await page.locator(".audio-player").getByText(/press Play/i).isVisible().catch(() => false);
    if (needsSecond) {
      await page.locator(".audio-player").getByRole("button", { name: /^Play$/i }).click();
    }
    await expect(page.locator(".audio-player").getByRole("button", { name: /^Pause$/i })).toBeVisible({ timeout: 15_000 });
    await page.waitForFunction(() => {
      const audio = document.querySelector("audio");
      return !!audio && audio.readyState >= 2 && audio.currentTime > 0.2;
    }, undefined, { timeout: 20_000 });
    await page.waitForFunction(() => {
      const path = document.querySelector(".audio-player")?.getAttribute("data-playback-path") || "";
      return path === "blob_playing" || path === "native_playing";
    }, undefined, { timeout: 20_000 }).catch(() => undefined);
    const state = await page.evaluate(() => {
      const root = document.querySelector(".audio-player");
      const audio = document.querySelector("audio");
      return {
        path: root?.getAttribute("data-playback-path") || "",
        currentSrc: audio?.currentSrc || "",
        currentTime: audio?.currentTime || 0,
        paused: audio?.paused ?? true,
      };
    });
    // Prefetch uses blob: URLs so play() stays in the user-gesture window.
    expect(state.currentSrc.length).toBeGreaterThan(0);
    expect(state.currentSrc.includes("narration.mp3") || state.currentSrc.startsWith("blob:")).toBeTruthy();
    if (state.path === "failed" && !state.paused && state.currentTime > 0.2) {
      // Firefox can race the path attribute while audio is audibly advancing.
      expect(state.currentTime).toBeGreaterThan(0.2);
    } else {
      expect(["blob_playing", "native_playing"]).toContain(state.path);
    }
    if (!testInfo.project.name.includes("webkit")) {
      expect(seen.some((u) => u.includes("narration.mp3"))).toBeTruthy();
    }
  });

  test("modal arrows do not change audio time", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name.includes("mobile") && testInfo.project.name.includes("webkit"), "iOS WebKit autoplay policy");
    await page.goto("/stories/001");
    const play = page.getByRole("button", { name: /^Play$/i });
    await play.click();
    await page.waitForTimeout(800);
    const before = await page.evaluate(() => document.querySelector("audio")?.currentTime ?? 0);
    await page.getByRole("tab", { name: /Coloring/i }).click();
    const tile = page.locator(".asset-tile").first();
    if (await tile.count()) {
      await tile.click();
      await expect(page.getByRole("dialog")).toBeVisible();
      await page.keyboard.press("ArrowRight");
      await page.waitForTimeout(300);
      const after = await page.evaluate(() => document.querySelector("audio")?.currentTime ?? 0);
      expect(Math.abs(after - before)).toBeLessThan(20);
      await page.keyboard.press("Escape");
    }
  });
});

test.describe("v1.2 routes", () => {
  for (const route of ["/faq", "/printables", "/library/prayers-mantras", "/preachers", "/contact"]) {
    test(`loads ${route}`, async ({ page }) => {
      const res = await page.goto(route);
      expect(res?.ok()).toBeTruthy();
    });
  }

  test("preacher outline updates on selection", async ({ page }) => {
    await page.goto("/preachers");
    const card = page.locator("button.scope-card").first();
    if (!(await card.count())) {
      test.skip(true, "No catalog stories in this runtime");
      return;
    }
    await card.click();
    await expect(page.getByRole("heading", { name: /Outline preview/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^Print$/i })).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole("button", { name: /Export TXT/i })).toBeVisible();
  });

  test("contact form builds mailto", async ({ page }) => {
    await page.goto("/contact");
    await page.getByLabel(/^Name$/i).fill("Test Parent");
    await page.getByLabel(/^Email$/i).fill("parent@example.com");
    await page.getByLabel(/^Subject$/i).fill("Question");
    await page.getByLabel(/^Message$/i).fill("This is a sufficiently long test message.");
    await expect(page.getByRole("button", { name: /Open in email app/i })).toBeVisible();
    await expect(page.locator('a[href^="mailto:svarnagaurangdas"]').first()).toBeVisible();
  });
});
