import { test } from "@playwright/test";
import { expectNoCriticalAxe } from "./helpers";

const routes = ["/", "/library/krishna-book", "/teachers", "/contact", "/prabhupada-vani", "/studio", "/about"];

test.describe("accessibility", () => {
  for (const route of routes) {
    test(`axe critical/serious clean on ${route}`, async ({ page }) => {
      await page.goto(route);
      await expectNoCriticalAxe(page);
    });
  }
});
