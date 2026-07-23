# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pdf-and-images.spec.ts >> pdf and images >> activity PDF and coloring lightbox work
- Location: e2e\pdf-and-images.spec.ts:5:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: /^print$/i })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('button', { name: /^print$/i })

```

```yaml
- banner:
  - link "Bhāva home":
    - /url: /
    - text: bhāva Devotional learning
  - navigation "Primary navigation":
    - link "Home":
      - /url: /
    - link "Library":
      - /url: /library
    - link "For Teachers":
      - /url: /teachers
    - link "Prabhupāda Vāṇī":
      - /url: /prabhupada-vani
    - link "Bhakti Blog":
      - /url: /blog
    - link "About":
      - /url: /about
    - link "Contact":
      - /url: /contact
- main:
  - complementary:
    - link "← Krishna Book":
      - /url: /library/krishna-book
    - img "The Earth Prays for Krishna to Come story poster"
    - paragraph: Story 001
    - heading "The Earth Prays for Krishna to Come" [level=2]
    - paragraph: Suggested for 6-12
    - paragraph: Krishna Book Chapter 1
  - paragraph: Listen · Read · Activities
  - heading "The Earth Prays for Krishna to Come" [level=1]
  - text: PASS
  - img "Narration waveform"
  - button "Play"
  - button "Back 15 seconds": −15s
  - button "Forward 15 seconds": +15s
  - text: Speed
  - combobox "Playback speed":
    - option "0.75×"
    - option "1×" [selected]
    - option "1.25×"
    - option "1.5×"
    - option "2×"
  - text: Volume
  - slider "Volume": "1"
  - text: 0:00 / −4:02
  - button "Bookmark position"
  - button "Jump to bookmark"
  - text: Sleep timer
  - combobox "Sleep timer":
    - option "Off" [selected]
    - option "5 min"
    - option "15 min"
    - option "30 min"
  - link "Download audio":
    - /url: /api/v1/stories/001/assets/narration.mp3
  - paragraph: "Keyboard: Space play/pause · ← −15s · → +15s. Progress resumes on this device."
  - navigation "Story navigation":
    - link "Story 002 →":
      - /url: /stories/002
  - tablist:
    - tab "Listen"
    - tab "Read"
    - tab "Activities" [selected]
    - tab "Coloring"
    - tab "Source"
    - tab "Notes"
    - tab "Ślokās"
  - tabpanel:
    - heading "Activity sheet" [level=2]
    - link "Open full tab":
      - /url: /api/v1/stories/001/assets/activity_sheet.pdf
    - link "Download PDF":
      - /url: /api/v1/stories/001/assets/activity_sheet.pdf
    - button "Open to print"
    - iframe
    - paragraph: Opens the PDF in a new tab — use your browser’s print command from there.
- contentinfo:
  - text: Bhāva — stewarded with care by Svarna Gauranga Das.
  - link "Sunday School":
    - /url: /sunday-school
  - link "For Preachers":
    - /url: /preachers
  - link "Privacy":
    - /url: /privacy
  - link "Accessibility":
    - /url: /accessibility
  - link "Source & permissions":
    - /url: /source-permissions
- alert
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | import { fetchStories } from "./helpers";
  3  | 
  4  | test.describe("pdf and images", () => {
  5  |   test("activity PDF and coloring lightbox work", async ({ page, request }) => {
  6  |     const stories = await fetchStories(request);
  7  |     test.skip(!stories.length, "No catalog stories available");
  8  |     await page.goto(`/stories/${stories[0].story_no}`);
  9  | 
  10 |     await page.getByRole("tab", { name: "Activities" }).click();
  11 |     await expect(page.getByRole("link", { name: /download pdf/i })).toBeVisible();
> 12 |     await expect(page.getByRole("button", { name: /^print$/i })).toBeVisible();
     |                                                                  ^ Error: expect(locator).toBeVisible() failed
  13 | 
  14 |     await page.getByRole("tab", { name: "Coloring" }).click();
  15 |     const tile = page.locator(".asset-tile").first();
  16 |     await expect(tile).toBeVisible();
  17 |     await tile.click();
  18 |     const dialog = page.getByRole("dialog");
  19 |     await expect(dialog).toBeVisible();
  20 |     await page.keyboard.press("Escape");
  21 |     await expect(dialog).toHaveCount(0);
  22 |   });
  23 | });
  24 | 
```