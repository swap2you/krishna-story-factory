/** @vitest-environment node */
import { describe, expect, it } from "vitest";
import {
  getDerivativeBySlug,
  listDerivativeMetas,
  listDerivatives,
  listPublicDerivativeMetas,
  listPublicDerivatives,
} from "@/lib/learning/derivatives";

const EXPECTED_PUBLIC = [
  "family-trust-qa-activity",
  "printing-classroom-family-practice",
  "sunday-school-printing-teacher-guide",
  "what-is-bhava-lesson-plan",
].sort();

describe("learning derivatives visibility", () => {
  it("lists exactly the published public derivatives", () => {
    const publicOnes = listPublicDerivatives();
    expect(publicOnes.map((d) => d.slug).sort()).toEqual(EXPECTED_PUBLIC);
    for (const d of publicOnes) {
      expect(d.visibility).toBe("public");
      expect(["approved", "published"]).toContain(d.review_state);
      expect(d.export_manifest.downloadable).toBe(false);
      expect(d.body_md.length).toBeGreaterThan(40);
      expect(d.source_lineage.origin).toMatch(/bhava/i);
    }
  });

  it("exposes a metadata-only listing without requiring bodies for hub/sitemap", () => {
    const metas = listPublicDerivativeMetas();
    expect(metas.map((d) => d.slug).sort()).toEqual(EXPECTED_PUBLIC);
    expect(metas.every((m) => !("body_md" in m))).toBe(true);
    expect(listDerivativeMetas(false).length).toBe(metas.length);
  });

  it("loads a derivative by slug only when public", () => {
    const lesson = getDerivativeBySlug("what-is-bhava-lesson-plan");
    expect(lesson?.title).toContain("What is Bhāva");
    expect(lesson?.canonical_record_version.record_slug).toBe("what-is-bhava");
  });

  it("rejects path-escape and unsafe slug values", () => {
    expect(getDerivativeBySlug("..")).toBeNull();
    expect(getDerivativeBySlug("../secrets")).toBeNull();
    expect(getDerivativeBySlug("what-is-bhava-lesson-plan/../../etc")).toBeNull();
    expect(getDerivativeBySlug("UPPER")).toBeNull();
  });

  it("keeps private drafts out of the public list when present", () => {
    const all = listDerivatives(true);
    const publicSlugs = new Set(listPublicDerivatives().map((d) => d.slug));
    for (const d of all) {
      if (!publicSlugs.has(d.slug)) {
        expect(
          d.visibility === "public" && ["approved", "published"].includes(d.review_state),
        ).toBe(false);
      }
    }
  });

  it("does not advertise fake downloads", () => {
    for (const d of listPublicDerivatives()) {
      expect(d.export_manifest.downloadable).toBe(false);
      expect(d.export_manifest.artifact_paths ?? []).toEqual([]);
    }
  });
});
