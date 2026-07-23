import { expect, test } from "@playwright/test";

test.describe("studio safety", () => {
  test("factory actions stay disabled", async ({ page }) => {
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
});
