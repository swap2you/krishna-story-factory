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

export function listDerivatives(includePrivate = false): LearningDerivative[] {
  const dir = derivativesRoot();
  if (!fs.existsSync(dir)) return [];
  const out: LearningDerivative[] = [];
  for (const slug of fs.readdirSync(dir)) {
    const metaPath = path.join(dir, slug, "meta.json");
    const bodyPath = path.join(dir, slug, "body.md");
    const meta = readJson<LearningDerivativeMeta>(metaPath);
    if (!meta) continue;
    if (!includePrivate && !isPublicDerivative(meta)) continue;
    const body_md = fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "";
    out.push({ ...meta, body_md });
  }
  return out.sort((a, b) => a.title.localeCompare(b.title));
}

export function listPublicDerivatives(): LearningDerivative[] {
  return listDerivatives(false);
}

export function getDerivativeBySlug(
  slug: string,
  opts?: { includePrivate?: boolean },
): LearningDerivative | null {
  const metaPath = path.join(derivativesRoot(), slug, "meta.json");
  const bodyPath = path.join(derivativesRoot(), slug, "body.md");
  const meta = readJson<LearningDerivativeMeta>(metaPath);
  if (!meta) return null;
  if (!opts?.includePrivate && !isPublicDerivative(meta)) return null;
  const body_md = fs.existsSync(bodyPath) ? fs.readFileSync(bodyPath, "utf8") : "";
  return { ...meta, body_md };
}

export function audienceLabel(meta: LearningDerivativeMeta): string {
  const profiles = meta.audience.profiles.map((p) => p.replace(/_/g, " ")).join(", ");
  return `${profiles} · ${meta.audience.age_range.label}`;
}
