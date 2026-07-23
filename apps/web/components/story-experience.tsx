"use client";

import { useEffect, useMemo, useState } from "react";
import { Button, Tabs, Toast, useToast } from "@bhava/ui";
import type { Story } from "@/lib/catalog";
import { AudioPlayer } from "@/components/audio-player";

type Mode = "default" | "sepia" | "dark" | "dyslexia";

function renderMarkdown(source: string): string {
  const escaped = source
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const withBlocks = escaped
    .replace(/^### (.*)$/gm, "<h3>$1</h3>")
    .replace(/^## (.*)$/gm, "<h2>$1</h2>")
    .replace(/^# (.*)$/gm, "<h1>$1</h1>")
    .replace(/^\s*[-*] (.*)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, (block) => `<ul>${block}</ul>`)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");

  return withBlocks
    .split(/\n{2,}/)
    .map((chunk) => {
      const trimmed = chunk.trim();
      if (!trimmed) return "";
      if (trimmed.startsWith("<h") || trimmed.startsWith("<ul") || trimmed.startsWith("<ol")) return trimmed;
      return `<p>${trimmed.replace(/\n/g, "<br/>")}</p>`;
    })
    .join("\n");
}

export function StoryExperience({ story, storyNo }: { story: Story | null; storyNo: string }) {
  const [large, setLarge] = useState(false);
  const [mode, setMode] = useState<Mode>("default");
  const [notes, setNotes] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [loadingMd, setLoadingMd] = useState(false);
  const [lightbox, setLightbox] = useState<string | null>(null);
  const { message, showToast } = useToast();
  const key = `bhava:notes:${storyNo}`;
  const title = story?.title ?? `Krishna Book story ${storyNo}`;

  useEffect(() => {
    setNotes(localStorage.getItem(key) ?? "");
  }, [key]);

  useEffect(() => {
    if (!story?.story_md_url) {
      setMarkdown("");
      return;
    }
    setLoadingMd(true);
    const controller = new AbortController();
    void (async () => {
      try {
        const response = await fetch(story.story_md_url!, { signal: controller.signal });
        if (!response.ok) {
          setMarkdown("");
          return;
        }
        setMarkdown(await response.text());
      } catch {
        if (!controller.signal.aborted) setMarkdown("");
      } finally {
        if (!controller.signal.aborted) setLoadingMd(false);
      }
    })();
    return () => controller.abort();
  }, [story?.story_md_url]);

  const readingHtml = useMemo(() => {
    if (markdown.trim()) return renderMarkdown(markdown);
    if (story?.summary) return renderMarkdown(story.summary);
    return "<p>Story text will appear here when <code>story.md</code> is available from the local catalog.</p>";
  }, [markdown, story?.summary]);

  const coloring = [
    { label: "Story poster", url: story?.poster_url },
    { label: "Detailed coloring", url: story?.coloring_url },
    { label: "Simple coloring", url: story?.simple_coloring_url },
  ].filter((item) => item.url);

  return (
    <>
      <Tabs tabs={["Listen", "Read", "Activities", "Coloring", "Source", "Notes", "Ślokas"]}>
        {(active) => (
          <div className={`reading-mode-${mode}`}>
            {active === "Listen" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Listen together</h2>
                {story?.narration_url ? (
                  <AudioPlayer
                    src={story.narration_url}
                    title={title}
                    storyNo={storyNo}
                    posterUrl={story.poster_url}
                  />
                ) : (
                  <p className="hint">Narration appears when the catalog provides narration.mp3.</p>
                )}
              </div>
            )}

            {active === "Read" && (
              <div className="reader-card">
                <div className="actions" style={{ marginBottom: "1rem" }}>
                  <Button variant="quiet" onClick={() => setLarge((value) => !value)}>
                    {large ? "Standard text" : "Larger text"}
                  </Button>
                  {(["default", "sepia", "dark", "dyslexia"] as Mode[]).map((value) => (
                    <Button key={value} variant={mode === value ? "accent" : "quiet"} onClick={() => setMode(value)}>
                      {value}
                    </Button>
                  ))}
                  <Button variant="quiet" onClick={() => window.print()}>Print</Button>
                  {story?.story_md_url ? (
                    <a className="bhava-button bhava-button--quiet" href={story.story_md_url} download>
                      Download Markdown
                    </a>
                  ) : null}
                </div>
                {loadingMd ? <p className="hint">Opening the story manuscript…</p> : null}
                <article className={`reading ${large ? "large" : ""}`} dangerouslySetInnerHTML={{ __html: readingHtml }} />
              </div>
            )}

            {active === "Activities" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Activity sheet</h2>
                {story?.activity_pdf_url ? (
                  <>
                    <div className="actions" style={{ marginBottom: "1rem" }}>
                      <a className="bhava-button bhava-button--quiet" href={story.activity_pdf_url} target="_blank" rel="noreferrer">
                        Open full tab
                      </a>
                      <a className="bhava-button bhava-button--quiet" href={story.activity_pdf_url} download>
                        Download PDF
                      </a>
                      <Button variant="quiet" onClick={() => window.open(story.activity_pdf_url!, "_blank")}>Print</Button>
                    </div>
                    <div className="pdf-shell">
                      <iframe title={`${title} activity sheet`} src={story.activity_pdf_url} />
                    </div>
                    <p className="hint">Need more room? Use Open full tab — your browser can print the PDF directly.</p>
                  </>
                ) : (
                  <p className="hint">Activity sheet appears when activity_sheet.pdf is in the package.</p>
                )}
              </div>
            )}

            {active === "Coloring" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Coloring & poster</h2>
                <div className="gallery">
                  {coloring.length ? coloring.map((item) => (
                    <button key={item.label} type="button" className="asset-tile" onClick={() => setLightbox(item.url!)}>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={item.url!} alt={item.label} />
                      <span>{item.label}</span>
                    </button>
                  )) : <p className="hint">Coloring pages appear when package images are indexed.</p>}
                </div>
                {lightbox ? (
                  <div className="bhava-dialog-backdrop" role="presentation" onMouseDown={() => setLightbox(null)}>
                    <div className="bhava-dialog" onMouseDown={(event) => event.stopPropagation()}>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={lightbox} alt="Full-screen artwork" style={{ width: "100%", borderRadius: "0.9rem" }} />
                      <div className="actions" style={{ marginTop: "1rem" }}>
                        <a className="bhava-button bhava-button--quiet" href={lightbox} download>Download</a>
                        <Button variant="quiet" onClick={() => window.print()}>Print</Button>
                        <Button variant="quiet" onClick={() => setLightbox(null)}>Close</Button>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            {active === "Source" && (
              <div className="source-grid">
                <div className="source-card">
                  <h3>Package reference</h3>
                  <p><strong>Source:</strong> {story?.source_reference ?? "Pending catalog source reference."}</p>
                  <p><strong>Scripture:</strong> {story?.scripture_reference ?? "Krishna Book sequence"}</p>
                  <div className="source-boundary">
                    Bhāva shows reviewed package facts and boundaries. It does not republish unlicensed full BBT books.
                  </div>
                </div>
                <div className="source-card">
                  <h3>Publication care</h3>
                  <p><strong>Quality:</strong> {story?.quality_status ?? "See package manifest."}</p>
                  <p>Stewarded for families and teachers by <strong>Svarna Gauranga Das</strong>.</p>
                </div>
              </div>
            )}

            {active === "Notes" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Our family notes</h2>
                <p className="hint">Notes stay in this browser only (localStorage). Bhāva does not upload child notes.</p>
                <textarea
                  className="notes"
                  value={notes}
                  placeholder="What did you notice, feel, or want to remember?"
                  onChange={(event) => setNotes(event.target.value)}
                />
                <div className="actions" style={{ marginTop: "1rem" }}>
                  <Button onClick={() => { localStorage.setItem(key, notes); showToast("Notes saved on this device."); }}>
                    Save notes
                  </Button>
                  <Button
                    variant="quiet"
                    onClick={() => {
                      const blob = new Blob([notes], { type: "text/plain;charset=utf-8" });
                      const url = URL.createObjectURL(blob);
                      const anchor = document.createElement("a");
                      anchor.href = url;
                      anchor.download = `bhava-notes-${storyNo}.txt`;
                      anchor.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    Export
                  </Button>
                  <Button variant="quiet" onClick={() => window.print()}>Print notes</Button>
                </div>
              </div>
            )}

            {active === "Ślokas" && (
              <div className="shloka-card">
                <p className="eyebrow" style={{ color: "var(--bhava-saffron)" }}>Not yet curated</p>
                <p className="sanskrit">—</p>
                <p><strong>Transliteration:</strong> —</p>
                <p><strong>Word-for-word:</strong> —</p>
                <p><strong>Translation:</strong> —</p>
                <p className="hint">Placeholders only until reviewed ślokas are supplied. We will not invent verses.</p>
              </div>
            )}
          </div>
        )}
      </Tabs>
      <Toast message={message} />
    </>
  );
}
