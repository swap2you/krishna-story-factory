# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: contact-and-static.spec.ts >> contact and static >> contact shows steward name and mailto CTA
- Location: e2e\contact-and-static.spec.ts:4:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/Svarna Gauranga Das/i)
Expected: visible
Error: strict mode violation: getByText(/Svarna Gauranga Das/i) resolved to 3 elements:
    1) <h2>Svarna Gauranga Das</h2> aka getByRole('heading', { name: 'Svarna Gauranga Das' })
    2) <a class="bhava-button bhava-button--accent" href="mailto:swarnagaurangadas@gmail.com">…</a> aka getByRole('link', { name: 'Email Svarna Gauranga Das' })
    3) <span>Bhāva — stewarded with care by Svarna Gauranga Da…</span> aka getByText('Bhāva — stewarded with care')

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText(/Svarna Gauranga Das/i)

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
          - generic [ref=e8]: bhāva
        - navigation "Primary navigation" [ref=e9]:
          - link "Home" [ref=e10] [cursor=pointer]:
            - /url: /
          - link "Library" [ref=e11] [cursor=pointer]:
            - /url: /library
          - link "For Teachers" [ref=e12] [cursor=pointer]:
            - /url: /teachers
          - link "Prabhupāda Vāṇī" [ref=e13] [cursor=pointer]:
            - /url: /prabhupada-vani
          - link "Bhakti Blog" [ref=e14] [cursor=pointer]:
            - /url: /blog
          - link "About" [ref=e15] [cursor=pointer]:
            - /url: /about
          - link "Contact" [ref=e16] [cursor=pointer]:
            - /url: /contact
    - main [ref=e17]:
      - generic [ref=e19]:
        - paragraph [ref=e20]: Contact
        - heading "Let's stay in touch." [level=1] [ref=e21]
        - paragraph [ref=e22]: Bhāva is stewarded with care. Reach out for questions, feedback, or partnership ideas.
      - generic [ref=e24]:
        - article [ref=e25]:
          - paragraph [ref=e26]: Steward
          - heading "Svarna Gauranga Das" [level=2] [ref=e27]
          - paragraph [ref=e28]: For families, teachers, and partners who want a calm home for Krishna Book learning.
          - link "Email Svarna Gauranga Das" [ref=e30] [cursor=pointer]:
            - /url: mailto:swarnagaurangadas@gmail.com
        - article [ref=e31]:
          - paragraph [ref=e32]: Links
          - heading "Find Bhāva online" [level=2] [ref=e33]
          - paragraph [ref=e34]:
            - link "swarnagaurangadas@gmail.com" [ref=e35] [cursor=pointer]:
              - /url: mailto:swarnagaurangadas@gmail.com
          - paragraph [ref=e36]:
            - link "Privacy" [ref=e37] [cursor=pointer]:
              - /url: /privacy
            - text: ·
            - link "Sources" [ref=e38] [cursor=pointer]:
              - /url: /source-permissions
    - contentinfo [ref=e39]:
      - generic [ref=e40]:
        - generic [ref=e41]: Bhāva — stewarded with care by Svarna Gauranga Das.
        - generic [ref=e42]:
          - link "Sunday School" [ref=e43] [cursor=pointer]:
            - /url: /sunday-school
          - link "For Preachers" [ref=e44] [cursor=pointer]:
            - /url: /preachers
          - link "Privacy" [ref=e45] [cursor=pointer]:
            - /url: /privacy
          - link "Accessibility" [ref=e46] [cursor=pointer]:
            - /url: /accessibility
          - link "Source & permissions" [ref=e47] [cursor=pointer]:
            - /url: /source-permissions
  - alert [ref=e48]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test.describe("contact and static", () => {
  4  |   test("contact shows steward name and mailto CTA", async ({ page }) => {
  5  |     await page.goto("/contact");
> 6  |     await expect(page.getByText(/Svarna Gauranga Das/i)).toBeVisible();
     |                                                          ^ Error: expect(locator).toBeVisible() failed
  7  |     await expect(page.locator('a[href^="mailto:swarnagaurangadas"]')).toBeVisible();
  8  |   });
  9  | 
  10 |   test("vanani redirects to prabhupada-vani", async ({ page }) => {
  11 |     await page.goto("/vanani");
  12 |     await expect(page).toHaveURL(/\/prabhupada-vani\/?$/);
  13 |     await expect(page.getByText(/Prabhupāda Vāṇī|timeless instruction/i).first()).toBeVisible();
  14 |   });
  15 | });
  16 | 
```