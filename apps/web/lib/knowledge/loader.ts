import fs from "node:fs";
import path from "node:path";

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

const ROOT = path.join(process.cwd(), "..", "..", "content", "knowledge");
const ROOT_ALT = path.join(process.cwd(), "content", "knowledge");

function knowledgeRoot(): string {
  if (fs.existsSync(ROOT)) return ROOT;
  if (fs.existsSync(ROOT_ALT)) return ROOT_ALT;
  // monorepo: apps/web cwd
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
  return ["published", "approved", "review_due", "archived"].includes(meta.review_state);
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

export function searchKnowledge(query: string): KnowledgeDoc[] {
  const q = query.trim().toLowerCase();
  const pool = [...listArticles(), ...listQuestions()];
  if (!q) return pool;
  return pool.filter((item) => {
    const hay = [item.title, item.summary, item.body_md ?? "", item.answer_md ?? "", item.pathway ?? ""]
      .join("\n")
      .toLowerCase();
    return hay.includes(q);
  });
}
