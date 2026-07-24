import { expect, test } from "@playwright/test";

const routes = [
  "/",
  "/library",
  "/library/krishna-book",
  "/teachers",
  "/prabhupada-vani",
  "/knowledge",
  "/about",
  "/contact",
  "/privacy",
  "/accessibility",
  "/source-permissions",
  "/studio",
];

test.describe("navigation", () => {
  for (const route of routes) {
    test(`loads ${route}`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response?.ok()).toBeTruthy();
      await expect(page.locator("header .wordmark")).toBeVisible();
    });
  }

  test("primary nav includes Prabhupāda Vāṇī destination", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("navigation", { name: "Primary navigation" }).getByRole("link", { name: "Prabhupāda Vāṇī" })).toHaveAttribute(
      "href",
      "/prabhupada-vani",
    );
  });
});
