import { afterEach, describe, expect, it } from "vitest";
import { formatFooterReleaseLine, getBhavaReleaseMeta } from "./release-meta";

const KEYS = [
  "NEXT_PUBLIC_BHAVA_WEB_VERSION",
  "NEXT_PUBLIC_BHAVA_CONTENT_RELEASE",
  "NEXT_PUBLIC_BHAVA_GIT_SHA",
] as const;

describe("release-meta", () => {
  const saved: Partial<Record<(typeof KEYS)[number], string | undefined>> = {};

  afterEach(() => {
    for (const key of KEYS) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
      delete saved[key];
    }
  });

  it("formats a subordinate footer release line", () => {
    const line = formatFooterReleaseLine({
      webVersion: "001-020-v3",
      contentRelease: "bhava-content-001-020-v3",
      gitSha: "30e720cd22cb333e087b3d5e48faeac0056dcde3",
      shortSha: "30e720c",
    });
    expect(line).toBe("Bhāva Web 001-020-v3 · Content 001 020 v3 · Build 30e720c");
  });

  it("shortens SHA and falls back safely", () => {
    for (const key of KEYS) saved[key] = process.env[key];
    process.env.NEXT_PUBLIC_BHAVA_WEB_VERSION = "001-020-v3";
    process.env.NEXT_PUBLIC_BHAVA_CONTENT_RELEASE = "bhava-content-001-020-v3";
    process.env.NEXT_PUBLIC_BHAVA_GIT_SHA = "abcdef0123456789";
    const meta = getBhavaReleaseMeta();
    expect(meta.shortSha).toBe("abcdef0");
    expect(formatFooterReleaseLine(meta)).toContain("Build abcdef0");
  });
});
