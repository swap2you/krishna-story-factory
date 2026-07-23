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
        - link "Bhāva home" [ref=e5]:
          - /url: /
          - img [ref=e6]
          - generic [ref=e7]:
            - generic [ref=e8]: bhāva
            - generic [ref=e9]: Devotional learning
        - navigation "Primary navigation" [ref=e10]:
          - link "Home" [ref=e11]:
            - /url: /
          - link "Library" [ref=e12]:
            - /url: /library
          - link "For Teachers" [ref=e13]:
            - /url: /teachers
          - link "Prabhupāda Vāṇī" [ref=e14]:
            - /url: /prabhupada-vani
          - link "Bhakti Blog" [ref=e15]:
            - /url: /blog
          - link "About" [ref=e16]:
            - /url: /about
          - link "Contact" [ref=e17]:
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
            - link "swarnagaurangadas@gmail.com" [ref=e36]:
              - /url: mailto:swarnagaurangadas@gmail.com
          - paragraph [ref=e37]:
            - link "Privacy" [ref=e38]:
              - /url: /privacy
            - text: ·
            - link "Sources" [ref=e39]:
              - /url: /source-permissions
    - contentinfo [ref=e40]:
      - generic [ref=e41]:
        - generic [ref=e42]: Bhāva — stewarded with care by Svarna Gauranga Das.
        - generic [ref=e43]:
          - link "Sunday School" [ref=e44]:
            - /url: /sunday-school
          - link "For Preachers" [ref=e45]:
            - /url: /preachers
          - link "Privacy" [ref=e46]:
            - /url: /privacy
          - link "Accessibility" [ref=e47]:
            - /url: /accessibility
          - link "Source & permissions" [ref=e48]:
            - /url: /source-permissions
  - alert [ref=e49]
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