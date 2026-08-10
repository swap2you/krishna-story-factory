/**
 * One-shot P01C review screenshots against standalone production build.
 * Run: npx playwright test e2e/p01c_review_screenshots.spec.ts --project=chromium-desktop
 */
import { test, expect } from "@playwright/test";
import path from "path";

const OUT = path.resolve(
  __dirname,
  "../../../artifacts/review-bundles/P01C-2026-08-07/screenshots",
);
const TOKEN = process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "bhava-local-studio";
const SLUG = "p01c-structural-fixture";

async function assertNoDevChrome(page: import("@playwright/test").Page) {
  await expect(page.locator("text=1 Issue")).toHaveCount(0);
  await expect(page.locator("[data-nextjs-toast]")).toHaveCount(0);
  await expect(page.locator("#__next-build-watcher")).toHaveCount(0);
}

async function studioSignIn(page: import("@playwright/test").Page) {
  await page.goto("/studio/knowledge", { waitUntil: "networkidle" });
  const token = page.getByLabel(/Bootstrap token/i);
  if (await token.count()) {
    await token.fill(TOKEN);
    await page.getByLabel(/Studio role/i).selectOption("steward");
    await page.getByRole("button", { name: /Enter studio/i }).click();
    await expect(page.getByRole("heading", { name: "Roadmap total" })).toBeVisible({
      timeout: 20000,
    });
  }
}

test.describe("P01C review screenshots (standalone)", () => {
  test("capture six review screenshots without Next toolbar", async ({ page }) => {
    test.skip(
      process.env.BHAVA_E2E_MODE === "public",
      "review screenshots require private studio on standalone/local builds",
    );
    test.setTimeout(180_000);
    await studioSignIn(page);
    await assertNoDevChrome(page);
    await page.screenshot({
      path: path.join(OUT, "01-studio-queue-desktop.png"),
      fullPage: true,
    });

    await page.goto(`/studio/knowledge/preview/${SLUG}?lens=explorer`, {
      waitUntil: "networkidle",
    });
    await assertNoDevChrome(page);
    await page.screenshot({
      path: path.join(OUT, "02-preview-explorer-desktop.png"),
      fullPage: true,
    });

    await page.goto(`/studio/knowledge/preview/${SLUG}?lens=study`, {
      waitUntil: "networkidle",
    });
    await assertNoDevChrome(page);
    await page.screenshot({
      path: path.join(OUT, "03-preview-study-desktop.png"),
      fullPage: true,
    });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`/studio/knowledge/preview/${SLUG}?lens=little_learner`, {
      waitUntil: "networkidle",
    });
    await assertNoDevChrome(page);
    await page.screenshot({
      path: path.join(OUT, "04-preview-little-learner-mobile.png"),
      fullPage: true,
    });

    await page.setViewportSize({ width: 820, height: 1180 });
    await page.goto(`/studio/knowledge/preview/${SLUG}?lens=teen`, {
      waitUntil: "networkidle",
    });
    await assertNoDevChrome(page);
    await page.screenshot({
      path: path.join(OUT, "05-preview-teen-tablet.png"),
      fullPage: true,
    });

    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(`/studio/knowledge/preview/${SLUG}?lens=explorer`, {
      waitUntil: "networkidle",
    });
    await assertNoDevChrome(page);
    const footer = page.locator("footer").last();
    await footer.scrollIntoViewIfNeeded();
    await footer.screenshot({ path: path.join(OUT, "06-footer-identity.png") });
  });
});
