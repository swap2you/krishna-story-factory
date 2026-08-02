import { afterEach, describe, expect, it, vi } from "vitest";

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
  vi.resetModules();
});

describe("loadStories catalog client", () => {
  it("returns ok with stories for a successful response", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ story_no: "001", slug: "earth", title: "The Earth Prays for Krishna to Come" }],
    }) as unknown as typeof fetch;

    const { loadStories } = await import("./catalog");
    const state = await loadStories();
    expect(state.status).toBe("ok");
    if (state.status === "ok") {
      expect(state.stories).toHaveLength(1);
      expect(state.stories[0].title).toMatch(/Earth Prays/i);
    }
  });

  it("distinguishes HTTP 500 from an empty catalog", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({}),
    }) as unknown as typeof fetch;

    const { loadStories } = await import("./catalog");
    const state = await loadStories();
    expect(state).toEqual({ status: "unavailable", reason: "http_error", httpStatus: 500 });
  });

  it("distinguishes timeouts", async () => {
    globalThis.fetch = vi.fn().mockImplementation(() => {
      const error = new Error("aborted");
      error.name = "AbortError";
      return Promise.reject(error);
    }) as unknown as typeof fetch;

    const { loadStories } = await import("./catalog");
    const state = await loadStories();
    expect(state).toEqual({ status: "unavailable", reason: "timeout" });
  });

  it("distinguishes invalid JSON", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => {
        throw new Error("bad json");
      },
    }) as unknown as typeof fetch;

    const { loadStories } = await import("./catalog");
    const state = await loadStories();
    expect(state).toEqual({ status: "unavailable", reason: "invalid_json", httpStatus: 200 });
  });

  it("treats a successful empty array as ok empty, not unavailable", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    }) as unknown as typeof fetch;

    const { loadStories } = await import("./catalog");
    const state = await loadStories();
    expect(state).toEqual({ status: "ok", stories: [] });
  });
});
