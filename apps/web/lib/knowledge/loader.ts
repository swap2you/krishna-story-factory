import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

export type KnowledgeMeta = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  content_type: string;
  pathway?: string;
  visibility: string;
  review_state: string;
  audience?: string[];
  sources?: { label: string; tier?: string }[];
  answer_md?: string;
};

export type KnowledgeDoc = KnowledgeMeta & {
  body_md?: string;
};

export type RoadmapRecord = {
  id: string;
  pillar: string;
  cluster: string;
  title: string;
  content_type: string;
  audience: string;
  level: string;
  priority: string;
  source_tier_required: string;
  required_reviewer: string;
  visibility: string;
  package_status: string;
  lifecycle: string;
  provenance: {
    source_file: string;
    source_line: number;
    source_csv_sha256: string;
    package: string;
  };
};

export const CONTENT_TYPES = [
  "article",
  "canonical_question",
  "prayer",
  "arati",
  "sloka",
  "stuti",
  "learning_path",
  "checklist",
  "glossary",
  "teacher_resource",
  "preacher_resource",
  "policy_standard",
  "source_guide",
] as const;

export type ContentType = (typeof CONTENT_TYPES)[number];

const PUBLIC_LIFECYCLES = new Set(["approved", "published"]);

const ROOT = path.join(process.cwd(), "..", "..", "content", "knowledge");
const ROOT_ALT = path.join(process.cwd(), "content", "knowledge");

function knowledgeRoot(): string {
  if (fs.existsSync(ROOT)) return ROOT;
  if (fs.existsSync(ROOT_ALT)) return ROOT_ALT;
  const fromWeb = path.join(process.cwd(), "..", "..", "content", "knowledge");
  if (fs.existsSync(fromWeb)) return fromWeb;
  return path.resolve(process.cwd(), "../../content/knowledge");
}

function readJson<T>(file: string): T | null {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as T;
  } catch {
    return null;
  }
}

function isPublic(meta: KnowledgeMeta): boolean {
  if (meta.visibility !== "public") return false;
  return ["published", "approved"].includes(meta.review_state);
}

function loadRoadmapRecords(): RoadmapRecord[] {
  const file = path.join(knowledgeRoot(), "roadmap", "records.json");
  const data = readJson<RoadmapRecord[]>(file);
  return Array.isArray(data) ? data : [];
}

export function listPathways() {
  const data = readJson<{ pathways: { slug: string; title: string; status: string }[] }>(
    path.join(knowledgeRoot(), "pathways", "index.json"),
  );
  return data?.pathways ?? [];
}

export function listArticles(): KnowledgeDoc[] {
  const dir = path.join(knowledgeRoot(), "articles");
  if (!fs.existsSync(dir)) return [];
  const out: KnowledgeDoc[] = [];
  for (const slug of fs.readdirSync(dir)) {
    const metaPath = path.join(dir, slug, "meta.json");
    const bodyPath = path.join(dir, slug, "index.md");
    const meta = readJson<KnowledgeMeta>(metaPath);
    if (!meta || !isPublic(meta)) continue;
    const body_md = fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "";
    out.push({ ...meta, body_md });
  }
  return out.sort((a, b) => a.title.localeCompare(b.title));
}

export function listQuestions(): KnowledgeDoc[] {
  const dir = path.join(knowledgeRoot(), "questions");
  if (!fs.existsSync(dir)) return [];
  const out: KnowledgeDoc[] = [];
  for (const slug of fs.readdirSync(dir)) {
    const meta = readJson<KnowledgeMeta>(path.join(dir, slug, "meta.json"));
    if (!meta || !isPublic(meta)) continue;
    out.push(meta);
  }
  return out.sort((a, b) => a.title.localeCompare(b.title));
}

export function listByType(contentType: string): KnowledgeDoc[] {
  return [...listArticles(), ...listQuestions()].filter((item) => item.content_type === contentType);
}

export function getBySlug(slug: string): KnowledgeDoc | null {
  const articleMeta = path.join(knowledgeRoot(), "articles", slug, "meta.json");
  if (fs.existsSync(articleMeta)) {
    const meta = readJson<KnowledgeMeta>(articleMeta);
    if (!meta || !isPublic(meta)) return null;
    const bodyPath = path.join(knowledgeRoot(), "articles", slug, "index.md");
    return { ...meta, body_md: fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "" };
  }
  const qMeta = path.join(knowledgeRoot(), "questions", slug, "meta.json");
  if (fs.existsSync(qMeta)) {
    const meta = readJson<KnowledgeMeta>(qMeta);
    if (!meta || !isPublic(meta)) return null;
    return meta;
  }
  return null;
}

/** Public: approved/published only. Private studio: full roadmap. */
export function listRoadmap(includePrivate = false): RoadmapRecord[] {
  const all = loadRoadmapRecords();
  if (includePrivate) return all;
  return all.filter(
    (r) => r.visibility === "public" && PUBLIC_LIFECYCLES.has(r.lifecycle),
  );
}

export function getRoadmapCounts(includePrivate = false): {
  total: number;
  lifecycle: Record<string, number>;
  pillars: Record<string, number>;
} {
  const rows = listRoadmap(includePrivate);
  const lifecycle: Record<string, number> = {};
  const pillars: Record<string, number> = {};
  for (const row of rows) {
    lifecycle[row.lifecycle] = (lifecycle[row.lifecycle] ?? 0) + 1;
    pillars[row.pillar] = (pillars[row.pillar] ?? 0) + 1;
  }
  return { total: rows.length, lifecycle, pillars };
}

export function listRoadmapPillars(includePrivate = false): string[] {
  return [...new Set(listRoadmap(includePrivate).map((r) => r.pillar))].sort();
}

export function searchKnowledge(query: string, opts?: { includePrivateRoadmap?: boolean }): KnowledgeDoc[] {
  const q = query.trim().toLowerCase();
  const pool = [...listArticles(), ...listQuestions()];
  if (!q) return pool;
  const docs = pool.filter((item) => {
    const hay = [item.title, item.summary, item.body_md ?? "", item.answer_md ?? "", item.pathway ?? ""]
      .join("\n")
      .toLowerCase();
    return hay.includes(q);
  });
  return docs;
}

export function searchRoadmap(query: string, includePrivate = false): RoadmapRecord[] {
  const q = query.trim().toLowerCase();
  const rows = listRoadmap(includePrivate);
  if (!q) return rows;
  return rows.filter((row) => {
    const hay = [row.id, row.title, row.pillar, row.cluster, row.content_type, row.audience]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });
}

export function roadmapSourceChecksum(): string | null {
  const index = readJson<{ source?: { sha256?: string } }>(
    path.join(knowledgeRoot(), "roadmap", "index.json"),
  );
  return index?.source?.sha256 ?? null;
}

export function fileSha256(filePath: string): string {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash("sha256").update(buf).digest("hex");
}
