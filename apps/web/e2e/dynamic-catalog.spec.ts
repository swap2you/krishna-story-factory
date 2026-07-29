import { expect, test } from "@playwright/test";
import { apiURL, fetchStories } from "./helpers";

test.describe("dynamic catalog", () => {
  test("API stories endpoint returns ordered publishable packages", async ({ request }) => {
    const stories = await fetchStories(request);
    expect(stories.length).toBeGreaterThan(0);
    const numbers = stories.map((s) => s.story_no);
    const sorted = [...numbers].sort();
    expect(numbers).toEqual(sorted);
    const health = await request.get(`${apiURL}/health`);
    expect(health.ok()).toBeTruthy();
  });
});
