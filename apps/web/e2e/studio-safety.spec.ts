import { expect, test } from "@playwright/test";
import { PRIVATE_PREFIXES, isLocalMode, isPublicMode } from "./mode";
import { apiURL, expectNoCriticalAxe } from "./helpers";

test.describe("studio safety", () => {
  test("studio is accessible on an operator workstation", async ({ page }) => {
    test.skip(!isLocalMode, "Studio is not served in public production mode");
    await page.goto("/studio");
    await expectNoCriticalAxe(page);
  });

  test("factory actions stay disabled on an operator workstation", async ({ page }) => {
    test.skip(!isLocalMode, "Studio is not served in public production mode");
    await page.goto("/studio");
    await expect(page.getByText(/loopback|factory studio|disabled/i).first()).toBeVisible();
    const enabledButtons = page.getByRole("button").filter({ hasNotText: /refresh|reload/i });
    const count = await enabledButtons.count();
    for (let i = 0; i < count; i += 1) {
      const button = enabledButtons.nth(i);
      const disabled = await button.isDisabled().catch(() => false);
      const label = (await button.innerText()).toLowerCase();
      if (label.includes("generate") || label.includes("preflight") || label.includes("scheduler")) {
        expect(disabled).toBeTruthy();
      }
    }
  });

  test("public production blocks every private route", async ({ page }) => {
    test.skip(!isPublicMode, "Blocking only applies to the public production build");
    for (const prefix of PRIVATE_PREFIXES) {
      const response = await page.goto(prefix);
      expect(response?.status(), `${prefix} must not be served`).toBe(404);
    }
  });

  test("public production API exposes no factory or docs surface", async ({ request }) => {
    test.skip(!isPublicMode, "Blocking only applies to the public production build");
    const origin = apiURL.replace(/\/api\/v1$/, "");
    for (const path of ["/openapi.json", "/docs", "/redoc", "/api/v1/local/status"]) {
      const response = await request.get(`${origin}${path}`);
      expect(response.status(), `${path} must not be served`).toBe(404);
    }
  });
});
