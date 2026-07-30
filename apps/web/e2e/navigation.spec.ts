import { expect, test } from "@playwright/test";
import { isLocalMode, isPublicMode } from "./mode";

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
];

test.describe("navigation", () => {
  for (const route of routes) {
    test(`loads ${route}`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response?.ok()).toBeTruthy();
      await expect(page.getByRole("link", { name: "Bhāva home" })).toBeVisible();
    });
  }

  test("primary nav includes Prabhupāda Vāṇī destination", async ({ page }) => {
    await page.goto("/");
    const menu = page.getByRole("button", { name: /^Menu$/i });
    if (await menu.isVisible().catch(() => false)) {
      await menu.click();
    }
    await expect(
      page.getByRole("navigation", { name: "Primary navigation" }).getByRole("link", { name: "Prabhupāda Vāṇī" }),
    ).toHaveAttribute("href", "/prabhupada-vani");
  });

  test("studio is reachable on an operator workstation", async ({ page }) => {
    test.skip(!isLocalMode, "Studio only exists outside public production mode");
    const response = await page.goto("/studio");
    expect(response?.ok()).toBeTruthy();
    await expect(page.getByRole("link", { name: "Bhāva home" })).toBeVisible();
  });

  test("public site never links to a private surface", async ({ page }) => {
    test.skip(!isPublicMode, "Deny-list only applies to the public production build");
    for (const route of ["/", "/library/krishna-book"]) {
      await page.goto(route);
      const hrefs = await page.locator("a[href]").evaluateAll((nodes) =>
        nodes.map((node) => node.getAttribute("href") ?? ""),
      );
      const leaked = hrefs.filter((href) => /^\/(studio|dev)(\/|$)/.test(href));
      expect(leaked, `private links found on ${route}`).toEqual([]);
    }
  });
});
