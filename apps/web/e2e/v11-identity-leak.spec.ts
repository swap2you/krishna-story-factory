import { expect, test } from "@playwright/test";

const FORBIDDEN = [/Swapnil/i, /swapnilpatil/i, /linkedin\.com/i, /github\.com/i];
const LEAK = [
  /Audio Narration/i,
  /Poster Visual Brief/i,
  /Coloring Visual Brief/i,
  /Activity Data/i,
  /<break time=/i,
];

const PUBLIC_ROUTES = [
  "/",
  "/library",
  "/library/krishna-book",
  "/library/srimad-bhagavatam",
  "/sunday-school",
  "/preachers",
  "/teachers",
  "/prabhupada-vani",
  "/knowledge",
  "/about",
  "/contact",
  "/faq",
  "/printables",
  "/privacy",
  "/source-permissions",
];

test.describe("v1.1 identity and route smoke", () => {
  for (const route of PUBLIC_ROUTES) {
    test(`public route ${route} has no civil identity leakage`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response?.ok() || response?.status() === 304).toBeTruthy();
      const body = await page.locator("body").innerText();
      for (const pattern of FORBIDDEN) {
        expect(body).not.toMatch(pattern);
      }
    });
  }

  test("contact uses only steward mailto", async ({ page }) => {
    await page.goto("/contact");
    await expect(page.getByText(/Svarna Gauranga Das/i).first()).toBeVisible();
    await expect(page.locator('a[href="mailto:svarnagaurangdas@gmail.com"]').first()).toBeVisible();
  });
});

test.describe("v1.1 reader leak regression", () => {
  test("story read panel excludes production metadata markers", async ({ page }) => {
    await page.goto("/stories/001");
    const readTab = page.getByRole("tab", { name: /^Read$/i });
    if (await readTab.count()) {
      await readTab.click();
    }
    const panel = page.locator("[role='tabpanel']").first();
    const text = await panel.innerText();
    for (const pattern of LEAK) {
      expect(text).not.toMatch(pattern);
    }
  });

  test("source tab shows reviewed Vedabase or honest pending state", async ({ page }) => {
    await page.goto("/stories/001");
    const sourceTab = page.getByRole("tab", { name: /Source/i });
    await sourceTab.click();
    const vedabase = page.getByRole("link", { name: /Open in Vedabase/i });
    const pending = page.getByText(/Vedabase link pending|needs-review|Reviewed source|Package reference|Pending catalog/i);
    await expect(vedabase.or(pending).first()).toBeVisible();
  });
});
