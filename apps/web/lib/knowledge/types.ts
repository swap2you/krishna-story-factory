import { CONTENT_TYPES, type ContentType } from "./loader";

export type ResourceDraft = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  content_type: ContentType | string;
  visibility: string;
  review_state: string;
  body_md?: string;
  sources?: { label: string; tier?: string; quotation_type?: string }[];
  rights?: { status?: string };
  confidential?: boolean;
  required_reviewer?: string;
  scriptural_reviewer?: string;
};

export function validateResourceDraft(draft: ResourceDraft): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  if (!draft.id?.trim()) errors.push("id_required");
  if (!draft.slug?.trim()) errors.push("slug_required");
  if (!draft.title?.trim()) errors.push("title_required");
  if (!CONTENT_TYPES.includes(draft.content_type as ContentType) && draft.content_type !== "question") {
    errors.push("unknown_content_type");
  }
  if (!draft.summary?.trim()) errors.push("summary_required");
  if (draft.confidential) errors.push("confidential_blocked");
  if ((draft.rights?.status || "") === "") errors.push("rights_required");
  if (["approved", "published"].includes(draft.review_state) && !draft.required_reviewer && !draft.scriptural_reviewer) {
    errors.push("reviewer_required_for_publish");
  }
  return { ok: errors.length === 0, errors };
}

export const TYPE_TEMPLATES: Record<string, { label: string; fields: string[] }> = {
  article: { label: "Article", fields: ["title", "summary", "body_md", "sources", "pathway"] },
  canonical_question: { label: "Canonical question", fields: ["title", "summary", "answer_md", "sources"] },
  prayer: { label: "Prayer", fields: ["title", "transliteration", "translation", "sources"] },
  arati: { label: "Ārati", fields: ["title", "verses", "sources"] },
  sloka: { label: "Śloka", fields: ["title", "devanagari", "transliteration", "synonyms", "translation"] },
  stuti: { label: "Stuti", fields: ["title", "verses", "sources"] },
  learning_path: { label: "Learning path", fields: ["title", "steps", "audience"] },
  checklist: { label: "Checklist", fields: ["title", "items", "audience"] },
  glossary: { label: "Glossary", fields: ["term", "definition", "aliases"] },
  teacher_resource: { label: "Teacher resource", fields: ["title", "classroom_use", "age_range"] },
  preacher_resource: { label: "Preacher resource", fields: ["title", "outline", "sources"] },
  policy_standard: { label: "Policy / standard", fields: ["title", "body_md", "authority"] },
  source_guide: { label: "Source guide", fields: ["title", "tiers", "examples"] },
};
