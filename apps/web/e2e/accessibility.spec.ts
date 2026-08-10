import { test } from "@playwright/test";
import { expectNoCriticalAxe } from "./helpers";

const routes = [
  "/",
  "/library",
  "/library/krishna-book",
  "/knowledge",
  "/knowledge/search",
  "/learning",
  "/learning/children-youth",
  "/learning/families",
  "/learning/gurukula-homeschool",
  "/learning/festivals",
  "/sunday-school",
  "/teachers",
  "/preachers",
  "/prabhupada-vani",
  "/printables",
  "/about",
  "/contact",
  "/faq",
  "/stories/001",
  "/stories/009",
];

test.describe("accessibility", () => {
  for (const route of routes) {
    test(`axe critical/serious clean on ${route}`, async ({ page }) => {
      await page.goto(route);
      await expectNoCriticalAxe(page);
    });
  }

  test("story player selects keep readable contrast", async ({ page }) => {
    await page.goto("/stories/009");
    await page.getByRole("tab", { name: /Listen/i }).click().catch(() => undefined);
    const select = page.locator(".audio-controls select").first();
    await select.waitFor({ state: "visible", timeout: 20_000 });
    const contrast = await select.evaluate((el) => {
      const styles = getComputedStyle(el);
      const parse = (value: string) => {
        const m = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
        if (!m) return null;
        return [Number(m[1]), Number(m[2]), Number(m[3])] as const;
      };
      const luminance = (rgb: readonly [number, number, number]) => {
        const chan = rgb.map((c) => {
          const s = c / 255;
          return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2];
      };
      const fg = parse(styles.color);
      const bg = parse(styles.backgroundColor);
      if (!fg || !bg) return 0;
      const L1 = luminance(fg);
      const L2 = luminance(bg);
      const lighter = Math.max(L1, L2);
      const darker = Math.min(L1, L2);
      return (lighter + 0.05) / (darker + 0.05);
    });
    test.info().annotations.push({ type: "contrast", description: String(contrast) });
    if (!(contrast >= 4.5)) {
      throw new Error(`Playback select contrast ${contrast} < 4.5`);
    }
  });
});
