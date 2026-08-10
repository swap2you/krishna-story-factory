"use client";

import Link from "next/link";
import type { KnowledgeDoc, KnowledgeProvenance } from "@/lib/knowledge/loader";
import { TrustPanel } from "./trust-panel";

type Props = {
  doc: KnowledgeDoc;
  provenance?: KnowledgeProvenance | null;
};

/**
 * Template V1 adapted shell for public Bhāva-original canonical Q&A.
 * Trust panel defaults open; no scripture sequence.
 */
export function QuestionRecordShell({ doc, provenance }: Props) {
  const trustRows = [
    {
      label: "Provenance label",
      value: provenance?.label ?? "Bhāva-original",
    },
    { label: "Content type", value: doc.content_type },
    { label: "Review state", value: provenance?.review_ledger.review_state ?? doc.review_state },
    { label: "Visibility", value: provenance?.review_ledger.visibility ?? doc.visibility },
    {
      label: "Source dossier",
      value:
        provenance?.source_dossier_summary ??
        "Bhāva editorial FAQ — not a scripture package.",
    },
    {
      label: "Claim map",
      value:
        provenance?.claim_map_note ??
        "Claims are limited to Bhāva-original FAQ guidance; no verse bodies.",
    },
    {
      label: "Rights / use",
      value: provenance
        ? `${provenance.rights_use.status} · scripture body: ${provenance.rights_use.scripture_body}. ${provenance.rights_use.notes}`
        : "Bhāva original / no scripture body",
    },
    {
      label: "Review ledger",
      value: provenance?.review_ledger.notes
        ? `${provenance.review_ledger.last_human_review ?? "reviewed"} — ${provenance.review_ledger.notes}`
        : "Published Bhāva-original pilot FAQ",
    },
    {
      label: "Correction path",
      value: (
        <Link href={provenance?.correction_path ?? "/knowledge/corrections"}>
          Suggest a correction
        </Link>
      ),
    },
  ];

  return (
    <article className="knowledge-learning knowledge-learning--board-b knowledge-article-shell">
      <header className="knowledge-learning__hero">
        <p className="eyebrow">Canonical Q&amp;A</p>
        <h1 className="knowledge-learning__title">{doc.title}</h1>
        <p className="knowledge-status knowledge-status--guide">Published · Bhāva-original</p>
        {doc.summary ? <p className="knowledge-learning__purpose">{doc.summary}</p> : null}
      </header>

      <section className="prose" aria-label="Answer" style={{ maxWidth: 760 }}>
        <p>{doc.answer_md}</p>
      </section>

      <TrustPanel rows={trustRows} defaultOpen />

      <p className="hint" style={{ marginTop: "2rem" }}>
        <Link href="/knowledge/questions">← All questions</Link>
        {" · "}
        <Link href="/knowledge/ask">Ask a follow-up</Link>
        {" · "}
        <Link href="/knowledge/corrections">Suggest a correction</Link>
      </p>
    </article>
  );
}
