import { defineConfig, devices } from "@playwright/test";

const webURL = process.env.BHAVA_WEB_URL ?? "http://127.0.0.1:3000";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["json", { outputFile: process.env.BHAVA_UAT_BROWSER_RESULTS ?? "test-results/browser-results.json" }]],
  use: {
    baseURL: webURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium-desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox-desktop", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit-desktop", use: { ...devices["Desktop Safari"] } },
    { name: "chromium-mobile", use: { ...devices["Pixel 5"] } },
    { name: "webkit-mobile", use: { ...devices["iPhone 13"] } },
  ],
  // External UAT runner starts API+web; local `npm run test:e2e` may set BHAVA_WEB_URL to an already-running instance.
  webServer: process.env.BHAVA_WEB_URL
    ? undefined
    : {
        command: "npm run dev -- -p 3000 -H 127.0.0.1",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
      },
});
