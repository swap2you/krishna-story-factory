import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  CANONICAL_ORIGIN,
  DEFAULT_OG_HEIGHT,
  DEFAULT_OG_IMAGE,
  DEFAULT_OG_WIDTH,
  pageMetadata,
} from "./seo";

describe("social share metadata", () => {
  it("uses absolute canonical origin and sized OG defaults", () => {
    expect(CANONICAL_ORIGIN).toBe("https://bhava.me");
    expect(DEFAULT_OG_IMAGE).toBe("/og/bhava-share-1200x630.webp");
    expect(DEFAULT_OG_WIDTH).toBe(1200);
    expect(DEFAULT_OG_HEIGHT).toBe(630);
    const asset = join(__dirname, "..", "public", "og", "bhava-share-1200x630.webp");
    expect(readFileSync(asset).byteLength).toBeGreaterThan(10_000);
  });

  it("emits og and twitter fields for pages", () => {
    const meta = pageMetadata({
      title: "Bhāva home",
      description: "Devotional learning",
      path: "/",
    });
    expect(meta.alternates?.canonical).toBe("https://bhava.me/");
    const og = meta.openGraph as {
      images?: Array<{ url?: string; width?: number; height?: number }>;
    };
    expect(og.images?.[0]?.url).toBe("https://bhava.me/og/bhava-share-1200x630.webp");
    expect(og.images?.[0]?.width).toBe(1200);
    expect(og.images?.[0]?.height).toBe(630);
    const twitter = meta.twitter as { card?: string; images?: string[] };
    expect(twitter.card).toBe("summary_large_image");
    expect(twitter.images?.[0]).toBe("https://bhava.me/og/bhava-share-1200x630.webp");
  });
});
