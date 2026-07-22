const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const routes = [
    ["home", "http://localhost:3000/"],
    ["library", "http://localhost:3000/library"],
    ["krishna-book", "http://localhost:3000/library/krishna-book"],
    ["story-001", "http://localhost:3000/stories/001"],
    ["story-007", "http://localhost:3000/stories/007"],
    ["teachers", "http://localhost:3000/teachers"],
    ["vanani", "http://localhost:3000/vanani"],
    ["blog", "http://localhost:3000/blog"],
    ["about", "http://localhost:3000/about"],
    ["contact", "http://localhost:3000/contact"],
    ["studio", "http://localhost:3000/studio"],
  ];
  for (const [name, url] of routes) {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(800);
    await page.screenshot({ path: `docs/product/screenshots/${name}.png`, fullPage: true });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("http://localhost:3000/", { waitUntil: "domcontentloaded" });
  await page.screenshot({ path: "docs/product/screenshots/home-mobile.png", fullPage: true });
  await browser.close();
  console.log("SCREENSHOTS_OK");
})().catch((e) => { console.error(e); process.exit(1); });
