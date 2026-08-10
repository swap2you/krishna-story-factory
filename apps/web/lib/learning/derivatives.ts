import fs from "node:fs";
import path from "node:path";

export type LearningDerivativeMeta = {
  id: string;
  slug: string;
  title: string;
  derivative_type: string;
  learning_objective: string;
  audience: {
    profiles: string[];
    age_range: {
      min?: number | null;
      max?: number | null;
      label: string;
    };
  };
  canonical_record_version: {
    record_slug: string;
    record_id: string;
    record_version: string;
    content_path?: string;
  };
  source_lineage: {
    origin: string;
    notes: string;
    forbidden_content?: string[];
  };
  review_state: string;
  answer_key_relation: {
    kind: string;
    paired_derivative_id?: string | null;
    notes?: string | null;
  };
  asset_provenance: {
    rights_status: string;
    steward: string;
    assets?: { role: string; path_or_uri: string; provenance: string }[];
    notes?: string | null;
  };
  export_manifest: {
    export_version: string;
    formats: string[];
    downloadable: boolean;
    artifact_paths?: string[];
    generated_at?: string | null;
  };
  body_path?: string;
  visibility: string;
};

export type LearningDerivative = LearningDerivativeMeta & {
  body_md: string;
};

/** Safe content slugs only: lowercase letters, digits, hyphens. */
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

const ROOT = path.join(process.cwd(), "..", "..", "content", "learning", "derivatives");
const ROOT_ALT = path.join(process.cwd(), "content", "learning", "derivatives");

function derivativesRoot(): string {
  if (fs.existsSync(ROOT)) return ROOT;
  if (fs.existsSync(ROOT_ALT)) return ROOT_ALT;
  return path.resolve(process.cwd(), "../../content/learning/derivatives");
}

function readJson<T>(file: string): T | null {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as T;
  } catch {
    return null;
  }
}

function isPublicDerivative(meta: LearningDerivativeMeta): boolean {
  if (meta.visibility !== "public") return false;
  return meta.review_state === "approved" || meta.review_state === "published";
}

export function isSafeDerivativeSlug(slug: string): boolean {
  return SLUG_RE.test(slug);
}

function resolveDerivativeDir(slug: string): string | null {
  if (!isSafeDerivativeSlug(slug)) return null;
  const root = path.resolve(derivativesRoot());
  const dir = path.resolve(root, slug);
  if (!dir.startsWith(root + path.sep) && dir !== root) return null;
  return dir;
}

export function listDerivativeMetas(includePrivate = false): LearningDerivativeMeta[] {
  const dir = derivativesRoot();
  if (!fs.existsSync(dir)) return [];
  const out: LearningDerivativeMeta[] = [];
  for (const entry of fs.readdirSync(dir)) {
    if (!isSafeDerivativeSlug(entry)) continue;
    const meta = readJson<LearningDerivativeMeta>(path.join(dir, entry, "meta.json"));
    if (!meta) continue;
    if (!includePrivate && !isPublicDerivative(meta)) continue;
    out.push(meta);
  }
  return out.sort((a, b) => a.title.localeCompare(b.title));
}

export function listPublicDerivativeMetas(): LearningDerivativeMeta[] {
  return listDerivativeMetas(false);
}

export function listDerivatives(includePrivate = false): LearningDerivative[] {
  return listDerivativeMetas(includePrivate).map((meta) => {
    const dir = resolveDerivativeDir(meta.slug);
    const bodyPath = dir ? path.join(dir, "body.md") : "";
    const body_md = bodyPath && fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "";
    return { ...meta, body_md };
  });
}

export function listPublicDerivatives(): LearningDerivative[] {
  return listDerivatives(false);
}

export function getDerivativeBySlug(
  slug: string,
  opts?: { includePrivate?: boolean },
): LearningDerivative | null {
  const dir = resolveDerivativeDir(slug);
  if (!dir) return null;
  const meta = readJson<LearningDerivativeMeta>(path.join(dir, "meta.json"));
  if (!meta) return null;
  if (!opts?.includePrivate && !isPublicDerivative(meta)) return null;
  const bodyPath = path.join(dir, "body.md");
  const body_md = fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "";
  return { ...meta, body_md };
}

export function audienceLabel(meta: LearningDerivativeMeta): string {
  const profiles = meta.audience.profiles.map((p) => p.replace(/_/g, " ")).join(", ");
  return `${profiles} · ${meta.audience.age_range.label}`;
}
