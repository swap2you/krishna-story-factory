import { expect, test, type Page } from "@playwright/test";

const destinations = [
  { label: "Learning Hub", href: /\/learning\/?$/ },
  { label: "Children & Youth", href: /\/learning\/children-youth\/?$/ },
  { label: "Families", href: /\/learning\/families\/?$/ },
  { label: "Sunday School", href: /\/sunday-school\/?$/ },
  { label: "For Teachers", href: /\/teachers\/?$/ },
  { label: "For Preachers", href: /\/preachers\/?$/ },
  { label: "Gurukula / Homeschool", href: /\/learning\/gurukula-homeschool\/?$/ },
  { label: "Festival use", href: /\/learning\/festivals\/?$/ },
  { label: "Printables", href: /\/printables\/?$/ },
] as const;

async function openPrimaryNavIfNeeded(page: Page) {
  const menu = page.getByRole("button", { name: /^Menu$/i });
  if (await menu.isVisible().catch(() => false)) {
    await menu.click();
  }
}

async function isMobileLearning(page: Page) {
  return page.evaluate(() => {
    const el = document.querySelector(".nav-learning--mobile");
    return !!el && getComputedStyle(el).display !== "none";
  });
}

function learningButton(page: Page) {
  return page
    .getByRole("navigation", { name: "Primary navigation" })
    .getByRole("button", { name: /^Learning$/i });
}

function learningMenu(page: Page, mobile: boolean) {
  return mobile
    ? page.locator(".nav-learning--mobile .nav-learning__menu")
    : page.locator(".nav-learning--desktop .nav-learning__menu");
}

test.describe("Learning menu", () => {
  test("starts closed and has no permanently visible panel", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const menu = learningMenu(page, mobile);
    await expect(menu).toHaveAttribute("data-state", "closed");
    await expect(menu).toBeHidden();
    await expect(learningButton(page)).toHaveAttribute("aria-expanded", "false");
  });

  test("click opens and second click closes", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const button = learningButton(page);
    const menu = learningMenu(page, mobile);
    await button.click();
    await expect(menu).toHaveAttribute("data-state", "open");
    await expect(menu).toBeVisible();
    await button.click();
    await expect(menu).toHaveAttribute("data-state", "closed");
    await expect(menu).toBeHidden();
  });

  test("keyboard Enter/Space toggle and Escape restore focus", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const button = learningButton(page);
    const menu = learningMenu(page, mobile);
    await button.focus();
    await page.keyboard.press("Enter");
    await expect(menu).toHaveAttribute("data-state", "open");
    await page.keyboard.press("Escape");
    await expect(menu).toHaveAttribute("data-state", "closed");
    if (!mobile) {
      await expect(button).toBeFocused();
    }
    await button.focus();
    await page.keyboard.press(" ");
    await expect(menu).toHaveAttribute("data-state", "open");
  });

  test("outside click closes", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const menu = learningMenu(page, mobile);
    await learningButton(page).click();
    await expect(menu).toHaveAttribute("data-state", "open");
    if (mobile) {
      await page.keyboard.press("Escape");
    } else {
      await page.locator(".brand-lockup").click({ force: true });
    }
    await expect(menu).toHaveAttribute("data-state", "closed");
  });

  test("route navigation closes the menu", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    const menu = learningMenu(page, mobile);
    await learningButton(page).click();
    await expect(menu).toHaveAttribute("data-state", "open");
    await menu.getByRole("link", { name: "For Teachers" }).click();
    await expect(page).toHaveURL(/\/teachers\/?$/);
    await openPrimaryNavIfNeeded(page);
    await expect(learningMenu(page, mobile)).toHaveAttribute("data-state", "closed");
    await expect(learningMenu(page, mobile)).toBeHidden();
  });

  test("no horizontal overflow when open", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const mobile = await isMobileLearning(page);
    await learningButton(page).click();
    await expect(learningMenu(page, mobile)).toBeVisible();
    const overflow = await page.evaluate(() => {
      const doc = document.documentElement;
      return doc.scrollWidth > doc.clientWidth + 1;
    });
    expect(overflow).toBeFalsy();
  });

  for (const dest of destinations) {
    test(`navigates to ${dest.label}`, async ({ page }) => {
      await page.goto("/");
      await openPrimaryNavIfNeeded(page);
      const mobile = await isMobileLearning(page);
      await learningButton(page).click();
      await learningMenu(page, mobile).getByRole("link", { name: dest.label }).click();
      await expect(page).toHaveURL(dest.href);
    });
  }
});

test.describe("Learning menu desktop hover", () => {
  test("hover opens and leaving closes after delay", async ({ page }, testInfo) => {
    test.skip(!/desktop/i.test(testInfo.project.name), "Hover enhancement is desktop-only");
    await page.goto("/");
    const fineHover = await page.evaluate(
      () => window.matchMedia("(hover: hover) and (pointer: fine)").matches,
    );
    test.skip(!fineHover, "Browser/project does not advertise fine hover");

    const root = page.locator(".nav-learning--desktop");
    await root.hover();
    await expect(learningMenu(page, false)).toHaveAttribute("data-state", "open", { timeout: 5_000 });
    await page.locator(".brand-lockup").hover();
    await expect(learningMenu(page, false)).toHaveAttribute("data-state", "closed", { timeout: 5_000 });
  });
});

test.describe("Learning menu mobile accordion", () => {
  test("opens as inline accordion under Learning", async ({ page }, testInfo) => {
    test.skip(!/mobile/i.test(testInfo.project.name), "Accordion layout is mobile viewport");
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    await learningButton(page).click();
    const menu = learningMenu(page, true);
    await expect(menu).toHaveAttribute("data-state", "open");
    await expect(menu).toBeVisible();
    const geometry = await page.evaluate(() => {
      const learning = document.querySelector(".nav-learning--mobile") as HTMLElement | null;
      const panel = document.querySelector(
        ".nav-learning--mobile .nav-learning__menu",
      ) as HTMLElement | null;
      if (!learning || !panel) return null;
      const lr = learning.getBoundingClientRect();
      const pr = panel.getBoundingClientRect();
      const style = getComputedStyle(panel);
      return {
        position: style.position,
        below: pr.top >= lr.top,
        widthOk: pr.width <= lr.width + 2,
      };
    });
    expect(geometry).toBeTruthy();
    expect(geometry!.position).toBe("static");
    expect(geometry!.below).toBeTruthy();
    expect(geometry!.widthOk).toBeTruthy();
  });
});
