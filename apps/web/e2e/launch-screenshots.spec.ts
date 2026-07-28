import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

/**
 * Writes real PNG screenshots for launch UAT (not LocalTunnel / extension exports).
 * Run: npx playwright test --project=screenshots
 */
const VIEWPORTS = [
  { name: "390x844", width: 390, height: 844 },
  { name: "430x932", width: 430, height: 932 },
  { name: "768x1024", width: 768, height: 1024 },
  { name: "1024x768", width: 1024, height: 768 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
] as const;

const CAPTURES: Array<{ route: string; file: string; tab?: RegExp; section?: string }> = [
  { route: "/", file: "home" },
  { route: "/library", file: "library" },
  { route: "/library/krishna-book", file: "library-krishna-book" },
  { route: "/knowledge", file: "knowledge" },
  { route: "/knowledge/search", file: "knowledge-search" },
  { route: "/learning/children-youth", file: "children-youth" },
  { route: "/sunday-school", file: "sunday-school" },
  { route: "/teachers", file: "teachers" },
  { route: "/preachers", file: "preachers" },
  { route: "/prabhupada-vani", file: "prabhupada-vani" },
  { route: "/printables", file: "printables" },
  { route: "/about", file: "about" },
  { route: "/contact", file: "contact" },
  { route: "/faq", file: "faq" },
  { route: "/stories/001", file: "story-001-listen", tab: /Listen/i, section: "Listen" },
  { route: "/stories/001", file: "story-001-read", tab: /Read/i, section: "Read" },
  { route: "/stories/009", file: "story-009-listen", tab: /Listen/i, section: "Listen" },
  { route: "/stories/009", file: "story-009-read", tab: /Read/i, section: "Read" },
  { route: "/stories/009", file: "story-009-activities", tab: /Activities/i, section: "Activities" },
  { route: "/stories/009", file: "story-009-coloring", tab: /Coloring/i, section: "Coloring" },
  { route: "/stories/009", file: "story-009-source", tab: /Source/i, section: "Source" },
  { route: "/stories/009", file: "story-009-notes", tab: /Notes/i, section: "Notes" },
  { route: "/stories/009", file: "story-009-shlokas", tab: /Ślok/i, section: "Ślokās" },
];

const OUT_ROOT = path.resolve(__dirname, "../../../docs/product/launch/screenshots");

test.describe("launch screenshots", () => {
  for (const vp of VIEWPORTS) {
    test.describe(vp.name, () => {
      test.use({ viewport: { width: vp.width, height: vp.height } });

      for (const capture of CAPTURES) {
        test(`${capture.file}`, async ({ page }) => {
          const dir = path.join(OUT_ROOT, vp.name);
          fs.mkdirSync(dir, { recursive: true });
          await page.goto(capture.route, { waitUntil: "networkidle" }).catch(async () => {
            await page.goto(capture.route);
          });
          if (capture.tab) {
            const tab = page.getByRole("tab", { name: capture.tab });
            if (await tab.count()) {
              await tab.first().click({ timeout: 10_000 }).catch(() => undefined);
              await page.waitForTimeout(300).catch(() => undefined);
            }
          }
          const filePath = path.join(dir, `${capture.file}.png`);
          await page.screenshot({ path: filePath, fullPage: true });
          expect(fs.existsSync(filePath)).toBeTruthy();
          expect(fs.statSync(filePath).size).toBeGreaterThan(2_000);
        });
      }
    });
  }
});
