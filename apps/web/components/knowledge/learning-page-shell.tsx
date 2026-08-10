"use client";

import { useEffect, useMemo, useState } from "react";
import type { KnowledgePackage, LensId } from "@/lib/knowledge/package-types";
import { DEFAULT_LENS, parseLens } from "@/lib/knowledge/package-types";
import { FocusModeBar } from "./focus-mode-bar";
import { LensSelector, LENS_LABELS } from "./lens-selector";
import { TrustPanel } from "./trust-panel";

const STORAGE_KEY = "bhava.knowledge.lens";

type Props = {
  pkg: KnowledgePackage;
  initialLens?: string;
  initialFocus?: boolean;
  initialStanza?: string;
};

/**
 * Template V1 package record shell (studio private preview).
 * Lenses, focus mode, canonical stanza sequence, trust panel, study-neutral exports.
 */
export function LearningPageShell({ pkg, initialLens, initialFocus, initialStanza }: Props) {
  const [lens, setLens] = useState<LensId>(parseLens(initialLens || pkg.record.audience_default));
  const [focusMode, setFocusMode] = useState(Boolean(initialFocus));
  const [sourceOpen, setSourceOpen] = useState(() => parseLens(initialLens || pkg.record.audience_default) === "study");
  const stanzas = useMemo(
    () => pkg.content.blocks.filter((b) => b.block_type === "stanza").sort((a, b) => a.ord - b.ord),
    [pkg],
  );
  const [stanzaIndex, setStanzaIndex] = useState(() => {
    const idx = stanzas.findIndex((s) => s.block_id === initialStanza);
    return idx >= 0 ? idx : 0;
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("lens")) return;
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (stored) {
      const next = parseLens(stored);
      setLens(next);
      const url = new URL(window.location.href);
      url.searchParams.set("lens", next);
      window.history.replaceState({}, "", url.toString());
    }
  }, []);

  function syncUrl(next: { lens?: LensId; focus?: boolean; stanzaId?: string }) {
    const url = new URL(window.location.href);
    if (next.lens) url.searchParams.set("lens", next.lens);
    if (next.focus !== undefined) {
      if (next.focus) url.searchParams.set("focus", "1");
      else url.searchParams.delete("focus");
    }
    if (next.stanzaId) url.searchParams.set("stanza", next.stanzaId);
    window.history.replaceState({}, "", url.toString());
  }

  function selectLens(next: LensId, opts?: { restoreReadingFocus?: boolean }) {
    setLens(next);
    if (next === "study") setSourceOpen(true);
    sessionStorage.setItem(STORAGE_KEY, next);
    syncUrl({ lens: next });
    if (opts?.restoreReadingFocus) {
      const current = stanzas[stanzaIndex];
      if (current) {
        requestAnimationFrame(() => {
          const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
          document.getElementById(current.block_id)?.scrollIntoView({
            block: "nearest",
            behavior: reduced ? "auto" : "smooth",
          });
          document.getElementById(`${current.block_id}-heading`)?.focus();
        });
      }
    } else {
      requestAnimationFrame(() => {
        document.querySelector<HTMLElement>(`.knowledge-lens [role="radio"][aria-checked="true"]`)?.focus();
      });
    }
  }

  function goStanza(nextIndex: number) {
    const clamped = Math.max(0, Math.min(stanzas.length - 1, nextIndex));
    setStanzaIndex(clamped);
    const block = stanzas[clamped];
    if (block) {
      syncUrl({ focus: true, stanzaId: block.block_id });
      requestAnimationFrame(() => {
        document.getElementById(`${block.block_id}-heading`)?.focus();
      });
    }
  }

  const purpose = pkg.content.blocks.find((b) => b.block_type === "purpose");
  const practice = pkg.content.blocks.find((b) => b.block_type === "practice");
  const context = pkg.content.blocks.find((b) => b.block_type === "context");
  const visible = focusMode ? [stanzas[stanzaIndex]].filter(Boolean) : stanzas;
  const blocked = pkg.record.source_status === "SOURCE_BLOCKED";
  const showBodies = Boolean(pkg.record.fixture) || !blocked;

  return (
    <article className="knowledge-learning knowledge-learning--board-b" data-lens={lens}>
      <header className="knowledge-learning__hero">
        <p className="eyebrow">Studio private preview</p>
        <h1 className="knowledge-learning__title">{pkg.record.title}</h1>
        <p className={`knowledge-status knowledge-status--${pkg.record.source_status.toLowerCase()}`}>
          {pkg.record.source_status}
          {pkg.record.fixture ? ` · ${pkg.record.fixture_label}` : null}
        </p>
        {purpose?.body ? <p className="knowledge-learning__purpose">{purpose.body}</p> : null}
        <div className="knowledge-placeholder-art" aria-hidden="true">
          Board B placeholder art slot (editorial gouache) — no production artwork
        </div>
      </header>

      <LensSelector lens={lens} onSelect={selectLens} />
      <p className="sr-only" aria-live="polite">
        Depth lens {LENS_LABELS[lens]} selected
        {focusMode ? `. Focus mode stanza ${stanzaIndex + 1} of ${stanzas.length}` : ""}
      </p>

      {blocked ? (
        <p className="knowledge-banner" role="status">
          Production scripture is not authorized for this record. Showing synthetic structural
          fixture text only.
        </p>
      ) : null}

      <section aria-label="Stanzas" className="knowledge-stanzas">
        {showBodies
          ? visible.map((stanza) => (
              <section
                key={stanza.block_id}
                id={stanza.block_id}
                className="knowledge-stanza"
                aria-labelledby={`${stanza.block_id}-heading`}
              >
                <h2 id={`${stanza.block_id}-heading`} tabIndex={-1}>
                  Stanza {stanza.ord}
                </h2>
                <p className="sanskrit knowledge-deva" lang="sa">
                  {stanza.devanagari}
                </p>
                <p className="knowledge-iast" lang="sa-Latn">
                  {stanza.iast}
                </p>
                <p className="knowledge-translation">{stanza.translation_en}</p>
                {stanza.lens_explanations?.[lens] ? (
                  <p className="knowledge-lens-note">{stanza.lens_explanations[lens]}</p>
                ) : null}
                {lens !== "little_learner" && stanza.word_meanings?.length ? (
                  <ul className="knowledge-word-meanings">
                    {stanza.word_meanings.map((w) => (
                      <li key={w.term}>
                        <strong>{w.term}</strong>: {w.meaning}
                      </li>
                    ))}
                  </ul>
                ) : null}
                <div className="knowledge-placeholder-art knowledge-placeholder-art--stanza" aria-hidden="true">
                  Placeholder illustration slot
                </div>
              </section>
            ))
          : (
            <p role="status">Scripture bodies are suppressed while source status is blocked.</p>
          )}
      </section>

      <FocusModeBar
        focusMode={focusMode}
        onToggle={() => {
          setFocusMode((v) => {
            const next = !v;
            const current = stanzas[stanzaIndex];
            syncUrl({ focus: next, stanzaId: current?.block_id });
            if (!next && current) {
              requestAnimationFrame(() => {
                document.getElementById(`${current.block_id}-heading`)?.focus();
              });
            }
            return next;
          });
        }}
        stanzaNav={{
          index: stanzaIndex,
          total: stanzas.length,
          onPrev: () => goStanza(stanzaIndex - 1),
          onNext: () => goStanza(stanzaIndex + 1),
        }}
      />

      {context?.body && lens !== "little_learner" ? (
        <section className="knowledge-context">
          <h2>Context</h2>
          <p>{context.body}</p>
        </section>
      ) : null}

      {practice?.body ? (
        <section className="knowledge-practice">
          <h2>Practice and remember</h2>
          <p>{practice.body}</p>
        </section>
      ) : null}

      <TrustPanel
        open={sourceOpen}
        onOpenChange={setSourceOpen}
        rows={[
          { label: "Source status", value: pkg.record.source_status },
          { label: "Dossier", value: pkg.source_dossier.decision },
          { label: "Version", value: pkg.record.record_version },
          {
            label: "Canonical hash",
            value: <code>{pkg.record.canonical_text_hash}</code>,
          },
          { label: "Roadmap ref", value: pkg.record.roadmap_ref || "—" },
        ]}
      />

      <section className="knowledge-downloads" aria-label="Downloads">
        <h2>Download</h2>
        <p className="hint">Study-neutral exports from canonical structured data. PDF/UA is not claimed.</p>
        <div className="knowledge-download-actions">
          <a className="bhava-button bhava-button--primary" href={`/api/studio/knowledge/export/${pkg.record.slug}?format=pdf`}>
            Download PDF
          </a>
          <a className="bhava-button" href={`/api/studio/knowledge/export/${pkg.record.slug}?format=docx`}>
            Download DOCX
          </a>
        </div>
      </section>
      <p className="hint">
        Default lens recommendation: {DEFAULT_LENS}. Lens preference stored in sessionStorage after explicit
        selection only.
      </p>
    </article>
  );
}
