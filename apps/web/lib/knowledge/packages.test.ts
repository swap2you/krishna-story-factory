import { describe, expect, it } from "vitest";
import {
  FIXTURE_MARKER,
  canonicalTextHash,
  getKnowledgePackage,
  listKnowledgePackages,
  validateKnowledgePackage,
} from "@/lib/knowledge/packages";

describe("knowledge packages P01C", () => {
  it("loads fixture package as SOURCE_BLOCKED with hash parity", () => {
    const pkg = getKnowledgePackage("p01c-structural-fixture");
    expect(pkg).toBeTruthy();
    expect(pkg!.record.source_status).toBe("SOURCE_BLOCKED");
    expect(pkg!.record.fixture_label).toContain(FIXTURE_MARKER);
    expect(canonicalTextHash(pkg!.content.blocks)).toBe(pkg!.record.canonical_text_hash);
    expect(validateKnowledgePackage(pkg!).ok).toBe(true);
  });

  it("lists fixture in package inventory", () => {
    const ids = listKnowledgePackages().map((p) => p.record.record_id);
    expect(ids).toContain("KF-P01C-FIXTURE-001");
  });
});
