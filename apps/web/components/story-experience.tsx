"use client";

import { useEffect, useMemo, useState } from "react";
import { Button, Tabs, Toast, useToast } from "@bhava/ui";
import type { Story } from "@/lib/catalog";
import { AudioPlayer } from "@/components/audio-player";

type Mode = "default" | "sepia" | "dark" | "dyslexia";

export function StoryExperience({ story, storyNo }: { story: Story | null; storyNo: string }) {
  const [large, setLarge] = useState(false);
  const [mode, setMode] = useState<Mode>("default");
  const [notes, setNotes] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [lightbox, setLightbox] = useState<string | null>(null);
  const { message, showToast } = useToast();
  const key = `bhava:notes:${storyNo}`;
  const title = story?.title ?? `Krishna Book story ${storyNo}`;

  useEffect(() => {
    setNotes(localStorage.getItem(key) ?? "");
  }, [key]);

  useEffect(() => {
    if (!story?.story_md_url) return;
    void fetch(story.story_md_url)
      .then((response) => (response.ok ? response.text() : ""))
      .then(setMarkdown)
      .catch(() => setMarkdown(""));
  }, [story?.story_md_url]);

  const readingHtml = useMemo(() => {
    const source = markdown || story?.summary || "Story text will appear when the local catalog provides story.md.";
    return source
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/^### (.*)$/gm, "<h3>$1</h3>")
      .replace(/^## (.*)$/gm, "<h2>$1</h2>")
      .replace(/^# (.*)$/gm, "<h1>$1</h1>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br/>");
  }, [markdown, story?.summary]);

  const coloring = [
    { label: "Poster", url: story?.poster_url },
    { label: "Detailed coloring", url: story?.coloring_url },
    { label: "Simple coloring", url: story?.simple_coloring_url },
  ].filter((item) => item.url);

  return (
    <>
      <Tabs tabs={["Listen", "Read", "Activities", "Coloring", "Source", "Notes", "Ślokas"]}>
        {(active) => (
          <div className={`story-content reading-mode-${mode}`}>
            {active === "Listen" && (
              <>
                <h2>Listen</h2>
                {story?.narration_url ? (
                  <AudioPlayer
                    src={story.narration_url}
                    title={title}
                    storyNo={storyNo}
                    posterUrl={story.poster_url}
                  />
                ) : (
                  <p>The catalog has not supplied a narration yet.</p>
                )}
              </>
            )}
            {active === "Read" && (
              <>
                <div className="actions">
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
                <article
                  className={`reading ${large ? "large" : ""}`}
                  dangerouslySetInnerHTML={{ __html: `<p>${readingHtml}</p>` }}
                />
              </>
            )}
            {active === "Activities" && (
              <>
                <h2>Activities</h2>
                {story?.activity_pdf_url ? (
                  <>
                    <div className="actions">
                      <a className="bhava-button bhava-button--quiet" href={story.activity_pdf_url} target="_blank" rel="noreferrer">
                        Open in new tab
                      </a>
                      <a className="bhava-button bhava-button--quiet" href={story.activity_pdf_url} download>
                        Download PDF
                      </a>
                      <Button variant="quiet" onClick={() => window.open(story.activity_pdf_url!, "_blank")}>Print</Button>
                    </div>
                    <iframe title={`${title} activity sheet`} src={story.activity_pdf_url} width="100%" height="640" />
                    <p className="hint">If the embedded viewer is blank, use Open in new tab — your browser can still print the PDF.</p>
                  </>
                ) : (
                  <p>Activity sheet will appear when the local catalog provides activity_sheet.pdf.</p>
                )}
              </>
            )}
            {active === "Coloring" && (
              <>
                <h2>Coloring pages</h2>
                <div className="gallery">
                  {coloring.length ? coloring.map((item) => (
                    <button
                      key={item.label}
                      type="button"
                      className="image-placeholder"
                      onClick={() => setLightbox(item.url!)}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={item.url!} alt={item.label} style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "0.7rem" }} />
                      <span>{item.label}</span>
                    </button>
                  )) : <p>Coloring images appear when the catalog provides them.</p>}
                </div>
                {lightbox ? (
                  <div className="bhava-dialog-backdrop" role="presentation" onMouseDown={() => setLightbox(null)}>
                    <div className="bhava-dialog" onMouseDown={(event) => event.stopPropagation()}>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={lightbox} alt="Full-screen artwork" style={{ width: "100%", borderRadius: "0.7rem" }} />
                      <div className="actions">
                        <a className="bhava-button bhava-button--quiet" href={lightbox} download>Download</a>
                        <Button variant="quiet" onClick={() => window.print()}>Print</Button>
                        <Button variant="quiet" onClick={() => setLightbox(null)}>Close</Button>
                      </div>
                    </div>
                  </div>
                ) : null}
              </>
            )}
            {active === "Source" && (
              <>
                <h2>Source</h2>
                <p><strong>Reference:</strong> {story?.source_reference ?? "Pending catalog source reference."}</p>
                <p><strong>Scripture:</strong> {story?.scripture_reference ?? "Krishna Book sequence"}</p>
                <p><strong>Review / quality:</strong> {story?.quality_status ?? "See package manifest."}</p>
                <p>Bhāva shows references and package facts. It does not republish unlicensed full BBT books.</p>
              </>
            )}
            {active === "Notes" && (
              <>
                <h2>Our family notes</h2>
                <p className="hint">Notes stay in this browser only (localStorage). Bhāva does not upload child notes.</p>
                <textarea
                  className="notes"
                  value={notes}
                  placeholder="What did you notice or want to remember?"
                  onChange={(event) => setNotes(event.target.value)}
                />
                <div className="actions">
                  <Button
                    onClick={() => {
                      localStorage.setItem(key, notes);
                      showToast("Notes saved on this device.");
                    }}
                  >
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
              </>
            )}
            {active === "Ślokas" && (
              <>
                <h2>Ślokas</h2>
                <p><em>Not yet curated</em> — placeholders only. Do not invent verses for Stories 001–007 until reviewed content is supplied.</p>
                <div className="bhava-card" style={{ padding: "1rem" }}>
                  <p><strong>Sanskrit:</strong> —</p>
                  <p><strong>Transliteration:</strong> —</p>
                  <p><strong>Word-for-word:</strong> —</p>
                  <p><strong>Translation:</strong> —</p>
                </div>
              </>
            )}
          </div>
        )}
      </Tabs>
      <Toast message={message} />
    </>
  );
}
