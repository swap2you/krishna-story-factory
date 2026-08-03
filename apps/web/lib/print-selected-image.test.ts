import { describe, expect, it } from "vitest";
import {
  buildIsolatedPrintHtmlForTest,
  isAllowedPrintAssetUrl,
  printableImageDocumentContract,
} from "./print-selected-image";

describe("printSelectedImage isolation contract", () => {
  const poster = "/api/v1/stories/001/assets/story_poster.png";
  const simple = "/api/v1/stories/001/assets/simple_coloring_page.png";
  const detailed = "/api/v1/stories/001/assets/coloring_page.png";
  const allowed = [poster, simple, detailed];

  it("allows only known story asset URLs", () => {
    expect(isAllowedPrintAssetUrl(poster, allowed)).toBe(true);
    expect(isAllowedPrintAssetUrl(simple, allowed)).toBe(true);
    expect(isAllowedPrintAssetUrl("https://evil.example/x.png", allowed)).toBe(false);
    expect(isAllowedPrintAssetUrl("/api/v1/stories/002/assets/story_poster.png", allowed)).toBe(false);
  });

  it("builds a printable document with only the selected poster", () => {
    const html = buildIsolatedPrintHtmlForTest(poster, "Story poster");
    const contract = printableImageDocumentContract(html, poster);
    expect(contract.hasTargetImage).toBe(true);
    expect(html).not.toMatch(/Simple coloring|Detailed coloring/i);
    expect(html).not.toMatch(/carousel-thumb|asset-tile|site-header|mini-player/i);
    expect(html.match(/<img\b/gi)?.length).toBe(1);
  });

  it("builds a printable document with only simple coloring", () => {
    const html = buildIsolatedPrintHtmlForTest(simple, "Simple coloring");
    expect(html).toContain(simple);
    expect(html).not.toContain(poster);
    expect(html).not.toContain(detailed);
  });

  it("builds a printable document with only detailed coloring", () => {
    const html = buildIsolatedPrintHtmlForTest(detailed, "Detailed coloring");
    expect(html).toContain(detailed);
    expect(html).not.toContain(poster);
    expect(html).not.toContain(simple);
  });

  it("changing the selected URL changes the print target", () => {
    const a = buildIsolatedPrintHtmlForTest(poster, "Story poster");
    const b = buildIsolatedPrintHtmlForTest(simple, "Simple coloring");
    expect(a).toContain(poster);
    expect(b).toContain(simple);
    expect(a).not.toContain(simple);
    expect(b).not.toContain(poster);
  });
});
