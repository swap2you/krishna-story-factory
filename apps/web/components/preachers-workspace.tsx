"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import type { Story } from "@/lib/catalog";

type Props = { stories: Story[] };

export function PreachersWorkspace({ stories }: Props) {
  const [selectedNo, setSelectedNo] = useState<string | null>(null);
  const selected = useMemo(
    () => stories.find((s) => s.story_no === selectedNo) ?? null,
    [stories, selectedNo],
  );

  const outlineText = useMemo(() => {
    if (!selected) return "";
    return [
      `Bhāva preacher outline — Story ${selected.story_no}`,
      selected.title,
      "",
      `Source: ${selected.source_reference ?? "See package manifest"}`,
      `Scripture: ${selected.scripture_reference ?? "See package manifest"}`,
      `Quality: ${selected.quality_status ?? "n/a"}`,
      `Age range: ${selected.age_range ?? "n/a"}`,
      "",
      "Devotional meaning / lessons:",
      "Use the released package reader and teaching reflections after human review.",
      "Do not invent Prabhupāda quotations.",
      "",
      `Story URL path: /stories/${selected.story_no}`,
    ].join("\n");
  }, [selected]);

  function exportTxt() {
    if (!selected) return;
    const blob = new Blob([outlineText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bhava-preacher-outline-${selected.story_no}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <PageIntro
        eyebrow="For preachers"
        title="Source-referenced materials for your next program."
        body="Select a reviewed story to populate outline preview, references, and export options. No fabricated quotations."
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 960 }}>
          <section className="teacher-panel">
            <h2>Story selector</h2>
            {!stories.length ? (
              <div className="coming" style={{ minHeight: "20vh" }}>
                <div><p>No catalog stories are available. Start the local API with released packages.</p></div>
              </div>
            ) : (
              <div className="scope-grid" style={{ marginTop: "1rem" }} role="listbox" aria-label="Reviewed stories">
                {stories.map((story) => {
                  const active = story.story_no === selectedNo;
                  return (
                    <button
                      key={story.story_no}
                      type="button"
                      role="option"
                      aria-selected={active}
                      className={`scope-card${active ? " is-active" : ""}`}
                      onClick={() => setSelectedNo(story.story_no)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          setSelectedNo(story.story_no);
                        }
                      }}
                      style={{ textAlign: "left", cursor: "pointer" }}
                    >
                      <h3 style={{ fontSize: "1.05rem", marginTop: 0 }}>
                        <span style={{ color: "var(--bhava-saffron)", marginRight: ".4rem" }}>#{story.story_no}</span>
                        {story.title}
                      </h3>
                      {story.source_reference ? <p style={{ margin: ".35rem 0 0", fontSize: ".88rem" }}><strong>Source:</strong> {story.source_reference}</p> : null}
                    </button>
                  );
                })}
              </div>
            )}
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }} aria-live="polite">
            <h2>Outline preview</h2>
            {!selected ? (
              <p className="hint">Select a story above to populate outline, references, and export actions.</p>
            ) : (
              <>
                <div className="source-boundary">
                  <p><strong>{selected.title}</strong> (#{selected.story_no})</p>
                  <p><strong>Source:</strong> {selected.source_reference ?? "Pending package reference"}</p>
                  <p><strong>Scripture:</strong> {selected.scripture_reference ?? "Pending"}</p>
                  <p><strong>Quality:</strong> {selected.quality_status ?? "n/a"} · <strong>Age:</strong> {selected.age_range ?? "n/a"}</p>
                  <p className="hint">
                    Devotional meaning and lessons come from the released package after review.
                    This outline does not invent quotations.
                  </p>
                  <p><Link href={`/stories/${selected.story_no}`}>Open story experience</Link></p>
                </div>
                <div className="actions" style={{ marginTop: "1rem" }}>
                  <button type="button" className="bhava-button bhava-button--accent" onClick={() => window.print()}>Print</button>
                  <button type="button" className="bhava-button bhava-button--quiet" onClick={exportTxt}>Export TXT</button>
                </div>
              </>
            )}
          </section>
        </div>
      </section>
    </>
  );
}
