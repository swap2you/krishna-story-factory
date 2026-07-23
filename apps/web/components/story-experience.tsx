"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { Button, Tabs, Toast, useToast } from "@bhava/ui";
import Link from "next/link";
import type { Story } from "@/lib/catalog";
import { AudioPlayer } from "@/components/audio-player";

type Mode = "default" | "sepia" | "dark";

type SyncCue = {
  sentence_index: number;
  start_sec: number;
  end_sec: number;
  text: string;
};

type SyncData = {
  status: string;
  method?: string;
  confidence?: number;
  cues: SyncCue[];
};

type SourceLink = {
  label?: string;
  reference?: string;
  permissions_status?: string;
  provenance?: string;
  content_type?: string;
  review_status?: string;
  reviewer?: string;
  reviewed_date?: string;
  vedabase_url?: string | null;
  chapter_title?: string;
  chapter_number?: number;
  passage_start?: string;
  passage_end?: string;
  permissions_note?: string;
  work?: string;
  author?: string;
};

type Reflection = {
  text: string;
  source?: string;
  provenance?: string;
  source_type?: string;
  reviewer?: string;
  reviewed_date?: string;
};

type ShlokaPayload = {
  shlokas: Array<Record<string, unknown>>;
  status?: string;
  note?: string;
};

type NotesSaveState = "idle" | "typing" | "saving" | "saved";

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

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function addHeadingIds(html: string): { html: string; headings: Array<{ id: string; level: number; text: string }> } {
  const headings: Array<{ id: string; level: number; text: string }> = [];
  let idx = 0;
  const processed = html.replace(/<h([23])>(.*?)<\/h[23]>/gi, (_match, level: string, content: string) => {
    const id = `section-${idx++}`;
    headings.push({ id, level: parseInt(level), text: content.replace(/<[^>]*>/g, "") });
    return `<h${level} id="${id}">${content}</h${level}>`;
  });
  return { html: processed, headings };
}

/* ── Phase 5: Sticky mini-player ──────────────────────────────── */

function MiniPlayer({ audioEl, title }: { audioEl: HTMLAudioElement; title: string }) {
  const [playing, setPlaying] = useState(!audioEl.paused);
  const [current, setCurrent] = useState(audioEl.currentTime);
  const [duration, setDuration] = useState(audioEl.duration || 0);

  useEffect(() => {
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    const onEnded = () => setPlaying(false);
    const onTime = () => setCurrent(audioEl.currentTime);
    const onMeta = () => setDuration(audioEl.duration || 0);

    setPlaying(!audioEl.paused);
    setCurrent(audioEl.currentTime);
    setDuration(audioEl.duration || 0);

    audioEl.addEventListener("play", onPlay);
    audioEl.addEventListener("pause", onPause);
    audioEl.addEventListener("ended", onEnded);
    audioEl.addEventListener("timeupdate", onTime);
    audioEl.addEventListener("loadedmetadata", onMeta);
    return () => {
      audioEl.removeEventListener("play", onPlay);
      audioEl.removeEventListener("pause", onPause);
      audioEl.removeEventListener("ended", onEnded);
      audioEl.removeEventListener("timeupdate", onTime);
      audioEl.removeEventListener("loadedmetadata", onMeta);
    };
  }, [audioEl]);

  const toggle = useCallback(() => {
    if (audioEl.paused) void audioEl.play();
    else audioEl.pause();
  }, [audioEl]);

  const skip = useCallback(
    (delta: number) => {
      audioEl.currentTime = Math.min(audioEl.duration || 0, Math.max(0, audioEl.currentTime + delta));
    },
    [audioEl],
  );

  const progress = duration ? current / duration : 0;

  return (
    <div className="mini-player" role="region" aria-label="Mini audio player">
      <button className="mini-player-btn" onClick={toggle} aria-label={playing ? "Pause" : "Play"}>
        {playing ? "\u23F8" : "\u25B6"}
      </button>
      <span className="mini-player-title">{title}</span>
      <button className="mini-player-skip" onClick={() => skip(-15)} aria-label="Back 15 seconds">&minus;15</button>
      <div
        className="mini-player-progress"
        role="progressbar"
        aria-valuenow={Math.round(current)}
        aria-valuemax={Math.round(duration)}
        onClick={(e) => {
          if (!duration) return;
          const rect = e.currentTarget.getBoundingClientRect();
          audioEl.currentTime = ((e.clientX - rect.left) / rect.width) * duration;
        }}
      >
        <div className="mini-player-bar" style={{ width: `${progress * 100}%` }} />
      </div>
      <button className="mini-player-skip" onClick={() => skip(15)} aria-label="Forward 15 seconds">+15</button>
      <span className="mini-player-time">{formatTime(current)} / {formatTime(duration)}</span>
    </div>
  );
}

