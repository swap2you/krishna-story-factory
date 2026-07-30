import { describe, expect, it } from "vitest";
import { renderMarkdown } from "./story-experience";

describe("renderMarkdown", () => {
  it("keeps a list that follows prose out of the paragraph", () => {
    // Released story bodies put bullets directly under a lead-in line. Wrapping
    // that in <p> produced <ul> inside <p> with <br/> between the items, which
    // axe reports as a serious "only-listitems" violation.
    const html = renderMarkdown("Ask your child:\n- What did Kṛṣṇa do?\n- Why was it merciful?");
    expect(html).toContain("<p>Ask your child:</p>");
    expect(html).toContain("<ul><li>What did Kṛṣṇa do?</li><li>Why was it merciful?</li></ul>");
    expect(html).not.toMatch(/<ul>(?:(?!<\/ul>)[^])*<br\/?>/);
    expect(html).not.toMatch(/<p>(?:(?!<\/p>)[^])*<ul>/);
  });

  it("renders headings as their own blocks", () => {
    const html = renderMarkdown("# Title\n\n## Rights and Credits\n\nBody text");
    expect(html).toContain("<h1>Title</h1>");
    expect(html).toContain("<h2>Rights and Credits</h2>");
    expect(html).toContain("<p>Body text</p>");
  });

  it("joins soft-wrapped paragraph lines with line breaks", () => {
    expect(renderMarkdown("first line\nsecond line")).toBe("<p>first line<br/>second line</p>");
  });

  it("escapes markup before applying inline formatting", () => {
    const html = renderMarkdown("<script>alert(1)</script> and **bold**");
    expect(html).not.toContain("<script>");
    expect(html).toContain("&lt;script&gt;");
    expect(html).toContain("<strong>bold</strong>");
  });
});
