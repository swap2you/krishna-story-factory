import { describe, expect, it } from "vitest";
import {
  getCollectionStatus,
  isCollectionActive,
  ACTIVE_AREAS,
  GROWING_NEXT,
  LIBRARY_MENU_BOOKS,
  LIBRARY_MENU_PRACTICE,
  LIBRARY_MENU_EDUCATOR,
} from "./collection-readiness";
import { PUBLIC_STORY_MAX } from "./public-boundary";

describe("collection-readiness", () => {
  it("returns active for krishna-book", () => {
    expect(getCollectionStatus("krishna-book")).toBe("active");
  });

  it("returns active for knowledge and learning pillars", () => {
    expect(getCollectionStatus("knowledge")).toBe("active");
    expect(getCollectionStatus("learning")).toBe("active");
    expect(getCollectionStatus("library")).toBe("active");
  });

  it("returns active for printables", () => {
    expect(getCollectionStatus("printables")).toBe("active");
  });

  it("returns planned for prayers-mantras and prabhupada-vani", () => {
    expect(getCollectionStatus("prayers-mantras")).toBe("planned");
    expect(getCollectionStatus("prabhupada-vani")).toBe("planned");
  });

  it("returns planned for unknown slugs", () => {
    expect(getCollectionStatus("unknown-collection")).toBe("planned");
  });

  it("isCollectionActive helper works", () => {
    expect(isCollectionActive("krishna-book")).toBe(true);
    expect(isCollectionActive("prayers-mantras")).toBe(false);
  });

  it("ACTIVE_AREAS is the four pillars with honest statuses", () => {
    expect(ACTIVE_AREAS.map((a) => a.slug)).toEqual([
      "library",
      "knowledge",
      "learning",
      "prabhupada-vani",
    ]);
    expect(ACTIVE_AREAS.map((a) => a.href)).toEqual([
      "/library",
      "/knowledge",
      "/learning",
      "/prabhupada-vani",
    ]);
    for (const area of ACTIVE_AREAS) {
      expect(area.status).toBe(getCollectionStatus(area.slug));
    }
    const vani = ACTIVE_AREAS.find((a) => a.slug === "prabhupada-vani");
    expect(vani?.status).toBe("planned");
  });

  it("ACTIVE_AREAS library copy respects PUBLIC_STORY_MAX", () => {
    const library = ACTIVE_AREAS.find((a) => a.slug === "library");
    const ceiling = String(PUBLIC_STORY_MAX).padStart(3, "0");
    expect(library?.description).toContain(`001–${ceiling}`);
  });

  it("GROWING_NEXT contains only planned collections", () => {
    for (const area of GROWING_NEXT) {
      expect(area.status).toBe("planned");
      expect(getCollectionStatus(area.slug)).toBe("planned");
    }
    expect(GROWING_NEXT.map((a) => a.slug)).not.toContain("prabhupada-vani");
  });

  it("all library menu items have valid slugs", () => {
    const all = [...LIBRARY_MENU_BOOKS, ...LIBRARY_MENU_PRACTICE, ...LIBRARY_MENU_EDUCATOR];
    for (const item of all) {
      expect(item.slug).toBeTruthy();
      expect(item.href).toBeTruthy();
      expect(item.label).toBeTruthy();
      const status = getCollectionStatus(item.slug);
      expect(["active", "planned"]).toContain(status);
    }
  });

  it("active pillar hubs do not include unfinished scripture shelves", () => {
    const activeSlugs = ACTIVE_AREAS.map((a) => a.slug);
    expect(activeSlugs).not.toContain("srimad-bhagavatam");
    expect(activeSlugs).not.toContain("teacher-resources");
  });
});
