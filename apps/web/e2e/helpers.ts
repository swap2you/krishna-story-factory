import { expect, type APIRequestContext, type Page } from "@playwright/test";

export const webURL = process.env.BHAVA_WEB_URL ?? "http://127.0.0.1:3000";
export const apiURL = (process.env.BHAVA_API_URL ?? "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export async function fetchStories(request: APIRequestContext) {
  const response = await request.get(`${apiURL}/stories`);
  expect(response.ok()).toBeTruthy();
  return (await response.json()) as Array<{ story_no: string; title: string; poster_url?: string }>;
}

export async function expectNoCriticalAxe(page: Page) {
  // Lazy import so unit tooling without browsers still loads helpers.
  const AxeBuilder = (await import("@axe-core/playwright")).default;
  const results = await new AxeBuilder({ page }).analyze();
  const serious = results.violations.filter((v) => v.impact === "critical" || v.impact === "serious");
  expect(serious, JSON.stringify(serious, null, 2)).toEqual([]);
}
