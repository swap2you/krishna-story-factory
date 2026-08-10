import { afterEach, describe, expect, it, vi } from "vitest";

describe("PUBLIC_STORY_MAX defaults", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("defaults to 25 when env is unset", async () => {
    vi.stubEnv("NEXT_PUBLIC_BHAVA_PUBLIC_STORY_MAX", "");
    vi.stubEnv("BHAVA_PUBLIC_STORY_MAX", "");
    const mod = await import("./public-boundary");
    expect(mod.PUBLIC_STORY_MAX).toBe(25);
  });

  it("falls back to 25 when env parses invalid", async () => {
    vi.stubEnv("NEXT_PUBLIC_BHAVA_PUBLIC_STORY_MAX", "nope");
    vi.stubEnv("BHAVA_PUBLIC_STORY_MAX", "nope");
    const mod = await import("./public-boundary");
    expect(mod.PUBLIC_STORY_MAX).toBe(25);
  });

  it("honors a valid override", async () => {
    vi.stubEnv("NEXT_PUBLIC_BHAVA_PUBLIC_STORY_MAX", "22");
    const mod = await import("./public-boundary");
    expect(mod.PUBLIC_STORY_MAX).toBe(22);
  });
});
