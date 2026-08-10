import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {
  FIXTURE_MARKER,
  nfc,
  type ContentBlock,
  type KnowledgePackage,
} from "@/lib/knowledge/package-types";

export * from "@/lib/knowledge/package-types";

function knowledgeRoot(): string {
  const candidates = [
    path.join(process.cwd(), "..", "..", "content", "knowledge"),
    path.join(process.cwd(), "content", "knowledge"),
    path.resolve(process.cwd(), "../../content/knowledge"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return candidates[0];
}

function packagesRoot(): string {
  return path.join(knowledgeRoot(), "packages");
}

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(file, "utf8")) as T;
}

export function canonicalTextHash(blocks: ContentBlock[]): string {
  const stanzas = blocks
    .filter((b) => b.block_type === "stanza")
    .sort((a, b) => a.ord - b.ord);
  const parts: string[] = [];
  for (const s of stanzas) {
    parts.push(nfc(s.devanagari || ""));
    parts.push(nfc(s.iast || ""));
    parts.push(nfc(s.translation_en || ""));
  }
  return crypto.createHash("sha256").update(parts.join("\n"), "utf8").digest("hex");
}

export function loadPackageDir(dir: string): KnowledgePackage {
  return {
    record: readJson(path.join(dir, "record.json")),
    content: readJson(path.join(dir, "content.json")),
    source_dossier: readJson(path.join(dir, "source_dossier.json")),
    rights: readJson(path.join(dir, "rights.json")),
    assets: readJson(path.join(dir, "assets.json")),
    reviews: readJson(path.join(dir, "reviews.json")),
    manifest: readJson(path.join(dir, "manifest.json")),
    dir,
  };
}

export function listKnowledgePackages(): KnowledgePackage[] {
  const root = packagesRoot();
  if (!fs.existsSync(root)) return [];
  return fs
    .readdirSync(root)
    .map((name) => path.join(root, name))
    .filter((dir) => fs.existsSync(path.join(dir, "record.json")))
    .map(loadPackageDir)
    .sort((a, b) => a.record.record_id.localeCompare(b.record.record_id));
}

export function getKnowledgePackage(slugOrId: string): KnowledgePackage | null {
  return (
    listKnowledgePackages().find(
      (p) => p.record.slug === slugOrId || p.record.record_id === slugOrId,
    ) ?? null
  );
}

export function validateKnowledgePackage(pkg: KnowledgePackage): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  const expected = canonicalTextHash(pkg.content.blocks);
  if (pkg.record.canonical_text_hash !== expected) {
    errors.push("canonical_text_hash mismatch");
  }
  if (pkg.record.unicode_normalization !== "NFC") {
    errors.push("unicode_normalization must be NFC");
  }
  if (pkg.record.visibility === "public" && pkg.record.source_status !== "DOSSIER_READY") {
    errors.push("public visibility requires DOSSIER_READY");
  }
  if (
    pkg.record.source_status === "SOURCE_BLOCKED" &&
    pkg.source_dossier.decision !== "SOURCE_BLOCKED"
  ) {
    errors.push("SOURCE_BLOCKED requires dossier decision SOURCE_BLOCKED");
  }
  if (pkg.record.fixture) {
    if (!pkg.record.fixture_label?.includes("TEST FIXTURE")) {
      errors.push("fixture_label missing");
    }
    void FIXTURE_MARKER;
  }
  return { ok: errors.length === 0, errors };
}
