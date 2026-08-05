import { describe, expect, it } from "vitest";
import { getCollectionArt } from "./collection-art";
import { AGE_PATHWAYS } from "./age-pathways";

describe("collection art focal metadata", () => {
  it("keeps Krishna Book and teacher subjects upper-centered", () => {
    expect(getCollectionArt("krishna-book").objectPositionDesktop).toContain("18%");
    expect(getCollectionArt("teacher-resources").objectPositionDesktop).toContain("30%");
    expect(getCollectionArt("prabhupada-vani").objectPositionDesktop).toContain("18%");
  });
});

describe("age pathways", () => {
  it("includes five pathways with honest growing statuses", () => {
    expect(AGE_PATHWAYS).toHaveLength(5);
    const growing = AGE_PATHWAYS.filter((p) => p.status === "growing");
    expect(growing.length).toBeGreaterThan(0);
    for (const pathway of AGE_PATHWAYS) {
      expect(pathway.publicTitle.length).toBeGreaterThan(3);
      expect(pathway.description.length).toBeGreaterThan(10);
      if (pathway.status === "growing" && !pathway.href) {
        expect(pathway.id).toBe("yauvana");
      }
    }
  });
});
