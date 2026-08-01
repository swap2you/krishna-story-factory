import { expect, test, type Page } from "@playwright/test";

const destinations = [
  { label: "Children & Youth", href: /\/learning\/children-youth\/?$/ },
  { label: "Sunday School", href: /\/sunday-school\/?$/ },
  { label: "For Teachers", href: /\/teachers\/?$/ },
  { label: "For Preachers", href: /\/preachers\/?$/ },
  { label: "Printables", href: /\/printables\/?$/ },
] as const;

async function openPrimaryNavIfNeeded(page: Page) {
  const menu = page.getByRole("button", { name: /^Menu$/i });
  if (await menu.isVisible().catch(() => false)) {
    await menu.click();
  }
}

function learningButton(page: Page) {
  return page.getByRole("navigation", { name: "Primary navigation" }).getByRole("button", { name: /^Learning$/i });
}

function learningMenu(page: Page) {
  return page.locator(".nav-learning__menu");
}

test.describe("Learning menu", () => {
  test("starts closed and has no permanently visible panel", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const menu = learningMenu(page);
    await expect(menu).toHaveAttribute("data-state", "closed");
    await expect(menu).toBeHidden();
    await expect(learningButton(page)).toHaveAttribute("aria-expanded", "false");
  });

  test("click opens and second click closes", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const button = learningButton(page);
    await button.click();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open");
    await expect(learningMenu(page)).toBeVisible();
    await button.click();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "closed");
    await expect(learningMenu(page)).toBeHidden();
  });

  test("keyboard Enter/Space toggle and Escape restore focus", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    const button = learningButton(page);
    await button.focus();
    await page.keyboard.press("Enter");
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open");
    await page.keyboard.press("Escape");
    await expect(learningMenu(page)).toHaveAttribute("data-state", "closed");
    await expect(button).toBeFocused();
    await button.focus();
    await page.keyboard.press(" ");
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open");
  });

  test("outside click closes", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    await learningButton(page).click();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open");
    await page.locator(".brand-lockup").click({ force: true });
    await expect(learningMenu(page)).toHaveAttribute("data-state", "closed");
  });

  test("route navigation closes the menu", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    await learningButton(page).click();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open");
    await learningMenu(page).getByRole("link", { name: "For Teachers" }).click();
    await expect(page).toHaveURL(/\/teachers\/?$/);
    await openPrimaryNavIfNeeded(page);
    await expect(learningMenu(page)).toHaveAttribute("data-state", "closed");
    await expect(learningMenu(page)).toBeHidden();
  });

  test("no horizontal overflow when open", async ({ page }) => {
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    await learningButton(page).click();
    await expect(learningMenu(page)).toBeVisible();
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
      await learningButton(page).click();
      await learningMenu(page).getByRole("link", { name: dest.label }).click();
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

    const root = page.locator(".nav-learning");
    await root.hover();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "open", { timeout: 5_000 });
    await page.locator(".brand-lockup").hover();
    await expect(learningMenu(page)).toHaveAttribute("data-state", "closed", { timeout: 5_000 });
  });
});

test.describe("Learning menu mobile accordion", () => {
  test("opens as inline accordion under Learning", async ({ page }, testInfo) => {
    test.skip(!/mobile/i.test(testInfo.project.name), "Accordion layout is mobile viewport");
    await page.goto("/");
    await openPrimaryNavIfNeeded(page);
    await learningButton(page).click();
    const menu = learningMenu(page);
    await expect(menu).toHaveAttribute("data-state", "open");
    await expect(menu).toBeVisible();
    const geometry = await page.evaluate(() => {
      const learning = document.querySelector(".nav-learning") as HTMLElement | null;
      const panel = document.querySelector(".nav-learning__menu") as HTMLElement | null;
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
