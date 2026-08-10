/** @vitest-environment node */
import { describe, expect, it } from "vitest";
import {
  PUBLIC_KNOWLEDGE_PILOT_SLUGS,
  getProvenance,
  listArticles,
  listPublicPilotCatalog,
  listQuestions,
} from "@/lib/knowledge/loader";

describe("public Knowledge pilot catalog", () => {
  it("exposes the expected pilot slugs as public records", () => {
    const { guides, questions, total } = listPublicPilotCatalog();
    const slugs = [...guides, ...questions].map((d) => d.slug).sort();

    expect(total).toBe(PUBLIC_KNOWLEDGE_PILOT_SLUGS.length);
    expect(guides.length).toBe(4);
    expect(questions.length).toBe(3);
    expect(slugs).toEqual([...PUBLIC_KNOWLEDGE_PILOT_SLUGS].sort());
  });

  it("keeps listArticles / listQuestions counts aligned with the pilot", () => {
    const articles = listArticles();
    const questions = listQuestions();
    expect(articles.map((a) => a.slug).sort()).toEqual(
      [
        "family-bedtime-story-practice",
        "printing-and-classroom-use",
        "source-and-permissions",
        "what-is-bhava",
      ].sort(),
    );
    expect(questions.map((q) => q.slug).sort()).toEqual(
      ["does-bhava-collect-child-data", "is-bhava-official-bbt", "what-is-bhava-faq"].sort(),
    );
  });

  it("loads Bhāva-original provenance for every pilot slug", () => {
    for (const slug of PUBLIC_KNOWLEDGE_PILOT_SLUGS) {
      const prov = getProvenance(slug);
      expect(prov, slug).toBeTruthy();
      expect(prov!.label).toBe("Bhāva-original");
      expect(prov!.rights_use.scripture_body).toBe("none");
      expect(prov!.correction_path).toBe("/knowledge/corrections");
    }
  });

  it("does not invent scripture publication for blocked golden/intake ids", () => {
    const { guides, questions } = listPublicPilotCatalog();
    const hay = [...guides, ...questions]
      .map((d) => `${d.slug} ${d.title} ${d.summary}`)
      .join(" ")
      .toLowerCase();
    expect(hay.includes("top-0147")).toBe(false);
    expect(hay.includes("nrsimha pranama")).toBe(false);
  });
});
