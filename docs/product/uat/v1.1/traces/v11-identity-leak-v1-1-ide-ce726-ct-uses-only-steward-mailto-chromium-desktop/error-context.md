# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: v11-identity-leak.spec.ts >> v1.1 identity and route smoke >> contact uses only steward mailto
- Location: e2e\v11-identity-leak.spec.ts:40:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('a[href="mailto:swarnagaurangadas@gmail.com"]')
Expected: visible
Error: strict mode violation: locator('a[href="mailto:swarnagaurangadas@gmail.com"]') resolved to 2 elements:
    1) <a class="bhava-button bhava-button--accent" href="mailto:swarnagaurangadas@gmail.com">…</a> aka getByRole('link', { name: 'Email Svarna Gauranga Das' })
    2) <a href="mailto:swarnagaurangadas@gmail.com">swarnagaurangadas@gmail.com</a> aka getByRole('link', { name: 'swarnagaurangadas@gmail.com' })

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('a[href="mailto:swarnagaurangadas@gmail.com"]')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - generic [ref=e4]:
        - link "Bhāva home" [ref=e5] [cursor=pointer]:
          - /url: /
          - img [ref=e6]
          - generic [ref=e7]:
            - generic [ref=e8]: bhāva
            - generic [ref=e9]: Devotional learning
        - navigation "Primary navigation" [ref=e10]:
          - link "Home" [ref=e11] [cursor=pointer]:
            - /url: /
          - link "Library" [ref=e12] [cursor=pointer]:
            - /url: /library
          - link "For Teachers" [ref=e13] [cursor=pointer]:
            - /url: /teachers
          - link "Prabhupāda Vāṇī" [ref=e14] [cursor=pointer]:
            - /url: /prabhupada-vani
          - link "Bhakti Blog" [ref=e15] [cursor=pointer]:
            - /url: /blog
          - link "About" [ref=e16] [cursor=pointer]:
            - /url: /about
          - link "Contact" [ref=e17] [cursor=pointer]:
            - /url: /contact
    - main [ref=e18]:
      - generic [ref=e20]:
        - paragraph [ref=e21]: Contact
        - heading "Let's stay in touch." [level=1] [ref=e22]
        - paragraph [ref=e23]: Bhāva is stewarded with care. Reach out for questions, feedback, or partnership ideas.
      - generic [ref=e25]:
        - article [ref=e26]:
          - paragraph [ref=e27]: Steward
          - heading "Svarna Gauranga Das" [level=2] [ref=e28]
          - paragraph [ref=e29]: For families, teachers, and partners who want a calm home for Krishna Book learning.
          - link "Email Svarna Gauranga Das" [ref=e31] [cursor=pointer]:
            - /url: mailto:swarnagaurangadas@gmail.com
        - article [ref=e32]:
          - paragraph [ref=e33]: Links
          - heading "Find Bhāva online" [level=2] [ref=e34]
          - paragraph [ref=e35]:
            - link "swarnagaurangadas@gmail.com" [ref=e36] [cursor=pointer]:
              - /url: mailto:swarnagaurangadas@gmail.com
          - paragraph [ref=e37]:
            - link "Privacy" [ref=e38] [cursor=pointer]:
              - /url: /privacy
            - text: ·
            - link "Sources" [ref=e39] [cursor=pointer]:
              - /url: /source-permissions
    - contentinfo [ref=e40]:
      - generic [ref=e41]:
        - generic [ref=e42]: Bhāva — stewarded with care by Svarna Gauranga Das.
        - generic [ref=e43]:
          - link "Sunday School" [ref=e44] [cursor=pointer]:
            - /url: /sunday-school
          - link "For Preachers" [ref=e45] [cursor=pointer]:
            - /url: /preachers
          - link "Privacy" [ref=e46] [cursor=pointer]:
            - /url: /privacy
          - link "Accessibility" [ref=e47] [cursor=pointer]:
            - /url: /accessibility
          - link "Source & permissions" [ref=e48] [cursor=pointer]:
            - /url: /source-permissions
  - alert [ref=e49]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | const FORBIDDEN = [/Swapnil/i, /swapnilpatil/i, /linkedin\.com/i, /github\.com/i];
  4  | const LEAK = [
  5  |   /Audio Narration/i,
  6  |   /Poster Visual Brief/i,
  7  |   /Coloring Visual Brief/i,
  8  |   /Activity Data/i,
  9  |   /<break time=/i,
  10 | ];
  11 | 
  12 | const PUBLIC_ROUTES = [
  13 |   "/",
  14 |   "/library",
  15 |   "/library/krishna-book",
  16 |   "/library/srimad-bhagavatam",
  17 |   "/sunday-school",
  18 |   "/preachers",
  19 |   "/teachers",
  20 |   "/prabhupada-vani",
  21 |   "/blog",
  22 |   "/about",
  23 |   "/contact",
  24 |   "/privacy",
  25 |   "/source-permissions",
  26 | ];
  27 | 
  28 | test.describe("v1.1 identity and route smoke", () => {
  29 |   for (const route of PUBLIC_ROUTES) {
  30 |     test(`public route ${route} has no civil identity leakage`, async ({ page }) => {
  31 |       const response = await page.goto(route);
  32 |       expect(response?.ok() || response?.status() === 304).toBeTruthy();
  33 |       const body = await page.locator("body").innerText();
  34 |       for (const pattern of FORBIDDEN) {
  35 |         expect(body).not.toMatch(pattern);
  36 |       }
  37 |     });
  38 |   }
  39 | 
  40 |   test("contact uses only steward mailto", async ({ page }) => {
  41 |     await page.goto("/contact");
  42 |     await expect(page.getByText(/Svarna Gauranga Das/i).first()).toBeVisible();
> 43 |     await expect(page.locator('a[href="mailto:swarnagaurangadas@gmail.com"]')).toBeVisible();
     |                                                                                ^ Error: expect(locator).toBeVisible() failed
  44 |   });
  45 | });
  46 | 
  47 | test.describe("v1.1 reader leak regression", () => {
  48 |   test("story read panel excludes production metadata markers", async ({ page }) => {
  49 |     await page.goto("/stories/001");
  50 |     const readTab = page.getByRole("tab", { name: /^Read$/i });
  51 |     if (await readTab.count()) {
  52 |       await readTab.click();
  53 |     }
  54 |     const panel = page.locator("[role='tabpanel']").first();
  55 |     const text = await panel.innerText();
  56 |     for (const pattern of LEAK) {
  57 |       expect(text).not.toMatch(pattern);
  58 |     }
  59 |   });
  60 | 
  61 |   test("source tab shows reviewed Vedabase or honest pending state", async ({ page }) => {
  62 |     await page.goto("/stories/001");
  63 |     const sourceTab = page.getByRole("tab", { name: /Source/i });
  64 |     await sourceTab.click();
  65 |     const vedabase = page.getByRole("link", { name: /Open in Vedabase/i });
  66 |     const pending = page.getByText(/Vedabase link pending|needs-review|Reviewed source|Package reference|Pending catalog/i);
  67 |     await expect(vedabase.or(pending).first()).toBeVisible();
  68 |   });
  69 | });
  70 | 
```