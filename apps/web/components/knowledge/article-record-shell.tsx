"use client";

import Link from "next/link";
import { useState } from "react";
import { HelpfulVote } from "@/components/helpful-vote";
import type { KnowledgeDoc, KnowledgeProvenance } from "@/lib/knowledge/loader";
import { FocusModeBar } from "./focus-mode-bar";
import { TrustPanel } from "./trust-panel";

type Props = {
  doc: KnowledgeDoc;
  provenance?: KnowledgeProvenance | null;
};

/**
 * Template V1 adapted shell for public Bhāva-original Knowledge guides.
 * Hero + reading focus + body + trust panel. No Devanāgarī/IAST scripture sequence.
 */
export function ArticleRecordShell({ doc, provenance }: Props) {
  const [focusMode, setFocusMode] = useState(false);

  const trustRows = [
    {
      label: "Provenance label",
      value: provenance?.label ?? "Bhāva-original",
    },
    { label: "Content type", value: doc.content_type },
    { label: "Review state", value: provenance?.review_ledger.review_state ?? doc.review_state },
    { label: "Visibility", value: provenance?.review_ledger.visibility ?? doc.visibility },
    ...(doc.pathway ? [{ label: "Pathway", value: doc.pathway }] : []),
    {
      label: "Source dossier",
      value:
        provenance?.source_dossier_summary ??
        "Bhāva editorial guide — not a scripture package.",
    },
    {
      label: "Claim map",
      value:
        provenance?.claim_map_note ??
        "Claims are limited to Bhāva-original editorial guidance; no verse bodies.",
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
        : doc.sources?.length
          ? doc.sources.map((s) => `${s.label}${s.tier ? ` (${s.tier})` : ""}`).join("; ")
          : "Published Bhāva-original pilot record",
    },
    {
      label: "Scripture bodies",
      value: "Not applicable — this is a Bhāva-original guide, not a verified verse package.",
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
    <article
      className={`knowledge-learning knowledge-learning--board-b knowledge-article-shell${
        focusMode ? " knowledge-article-shell--focus" : ""
      }`}
    >
      <header className="knowledge-learning__hero">
        <p className="eyebrow">Knowledge guide</p>
        <h1 className="knowledge-learning__title">{doc.title}</h1>
        <p className="knowledge-status knowledge-status--guide">Published · Bhāva-original</p>
        {doc.summary ? <p className="knowledge-learning__purpose">{doc.summary}</p> : null}
      </header>

      <p className="hint">
        Reading lenses and verse focus apply to verified scripture packages. This page is an editorial
        guide — Template V1 hero, focus, and trust panel without fabricated Devanāgarī or IAST.
      </p>

      <FocusModeBar focusMode={focusMode} onToggle={() => setFocusMode((v) => !v)} />

      <section
        className="knowledge-article-body prose"
        aria-label="Guide body"
        style={{ maxWidth: focusMode ? "48ch" : 760 }}
      >
        <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0 }}>{doc.body_md}</pre>
      </section>

      <TrustPanel rows={trustRows} defaultOpen />

      <div style={{ marginTop: "1.5rem" }}>
        <HelpfulVote resourceId={doc.id || doc.slug} />
      </div>

      <p className="hint" style={{ marginTop: "2rem" }}>
        <Link href="/knowledge">← Knowledge home</Link>
        {" · "}
        <Link href="/knowledge/corrections">Suggest a correction</Link>
        {" · "}
        <Link href="/knowledge/report-link">Report broken link</Link>
      </p>
    </article>
  );
}