/* ── Phase 5: Previous / Next story nav ───────────────────────── */

function StoryNav({ storyNo }: { storyNo: string }) {
  const num = parseInt(storyNo, 10);
  if (isNaN(num) || num <= 0) return null;
  const prev = num > 1 ? String(num - 1).padStart(3, "0") : null;
  const next = String(num + 1).padStart(3, "0");
  return (
    <nav className="story-nav" aria-label="Story navigation">
      {prev ? (
        <Link href={`/stories/${prev}`} className="bhava-button bhava-button--quiet">&larr; Story {prev}</Link>
      ) : (
        <span />
      )}
      <Link href={`/stories/${next}`} className="bhava-button bhava-button--quiet">Story {next} &rarr;</Link>
    </nav>
  );
}

/* ── Main component ───────────────────────────────────────────── */

export function StoryExperience({ story, storyNo }: { story: Story | null; storyNo: string }) {
  const [large, setLarge] = useState(false);
  const [mode, setMode] = useState<Mode>("default");
  const [notes, setNotes] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [loadingMd, setLoadingMd] = useState(false);
  const [audioEl, setAudioEl] = useState<HTMLAudioElement | null>(null);
  const [showMini, setShowMini] = useState(false);
  const [syncData, setSyncData] = useState<SyncData | null>(null);
  const [audioTime, setAudioTime] = useState(0);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [carouselOpen, setCarouselOpen] = useState(false);
  const [sourceLinks, setSourceLinks] = useState<SourceLink[] | null>(null);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [shlokaPayload, setShlokaPayload] = useState<ShlokaPayload | null>(null);
  const [revealShlokaMeta, setRevealShlokaMeta] = useState(false);
  const [notesSaveState, setNotesSaveState] = useState<NotesSaveState>("idle");
  const [notesDirty, setNotesDirty] = useState(false);

  const { message, showToast } = useToast();
  const playerContainerRef = useRef<HTMLDivElement>(null);
  const carouselDialogRef = useRef<HTMLDivElement>(null);
  const carouselCloseRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const touchStartRef = useRef(0);

  const key = `bhava:notes:${storyNo}`;
  const title = story?.title ?? `Krishna Book story ${storyNo}`;
  const dialogTitleId = useId();
  const readerSrc = story?.reader_url ?? (story ? `/api/v1/stories/${storyNo}/reader` : null);

  /* ── Derived ──────────────────────────────────────────────── */

  const coloring = useMemo(
    () =>
      [
        { label: "Story poster", url: story?.poster_url },
        { label: "Simple coloring", url: story?.simple_coloring_url },
        { label: "Detailed coloring", url: story?.coloring_url },
      ].filter((item): item is { label: string; url: string } => !!item.url),
    [story?.poster_url, story?.simple_coloring_url, story?.coloring_url],
  );

  const { html: readingHtmlWithIds, headings: sectionHeadings } = useMemo(() => {
    let base: string;
    if (markdown.trim()) {
      base = renderMarkdown(markdown);
    } else if (story?.summary) {
      base = renderMarkdown(story.summary);
    } else {
      base = "<p>Story text will appear here when <code>story.md</code> is available from the local catalog.</p>";
    }
    return addHeadingIds(base);
  }, [markdown, story?.summary]);

  const currentCueIndex = useMemo(() => {
    if (!syncData || syncData.status !== "aligned" || !syncData.cues.length) return -1;
    return syncData.cues.findIndex((c) => audioTime >= c.start_sec && audioTime < c.end_sec);
  }, [syncData, audioTime]);

  /* ── Effects ──────────────────────────────────────────────── */

  useEffect(() => {
    setNotes(localStorage.getItem(key) ?? "");
    setNotesDirty(false);
    setNotesSaveState("idle");
  }, [key]);

  useEffect(() => {
    if (!notesDirty) return;
    setNotesSaveState("typing");
    const timer = window.setTimeout(() => {
      setNotesSaveState("saving");
      localStorage.setItem(key, notes);
      setNotesSaveState("saved");
      setNotesDirty(false);
    }, 600);
    return () => window.clearTimeout(timer);
  }, [notes, key, notesDirty]);

  useEffect(() => {
    if (!readerSrc) {
      setMarkdown("");
      return;
    }
    setLoadingMd(true);
    const controller = new AbortController();
    void (async () => {
      try {
        const response = await fetch(readerSrc, { signal: controller.signal });
        if (!response.ok) { setMarkdown(""); return; }
        setMarkdown(await response.text());
      } catch {
        if (!controller.signal.aborted) setMarkdown("");
      } finally {
        if (!controller.signal.aborted) setLoadingMd(false);
      }
    })();
    return () => controller.abort();
  }, [readerSrc]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/v1/stories/${storyNo}/sync`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!controller.signal.aborted) setSyncData(data ?? { status: "needs_alignment", cues: [] });
      })
      .catch(() => {
        if (!controller.signal.aborted) setSyncData({ status: "needs_alignment", cues: [] });
      });
    return () => controller.abort();
  }, [storyNo]);

  useEffect(() => {
    const controller = new AbortController();
    setRevealShlokaMeta(false);
    void (async () => {
      try {
        const [linksRes, reflectionsRes, shlokasRes] = await Promise.all([
          fetch(`/api/v1/stories/${storyNo}/source-links`, { signal: controller.signal }),
          fetch(`/api/v1/stories/${storyNo}/reflections`, { signal: controller.signal }),
          fetch(`/api/v1/stories/${storyNo}/shlokas`, { signal: controller.signal }),
        ]);
        if (controller.signal.aborted) return;
        setSourceLinks(linksRes.ok ? ((await linksRes.json()) as SourceLink[]) : []);
        const reflectionData = reflectionsRes.ok ? await reflectionsRes.json() : [];
        setReflections(Array.isArray(reflectionData) ? (reflectionData as Reflection[]) : []);
        setShlokaPayload(
          shlokasRes.ok
            ? ((await shlokasRes.json()) as ShlokaPayload)
            : { shlokas: [], status: "pending", note: "not yet curated" },
        );
      } catch {
        if (!controller.signal.aborted) {
          setSourceLinks([]);
          setReflections([]);
          setShlokaPayload({ shlokas: [], status: "pending", note: "not yet curated" });
        }
      }
    })();
    return () => controller.abort();
  }, [storyNo]);

  useEffect(() => {
    if (!audioEl) return;
    const onTime = () => setAudioTime(audioEl.currentTime);
    audioEl.addEventListener("timeupdate", onTime);
    return () => audioEl.removeEventListener("timeupdate", onTime);
  }, [audioEl]);

  useEffect(() => {
    const el = playerContainerRef.current;
    if (!el || !audioEl) return;
    const observer = new IntersectionObserver(([entry]) => setShowMini(!entry.isIntersecting), { threshold: 0 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [audioEl]);

  useEffect(() => {
    if (!carouselOpen) return;
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    carouselCloseRef.current?.focus();

    const coloringLen = coloring.length;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") { e.preventDefault(); setCarouselOpen(false); return; }
      if (e.key === "ArrowLeft") { e.preventDefault(); setCarouselIndex((i) => Math.max(0, i - 1)); return; }
      if (e.key === "ArrowRight") { e.preventDefault(); setCarouselIndex((i) => Math.min(coloringLen - 1, i + 1)); return; }
      if (e.key !== "Tab") return;
      const dialog = carouselDialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(
        dialog.querySelectorAll<HTMLElement>("a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex='-1'])"),
      ).filter((el) => !el.hasAttribute("disabled"));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = prevOverflow;
      previousFocusRef.current?.focus();
    };
  }, [carouselOpen, coloring.length]);

  /* ── Handlers ─────────────────────────────────────────────── */

  const openActivityPdf = () => {
    if (!story?.activity_pdf_url) return;
    const w = window.open(story.activity_pdf_url, "_blank", "noopener,noreferrer");
    if (!w) showToast("Allow pop-ups to open the activity PDF.");
  };

  /* ── Render ───────────────────────────────────────────────── */

  return (
    <>
      {/* Phase 5: Persistent player above tabs — playback survives tab switches */}
      {story?.narration_url ? (
        <div ref={playerContainerRef} className="persistent-player">
          <AudioPlayer
            src={story.narration_url}
            title={title}
            storyNo={storyNo}
            posterUrl={story.poster_url}
            onAudioMount={setAudioEl}
          />
        </div>
      ) : null}

      {/* Phase 5: Sticky mini-player when the primary player scrolls away */}
      {showMini && audioEl ? <MiniPlayer audioEl={audioEl} title={title} /> : null}

      {/* Phase 5: Previous / Next story links */}
      <StoryNav storyNo={storyNo} />

      <Tabs tabs={["Listen", "Read", "Activities", "Coloring", "Source", "Notes", "\u015Alok\u0101s"]}>
        {(active) => (
          <div className={`reading-mode-${mode}`}>

            {/* ── Listen tab: combined listen + read-along ─── */}
            {active === "Listen" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Listen &amp; read along</h2>
                {!story?.narration_url && (
                  <p className="hint">Narration appears when the catalog provides narration.mp3.</p>
                )}

                {/* Phase 6: follow-along cues or fallback reader text */}
                {syncData?.status === "aligned" && syncData.cues.length > 0 ? (
                  <article className="reading follow-along">
                    {syncData.cues.map((cue, i) => (
                      <span
                        key={cue.sentence_index}
                        className={`follow-cue${i === currentCueIndex ? " follow-cue-active" : ""}`}
                        role="button"
                        tabIndex={0}
                        onClick={() => { if (audioEl) audioEl.currentTime = cue.start_sec; }}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            if (audioEl) audioEl.currentTime = cue.start_sec;
                          }
                        }}
                      >
                        {cue.text}{" "}
                      </span>
                    ))}
                  </article>
                ) : (
                  <>
                    {syncData && syncData.status !== "aligned" && (
                      <p className="hint follow-pending">Follow-along cues pending review</p>
                    )}
                    {loadingMd ? <p className="hint">Opening the story manuscript&hellip;</p> : null}
                    <article className="reading" dangerouslySetInnerHTML={{ __html: readingHtmlWithIds }} />
                  </>
                )}
              </div>
            )}

            {/* ── Read tab: full reader with controls ─────── */}
            {active === "Read" && (
              <div className="reader-card">
                {/* Phase 7: section nav jump links */}
                {sectionHeadings.length > 1 && (
                  <nav className="section-nav" aria-label="Story sections">
                    {sectionHeadings.map((h) => (
                      <a key={h.id} href={`#${h.id}`} className={h.level === 3 ? "section-nav-sub" : ""}>
                        {h.text}
                      </a>
                    ))}
                  </nav>
                )}
                <div className="actions" style={{ marginBottom: "1rem" }}>
                  <Button variant="quiet" onClick={() => setLarge((v) => !v)}>
                    {large ? "Standard text" : "Larger text"}
                  </Button>
                  {(["default", "sepia", "dark"] as Mode[]).map((v) => (
                    <Button key={v} variant={mode === v ? "accent" : "quiet"} onClick={() => setMode(v)}>
                      {v}
                    </Button>
                  ))}
                  <Button variant="quiet" onClick={() => window.print()}>Print</Button>
                  {readerSrc ? (
                    <a className="bhava-button bhava-button--quiet" href={`/api/v1/stories/${storyNo}/reader.txt`} download>
                      Download story text
                    </a>
                  ) : null}
                </div>
                {loadingMd ? <p className="hint">Opening the story manuscript&hellip;</p> : null}
                <article className={`reading ${large ? "large" : ""}`} dangerouslySetInnerHTML={{ __html: readingHtmlWithIds }} />
              </div>
            )}

            {/* ── Activities tab ──────────────────────────── */}
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
                      <Button variant="quiet" onClick={openActivityPdf}>Open to print</Button>
                    </div>
                    <div className="pdf-shell">
                      <iframe title={`${title} activity sheet`} src={story.activity_pdf_url} />
                    </div>
                    <p className="hint">Opens the PDF in a new tab — use your browser&rsquo;s print command from there.</p>
                  </>
                ) : (
                  <p className="hint">Activity sheet appears when activity_sheet.pdf is in the package.</p>
                )}
              </div>
            )}

            {/* ── Coloring tab: Phase 8 carousel ─────────── */}
            {active === "Coloring" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Coloring &amp; poster</h2>
                <div className="gallery">
                  {coloring.length ? (
                    coloring.map((item, idx) => (
                      <button
                        key={item.label}
                        type="button"
                        className="asset-tile"
                        onClick={() => { setCarouselIndex(idx); setCarouselOpen(true); }}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={item.url} alt={`${title} — ${item.label}`} />
                        <span>{item.label}</span>
                      </button>
                    ))
                  ) : (
                    <p className="hint">Coloring pages appear when package images are indexed.</p>
                  )}
                </div>
              </div>
            )}

            {/* ── Source tab ──────────────────────────────── */}
            {active === "Source" && (
              <div className="source-grid">
                <div className="source-card">
                  <h3>Reviewed source boundaries</h3>
                  {sourceLinks && sourceLinks.length > 0 ? (
                    <ul className="source-link-list" style={{ listStyle: "none", padding: 0, margin: "0 0 1rem" }}>
                      {sourceLinks.map((link, idx) => (
                        <li key={`${link.label ?? "ref"}-${idx}`} className="panel-card" style={{ marginBottom: "0.85rem", padding: "0.85rem 1rem" }}>
                          <p style={{ margin: "0 0 0.35rem" }}>
                            <strong>{link.label ?? "Reference"}:</strong> {link.reference ?? "—"}
                          </p>
                          {link.author ? <p className="hint" style={{ margin: "0 0 0.25rem" }}>Author: {link.author}</p> : null}
                          {(link.passage_start || link.passage_end) ? (
                            <p className="hint" style={{ margin: "0 0 0.25rem" }}>
                              Passage: {link.passage_start ?? "—"} → {link.passage_end ?? "—"}
                            </p>
                          ) : null}
                          <p className="hint" style={{ margin: "0 0 0.25rem" }}>
                            Provenance: {link.provenance ?? "pending"} · Permissions: {link.permissions_status ?? "needs-review"} · Review: {link.review_status ?? "needs_review"}
                          </p>
                          {(link.reviewer || link.reviewed_date) ? (
                            <p className="hint" style={{ margin: "0 0 0.25rem" }}>
                              Reviewed by {link.reviewer ?? "—"}{link.reviewed_date ? ` · ${link.reviewed_date}` : ""}
                            </p>
                          ) : null}
                          {link.permissions_note ? <p className="hint" style={{ margin: "0 0 0.5rem" }}>{link.permissions_note}</p> : null}
                          {link.vedabase_url ? (
                            <a className="bhava-button bhava-button--quiet" href={link.vedabase_url} target="_blank" rel="noopener noreferrer">
                              Open in Vedabase
                            </a>
                          ) : (
                            <p className="hint" style={{ margin: 0 }}>Vedabase link pending human verification.</p>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <>
                      <p><strong>Source:</strong> {story?.source_reference ?? "Pending catalog source reference."}</p>
                      <p><strong>Scripture:</strong> {story?.scripture_reference ?? "Krishna Book sequence"}</p>
                    </>
                  )}
                  <div className="source-boundary">
                    Bhāva shows reviewed package facts and boundaries. It does not republish unlicensed full BBT books, and never claims “used with permission” without a documented grant.
                  </div>
                </div>
                <div className="source-card">
                  <h3>Publication care</h3>
                  <p><strong>Quality:</strong> {story?.quality_status ?? "See package manifest."}</p>
                  <p>Stewarded for families and teachers by <strong>Svarna Gauranga Das</strong>.</p>
                </div>
              </div>
            )}

            {/* ── Notes tab ──────────────────────────────── */}
            {active === "Notes" && (
              <div className="panel-card">
                <h2 style={{ marginTop: 0 }}>Our family notes</h2>
                <p className="hint">Notes stay in this browser only (localStorage). Bhāva does not upload child notes.</p>
                <p className="hint" aria-live="polite">
                  {notesSaveState === "typing" && "Editing…"}
                  {notesSaveState === "saving" && "Saving…"}
                  {notesSaveState === "saved" && "Saved on this device"}
                  {notesSaveState === "idle" && "Autosave ready"}
                </p>
                <textarea
                  className="notes"
                  value={notes}
                  placeholder="What did you notice, feel, or want to remember?"
                  onChange={(e) => {
                    setNotesDirty(true);
                    setNotes(e.target.value);
                  }}
                />
                <div className="actions" style={{ marginTop: "1rem" }}>
                  <Button
                    onClick={() => {
                      localStorage.setItem(key, notes);
                      setNotesDirty(false);
                      setNotesSaveState("saved");
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
                  <Button
                    variant="quiet"
                    onClick={() => {
                      setNotes("");
                      setNotesDirty(false);
                      localStorage.removeItem(key);
                      setNotesSaveState("idle");
                      showToast("Notes cleared on this device.");
                    }}
                  >
                    Clear notes
                  </Button>
                </div>

                <section style={{ marginTop: "2rem" }} aria-labelledby="teaching-reflections-heading">
                  <h3 id="teaching-reflections-heading" style={{ marginBottom: "0.5rem" }}>
                    Teaching reflections
                  </h3>
                  <p className="hint">
                    Curated seeds from the package (may still need review). Separate from your private family notes.
                    These are never presented as Prabhupāda quotations.
                  </p>
                  {reflections.length > 0 ? (
                    <ul style={{ paddingLeft: "1.1rem", margin: "0.75rem 0 0" }}>
                      {reflections.map((item, idx) => (
                        <li key={`${item.source ?? "reflection"}-${idx}`} style={{ marginBottom: "0.85rem" }}>
                          <p style={{ margin: 0 }}>{item.text}</p>
                          <span className="hint">
                            {[item.source, item.provenance, item.source_type, item.reviewer, item.reviewed_date]
                              .filter(Boolean)
                              .join(" · ") || "seeded"}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="hint">Teaching reflections appear when web assets are built for this story.</p>
                  )}
                </section>
              </div>
            )}

            {/* ── Ślokas tab ─────────────────────────────── */}
            {active === "\u015Alok\u0101s" && (
              <div className="shloka-card">
                <p className="eyebrow" style={{ color: "var(--bhava-saffron)" }}>
                  {shlokaPayload?.status === "pending" || !shlokaPayload?.shlokas?.length
                    ? "Not yet curated"
                    : "Reviewed"}
                </p>
                {shlokaPayload?.shlokas?.length ? (
                  shlokaPayload.shlokas.map((verse, idx) => (
                    <article key={idx} style={{ marginBottom: "1.25rem" }}>
                      <p className="sanskrit">{String(verse.sanskrit ?? verse.devanagari ?? "—")}</p>
                      {revealShlokaMeta ? (
                        <>
                          <p><strong>Transliteration:</strong> {String(verse.transliteration ?? "—")}</p>
                          <p><strong>Word-for-word:</strong> {String(verse.word_for_word ?? verse.word_by_word ?? "—")}</p>
                          <p><strong>Translation:</strong> {String(verse.translation ?? "—")}</p>
                        </>
                      ) : (
                        <p className="hint">Meta fields hidden until you reveal them.</p>
                      )}
                    </article>
                  ))
                ) : (
                  <>
                    <p className="sanskrit" aria-hidden="true">—</p>
                    <p className="hint">Sanskrit placeholder — no verse text invented.</p>
                    {revealShlokaMeta ? (
                      <>
                        <p><strong>Transliteration:</strong> —</p>
                        <p><strong>Word-for-word:</strong> —</p>
                        <p><strong>Translation:</strong> —</p>
                      </>
                    ) : (
                      <p className="hint">Reveal stubs to preview the future layout without fabricated content.</p>
                    )}
                  </>
                )}
                <div className="actions" style={{ marginTop: "1rem" }}>
                  <Button variant="quiet" onClick={() => setRevealShlokaMeta((v) => !v)}>
                    {revealShlokaMeta ? "Hide stubs" : "Reveal stubs"}
                  </Button>
                </div>
                <p className="hint">
                  {shlokaPayload?.note ?? "Placeholders only until reviewed ślokas are supplied. We will not invent verses."}
                </p>
              </div>
            )}
          </div>
        )}
      </Tabs>

      {/* ── Phase 8: Carousel overlay ─────────────────────── */}
      {carouselOpen && coloring.length > 0 ? (
        <div className="bhava-dialog-backdrop" role="presentation" onMouseDown={() => setCarouselOpen(false)}>
          <div
            ref={carouselDialogRef}
            className="bhava-dialog carousel-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby={dialogTitleId}
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => { touchStartRef.current = e.touches[0].clientX; }}
            onTouchEnd={(e) => {
              const diff = e.changedTouches[0].clientX - touchStartRef.current;
              if (diff > 50) setCarouselIndex((i) => Math.max(0, i - 1));
              else if (diff < -50) setCarouselIndex((i) => Math.min(coloring.length - 1, i + 1));
            }}
          >
            <h2 id={dialogTitleId} style={{ marginTop: 0 }}>{coloring[carouselIndex]?.label}</h2>
            <p className="visually-hidden" aria-live="polite">
              Showing {coloring[carouselIndex]?.label}, image {carouselIndex + 1} of {coloring.length}
            </p>
            <div className="carousel-viewport">
              <button
                className="carousel-arrow carousel-prev"
                disabled={carouselIndex === 0}
                onClick={() => setCarouselIndex((i) => i - 1)}
                aria-label="Previous image"
              >
                &larr;
              </button>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={coloring[carouselIndex]?.url}
                alt={`${title} — ${coloring[carouselIndex]?.label}`}
                className="carousel-image"
              />
              <button
                className="carousel-arrow carousel-next"
                disabled={carouselIndex === coloring.length - 1}
                onClick={() => setCarouselIndex((i) => i + 1)}
                aria-label="Next image"
              >
                &rarr;
              </button>
            </div>
            <div className="carousel-thumbs" role="list" aria-label="Coloring pages">
              {coloring.map((item, i) => (
                <button
                  key={item.url}
                  type="button"
                  role="listitem"
                  className={`carousel-thumb${i === carouselIndex ? " active" : ""}`}
                  onClick={() => setCarouselIndex(i)}
                  aria-label={`Show ${item.label}`}
                  aria-current={i === carouselIndex ? "true" : undefined}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={item.url} alt="" />
                </button>
              ))}
            </div>
            {coloring.map((item, i) => (
              Math.abs(i - carouselIndex) === 1 ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={`preload-${item.url}`} src={item.url} alt="" hidden aria-hidden="true" />
              ) : null
            ))}
            <div className="carousel-position" aria-label={`Image ${carouselIndex + 1} of ${coloring.length}`}>
              {coloring.map((item, i) => (
                <button
                  key={item.label}
                  className={`carousel-dot${i === carouselIndex ? " active" : ""}`}
                  onClick={() => setCarouselIndex(i)}
                  aria-label={`Go to ${item.label}`}
                  aria-current={i === carouselIndex ? "true" : undefined}
                />
              ))}
            </div>
            <div className="actions" style={{ marginTop: "1rem" }}>
              <a className="bhava-button bhava-button--quiet" href={coloring[carouselIndex]?.url} download>Download</a>
              <Button variant="quiet" onClick={() => window.print()}>Print</Button>
              <Button ref={carouselCloseRef} variant="quiet" onClick={() => setCarouselOpen(false)}>Close</Button>
            </div>
          </div>
        </div>
      ) : null}

      <Toast message={message} />
    </>
  );
}
