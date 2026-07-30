import { defineConfig, devices } from "@playwright/test";

const webURL = process.env.BHAVA_WEB_URL ?? "http://127.0.0.1:3000";
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: isCI ? 3 : undefined,
  reporter: [["list"], ["json", { outputFile: process.env.BHAVA_UAT_BROWSER_RESULTS ?? "test-results/browser-results.json" }]],
  use: {
    baseURL: webURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium-desktop", use: { ...devices["Desktop Chrome"] }, testIgnore: /launch-screenshots\.spec\.ts/ },
    {
      name: "firefox-desktop",
      use: {
        ...devices["Desktop Firefox"],
        launchOptions: {
          firefoxUserPrefs: {
            "media.autoplay.default": 0,
            "media.autoplay.enabled.user-gestures-needed": false,
            "media.autoplay.blocking_policy": 0,
          },
        },
      },
      testIgnore: /launch-screenshots\.spec\.ts/,
    },
    { name: "webkit-desktop", use: { ...devices["Desktop Safari"] }, testIgnore: /launch-screenshots\.spec\.ts/ },
    { name: "chromium-mobile", use: { ...devices["Pixel 5"] }, testIgnore: /launch-screenshots\.spec\.ts/ },
    { name: "webkit-mobile", use: { ...devices["iPhone 13"] }, testIgnore: /launch-screenshots\.spec\.ts/ },
    {
      name: "screenshots",
      testMatch: /launch-screenshots\.spec\.ts/,
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // External UAT runner starts API+web; local `npm run test:e2e` may set BHAVA_WEB_URL to an already-running instance.
  webServer: process.env.BHAVA_WEB_URL
    ? undefined
    : {
        command: "npm run dev -- -p 3000 -H 127.0.0.1",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: !isCI,
        timeout: 180_000,
      },
});
