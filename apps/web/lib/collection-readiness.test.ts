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

describe("collection-readiness", () => {
  it("returns active for krishna-book", () => {
    expect(getCollectionStatus("krishna-book")).toBe("active");
  });

  it("returns active for knowledge", () => {
    expect(getCollectionStatus("knowledge")).toBe("active");
  });

  it("returns active for printables", () => {
    expect(getCollectionStatus("printables")).toBe("active");
  });

  it("returns planned for prayers-mantras", () => {
    expect(getCollectionStatus("prayers-mantras")).toBe("planned");
  });

  it("returns planned for unknown slugs", () => {
    expect(getCollectionStatus("unknown-collection")).toBe("planned");
  });

  it("isCollectionActive helper works", () => {
    expect(isCollectionActive("krishna-book")).toBe(true);
    expect(isCollectionActive("prayers-mantras")).toBe(false);
  });

  it("ACTIVE_AREAS contains only active collections", () => {
    for (const area of ACTIVE_AREAS) {
      expect(area.status).toBe("active");
      expect(getCollectionStatus(area.slug)).toBe("active");
    }
  });

  it("GROWING_NEXT contains only planned collections", () => {
    for (const area of GROWING_NEXT) {
      expect(area.status).toBe("planned");
      expect(getCollectionStatus(area.slug)).toBe("planned");
    }
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

  it("active areas do not include srimad-bhagavatam or teacher-resources", () => {
    const activeSlugs = ACTIVE_AREAS.map((a) => a.slug);
    expect(activeSlugs).not.toContain("srimad-bhagavatam");
    expect(activeSlugs).not.toContain("teacher-resources");
  });
});
