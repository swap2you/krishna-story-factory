export const FIXTURE_MARKER = "TEST FIXTURE — NOT APPROVED DEVOTIONAL CONTENT";
export const LENSES = ["little_learner", "explorer", "teen", "study"] as const;
export type LensId = (typeof LENSES)[number];
export const DEFAULT_LENS: LensId = "explorer";

export type KnowledgePackageRecord = {
  record_id: string;
  slug: string;
  title: string;
  title_iast?: string;
  content_type: string;
  lifecycle: string;
  package_status: string;
  visibility: string;
  source_status: "SOURCE_BLOCKED" | "RIGHTS_BLOCKED" | "DOSSIER_READY" | "CONFLICT_REVIEW_REQUIRED";
  purpose_sentence?: string;
  record_version: string;
  canonical_text_hash: string;
  unicode_normalization: "NFC";
  roadmap_ref?: string;
  fixture?: boolean;
  fixture_label?: string;
  audience_default?: string;
  min_age?: number;
  max_age?: number;
};

export type ContentBlock = {
  block_id: string;
  block_type: string;
  ord: number;
  body?: string;
  devanagari?: string;
  iast?: string;
  translation_en?: string;
  translator?: string;
  edition?: string;
  exact_locator?: string;
  word_meanings?: { term: string; meaning: string }[];
  lens_explanations?: Partial<Record<LensId, string>>;
  asset_refs?: string[];
};

export type KnowledgePackage = {
  record: KnowledgePackageRecord;
  content: { blocks: ContentBlock[] };
  source_dossier: { decision: string; summary?: string; gaps?: string[] };
  rights: Record<string, unknown>;
  assets: { assets: { asset_id: string; role: string; decorative?: boolean; status?: string; notes?: string }[] };
  reviews: { reviews: unknown[] };
  manifest: Record<string, unknown>;
  dir?: string;
};

export function nfc(value: string): string {
  return value.normalize("NFC");
}

export function isLensId(value: string | null | undefined): value is LensId {
  return !!value && (LENSES as readonly string[]).includes(value);
}

export function parseLens(value: string | null | undefined): LensId {
  return isLensId(value) ? value : DEFAULT_LENS;
}
