"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Button, Tabs, Toast, useToast } from "@bhava/ui";
import Link from "next/link";
import type { Story } from "@/lib/catalog";
import { AudioPlayer } from "@/components/audio-player";
import { PdfJsViewer } from "@/components/pdf-js-viewer";
import { lockBodyScroll } from "@/lib/body-scroll-lock";
import { printSelectedImage } from "@/lib/print-selected-image";

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

function renderInlineMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

export function renderMarkdown(source: string): string {
  const escaped = source
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const html: string[] = [];
  let paragraph: string[] = [];
  let items: string[] = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    html.push(`<p>${renderInlineMarkdown(paragraph.join("\n")).replace(/\n/g, "<br/>")}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!items.length) return;
    const rendered = items.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("");
    html.push(`<ul>${rendered}</ul>`);
    items = [];
  };

  for (const line of escaped.split("\n")) {
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }
    const heading = /^(#{1,3}) +(.*)$/.exec(line);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      html.push(`<h${level}>${renderInlineMarkdown(heading[2].trim())}</h${level}>`);
      continue;
    }
    const bullet = /^\s*[-*] +(.*)$/.exec(line);
    if (bullet) {
      // A list may begin immediately after prose, so close the paragraph first
      // rather than letting <ul> land inside <p> with <br/> between items.
      flushParagraph();
      items.push(bullet[1].trim());
      continue;
    }
    flushList();
    paragraph.push(line.trim());
  }
  flushParagraph();
  flushList();

  return html.join("\n");
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

/* ── True floating mini-player (portaled, fixed) ──────────────── */

function MiniPlayer({
  audioEl,
  title,
  geometry,
  onDismiss,
}: {
  audioEl: HTMLAudioElement;
  title: string;
  geometry: { top: number; left: number; width: number };
  onDismiss: () => void;
}) {
  const [playing, setPlaying] = useState(!audioEl.paused);
  const [current, setCurrent] = useState(audioEl.currentTime);
  const [duration, setDuration] = useState(audioEl.duration || 0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

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

  const seekRatio = useCallback(
    (clientX: number, el: HTMLElement) => {
      if (!duration) return;
      const rect = el.getBoundingClientRect();
      const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
      audioEl.currentTime = ratio * duration;
    },
    [audioEl, duration],
  );

  const progress = duration ? current / duration : 0;
  if (!mounted) return null;

  return createPortal(
    <div
      className="mini-player mini-player--floating"
      role="region"
      aria-label="Mini audio player"
      style={{
        top: geometry.top,
        left: geometry.left,
        width: geometry.width,
      }}
    >
      <button type="button" className="mini-player-btn" onClick={toggle} aria-label={playing ? "Pause" : "Play"}>
        {playing ? "\u23F8" : "\u25B6"}
      </button>
      <span className="mini-player-title">{title}</span>
      <button type="button" className="mini-player-skip" onClick={() => skip(-15)} aria-label="Back 15 seconds">
        &minus;15
      </button>
      <div
        className="mini-player-progress"
        role="slider"
        tabIndex={0}
        aria-label="Seek narration"
        aria-valuemin={0}
        aria-valuemax={Math.max(0, Math.round(duration))}
        aria-valuenow={Math.round(current)}
        aria-valuetext={`${formatTime(current)} of ${formatTime(duration)}`}
        onClick={(e) => seekRatio(e.clientX, e.currentTarget)}
        onKeyDown={(e) => {
          if (!duration) return;
          if (e.key === "ArrowLeft") {
            e.preventDefault();
            skip(-5);
          } else if (e.key === "ArrowRight") {
            e.preventDefault();
            skip(5);
          } else if (e.key === "Home") {
            e.preventDefault();
            audioEl.currentTime = 0;
          } else if (e.key === "End") {
            e.preventDefault();
            audioEl.currentTime = duration;
          }
        }}
      >
        <div className="mini-player-bar" style={{ width: `${progress * 100}%` }} />
      </div>
      <button type="button" className="mini-player-skip" onClick={() => skip(15)} aria-label="Forward 15 seconds">
        +15
      </button>
      <span className="mini-player-time">
        {formatTime(current)} / {formatTime(duration)}
      </span>
      <button
        type="button"
        className="mini-player-dismiss"
        onClick={onDismiss}
        aria-label="Hide floating player"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>,
    document.body,
  );
}

/* ── Phase 5: Previous / Next story nav ───────────────────────── */

function StoryNav({ storyNo, maxReleased }: { storyNo: string; maxReleased: number }) {
  const num = parseInt(storyNo, 10);
  if (isNaN(num) || num <= 0) return null;
  const prev = num > 1 ? String(num - 1).padStart(3, "0") : null;
  const hasNext = num < maxReleased;
  const next = hasNext ? String(num + 1).padStart(3, "0") : null;
  return (
    <nav className="story-nav" aria-label="Released story navigation">
      {prev ? (
        <Link href={`/stories/${prev}`} className="bhava-button bhava-button--quiet">&larr; Story {prev}</Link>
      ) : (
        <span />
      )}
      {next ? (
        <Link href={`/stories/${next}`} className="bhava-button bhava-button--quiet">Story {next} &rarr;</Link>
      ) : (
        <span className="hint" role="status">
          End of the currently published stories
        </span>
      )}
    </nav>
  );
}

/* ── Main component ───────────────────────────────────────────── */

export function StoryExperience({
  story,
  storyNo,
  maxReleased = 0,
}: {
  story: Story | null;
  storyNo: string;
  maxReleased?: number;
}) {
  const [large, setLarge] = useState(false);
  const [mode, setMode] = useState<Mode>("default");
  const [notes, setNotes] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [loadingMd, setLoadingMd] = useState(false);
  const [audioEl, setAudioEl] = useState<HTMLAudioElement | null>(null);
  const [showMini, setShowMini] = useState(false);
  const [miniDismissed, setMiniDismissed] = useState(false);
  const [miniGeometry, setMiniGeometry] = useState({ top: 82, left: 16, width: 360 });
  const [syncData, setSyncData] = useState<SyncData | null>(null);
  const [audioTime, setAudioTime] = useState(0);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [carouselOpen, setCarouselOpen] = useState(false);
  const [portalReady, setPortalReady] = useState(false);
  const [sourceLinks, setSourceLinks] = useState<SourceLink[] | null>(null);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [shlokaPayload, setShlokaPayload] = useState<ShlokaPayload | null>(null);
  const [notesSaveState, setNotesSaveState] = useState<NotesSaveState>("idle");
  const [notesDirty, setNotesDirty] = useState(false);
  const [recommendedPlaybackRate, setRecommendedPlaybackRate] = useState<number | undefined>(undefined);
  const [readerError, setReaderError] = useState(false);

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
    setMiniDismissed(false);
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
      setReaderError(false);
      return;
    }
    setLoadingMd(true);
    setReaderError(false);
    const controller = new AbortController();
    void (async () => {
      try {
        const response = await fetch(readerSrc, { signal: controller.signal });
        if (!response.ok) {
          setMarkdown("");
          setReaderError(true);
          return;
        }
        setMarkdown(await response.text());
      } catch {
        if (!controller.signal.aborted) {
          setMarkdown("");
          setReaderError(true);
        }
      } finally {
        if (!controller.signal.aborted) setLoadingMd(false);
      }
    })();
    return () => controller.abort();
  }, [readerSrc]);

  useEffect(() => {
    const controller = new AbortController();
    setRecommendedPlaybackRate(undefined);
    void fetch(`/api/v1/stories/${storyNo}/web-manifest`, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((data: { recommended_playback_rate?: unknown } | null) => {
        if (controller.signal.aborted || !data) return;
        const rate = data.recommended_playback_rate;
        if (typeof rate === "number" && Number.isFinite(rate) && rate > 0) {
          setRecommendedPlaybackRate(rate);
        }
      })
      .catch(() => {
        /* optional field */
      });
    return () => controller.abort();
  }, [storyNo]);

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
    setPortalReady(true);
  }, []);

  useEffect(() => {
    const el = playerContainerRef.current;
    if (!el || !audioEl) return;
    const observer = new IntersectionObserver(([entry]) => setShowMini(!entry.isIntersecting), { threshold: 0 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [audioEl]);

  const updateMiniGeometry = useCallback(() => {
    if (typeof window === "undefined") return;
    const header = document.querySelector<HTMLElement>(".site-header");
    const main = document.querySelector<HTMLElement>(".story-main");
    const headerBottom = header ? header.getBoundingClientRect().bottom : 74;
    const gap = 8;
    const top = Math.max(headerBottom + gap, gap);
    if (main) {
      const rect = main.getBoundingClientRect();
      const pad = 12;
      const left = Math.max(pad, rect.left + pad);
      const width = Math.max(240, Math.min(rect.width - pad * 2, window.innerWidth - left - pad));
      setMiniGeometry({ top, left, width });
      return;
    }
    const pad = 16;
    setMiniGeometry({
      top,
      left: pad,
      width: Math.max(240, Math.min(520, window.innerWidth - pad * 2)),
    });
  }, []);

  useLayoutEffect(() => {
    if (!showMini || carouselOpen) return;
    updateMiniGeometry();
    const header = document.querySelector(".site-header");
    const main = document.querySelector(".story-main");
    const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(() => updateMiniGeometry()) : null;
    if (ro && header) ro.observe(header);
    if (ro && main) ro.observe(main);
    window.addEventListener("resize", updateMiniGeometry);
    window.addEventListener("orientationchange", updateMiniGeometry);
    return () => {
      ro?.disconnect();
      window.removeEventListener("resize", updateMiniGeometry);
      window.removeEventListener("orientationchange", updateMiniGeometry);
    };
  }, [showMini, carouselOpen, updateMiniGeometry]);

  useEffect(() => {
    if (!carouselOpen) return;
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    const { unlock } = lockBodyScroll();
    const focusTimer = window.setTimeout(() => carouselCloseRef.current?.focus(), 0);

    const coloringLen = coloring.length;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        setCarouselOpen(false);
        return;
      }
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        e.stopPropagation();
        setCarouselIndex((i) => Math.max(0, i - 1));
        return;
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        e.stopPropagation();
        setCarouselIndex((i) => Math.min(coloringLen - 1, i + 1));
        return;
      }
      if (e.code === "Space") {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
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
    document.addEventListener("keydown", onKeyDown, true);
    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener("keydown", onKeyDown, true);
      // Restore focus without scrolling; unlock restores exact scrollY.
      previousFocusRef.current?.focus({ preventScroll: true });
      unlock();
    };
  }, [carouselOpen, coloring.length]);

  useEffect(() => {
    if (!carouselOpen) return;
    const dialog = carouselDialogRef.current;
    if (dialog) dialog.scrollTop = 0;
  }, [carouselOpen, carouselIndex]);

  /* ── Handlers ─────────────────────────────────────────────── */

  const openActivityPdf = () => {
    if (!story?.activity_pdf_url) return;
    const w = window.open(story.activity_pdf_url, "_blank", "noopener,noreferrer");
    if (!w) showToast("Allow pop-ups to open the activity PDF.");
  };

  const printCarouselImage = useCallback(async () => {
    const selected = coloring[carouselIndex];
    if (!selected?.url) return;
    const result = await printSelectedImage({
      imageUrl: selected.url,
      title: `${title} — ${selected.label}`,
      allowedUrls: coloring.map((item) => item.url),
    });
    if (!result.ok) {
      showToast(
        result.reason === "blocked_url"
          ? "Print is limited to this story’s package images."
          : "Could not open the print dialog. Try Download instead.",
      );
    }
  }, [carouselIndex, coloring, showToast, title]);

  /* ── Render ───────────────────────────────────────────────── */

  return (
    <>
      {story?.poster_url ? (
        <div className="story-poster-wash" aria-hidden="true" data-poster-src={story.poster_url}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={story.poster_url} alt="" decoding="async" />
        </div>
      ) : null}

      {/* Persistent player above tabs — playback survives tab switches */}
      {story?.narration_url ? (
        <div ref={playerContainerRef} className="persistent-player">
          <AudioPlayer
            key={storyNo}
            src={story.narration_url}
            title={title}
            storyNo={storyNo}
            posterUrl={story.poster_url}
            onAudioMount={setAudioEl}
            recommendedPlaybackRate={recommendedPlaybackRate}
          />
          {miniDismissed ? (
            <button
              type="button"
              className="bhava-button bhava-button--quiet mini-player-restore"
              onClick={() => setMiniDismissed(false)}
            >
              Show floating player
            </button>
          ) : null}
        </div>
      ) : null}

      {/* True floating mini-player when primary player scrolls away (hidden during image modal) */}
      {showMini && audioEl && !carouselOpen && !miniDismissed ? (
        <MiniPlayer
          audioEl={audioEl}
          title={title}
          geometry={miniGeometry}
          onDismiss={() => setMiniDismissed(true)}
        />
      ) : null}

      {/* Previous / Next story links */}
      <StoryNav storyNo={storyNo} maxReleased={maxReleased} />
      <p className="story-help-link">
        <Link href="/library/krishna-book/how-to-use">How to use Krishna Book stories</Link>
      </p>

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

                {/* Follow-along only when aligned cues exist; otherwise quiet reader text. */}
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
                    {loadingMd ? <p className="hint reader-status" role="status">Opening the story manuscript&hellip;</p> : null}
                    {readerError && !loadingMd ? (
                      <p className="hint reader-status reader-status--error" role="alert">
                        Story text could not be loaded. Try again shortly, or open the Read tab after refresh.
                      </p>
                    ) : null}
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
                {loadingMd ? <p className="hint reader-status" role="status">Opening the story manuscript&hellip;</p> : null}
                {readerError && !loadingMd ? (
                  <p className="hint reader-status reader-status--error" role="alert">
                    Story text could not be loaded. Use Download story text if available, or try again later.
                  </p>
                ) : null}
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
                      <a className="bhava-button bhava-button--quiet" href={`${story.activity_pdf_url}${story.activity_pdf_url.includes("?") ? "&" : "?"}download=1`} download>
                        Download PDF
                      </a>
                      <Button variant="quiet" onClick={openActivityPdf}>Open to print</Button>
                    </div>
                    <PdfJsViewer url={story.activity_pdf_url} title={title} />
                    <p className="hint">Open full tab or Download for print — use your browser&rsquo;s print command from there.</p>
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
                  <p>Stewarded for families and teachers by <strong>Svarna Gauranga Das</strong>.</p>
                  <p className="hint" style={{ marginTop: "0.75rem" }}>
                    © Svarna Gauranga Das · Dauji Publication · Bhāva. Scripture and preexisting
                    source texts are not claimed as original authorship. See{" "}
                    <a href="/rights">Copyright &amp; Permissions</a>.
                  </p>
                  <p className="hint">
                    A copyright notice and evidence record are not the same as formal U.S. Copyright
                    Office registration.
                  </p>
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
                  Companion scripture
                </p>
                {shlokaPayload?.shlokas?.length ? (
                  shlokaPayload.shlokas.map((verse, idx) => {
                    const reviewStatus = String(verse.review_status ?? "");
                    const notApplicable =
                      reviewStatus === "not_applicable" ||
                      String(verse.decision ?? "") === "no-separate-verse";
                    const reference = String(verse.reference ?? "").trim();
                    const explanation = String(verse.child_explanation ?? "").trim();
                    const url = typeof verse.url === "string" ? verse.url.trim() : "";
                    const sanskrit = String(verse.sanskrit ?? verse.devanagari ?? "").trim();
                    const transliteration = String(verse.transliteration ?? "").trim();
                    const translation = String(verse.translation ?? "").trim();
                    const wordForWord = String(verse.word_for_word ?? verse.word_by_word ?? "").trim();
                    const note = String(verse.note ?? "").trim();
                    const provenance = String(verse.provenance ?? "").trim();
                    const reviewer = String(verse.reviewer ?? "").trim();
                    const reviewedDate = String(verse.reviewed_date ?? "").trim();
                    const stateLabel = notApplicable
                      ? "No separate verse selected"
                      : reviewStatus === "reviewed"
                        ? "Reviewed companion reference"
                        : reviewStatus === "pending"
                          ? "Pending review"
                          : "Companion reference";
                    const chapterReference =
                      !notApplicable &&
                      (!reference || !/\d+\.\d+\.\d+/.test(reference) || reviewStatus !== "reviewed");
                    return (
                      <article key={`${reference || "shloka"}-${idx}`} className="shloka-entry" style={{ marginBottom: "1.25rem" }}>
                        <div className="shloka-entry-meta">
                          <p className="eyebrow" style={{ marginBottom: "0.35rem" }}>{stateLabel}</p>
                          {chapterReference ? (
                            <span className="shloka-badge" title="Exact verse range not yet verified">
                              Chapter reference
                            </span>
                          ) : null}
                        </div>
                        {reference ? <h3 style={{ marginTop: 0 }}>{reference}</h3> : null}
                        {explanation ? <p style={{ marginTop: "0.5rem" }}>{explanation}</p> : null}
                        {url ? (
                          <p style={{ marginTop: "0.85rem" }}>
                            <a
                              className="bhava-button bhava-button--quiet vedabase-action"
                              href={url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Read this passage on Vedabase
                              <span className="vedabase-action-icon" aria-hidden="true">
                                {" "}
                                ↗
                              </span>
                            </a>
                          </p>
                        ) : null}
                        {sanskrit ? <p className="sanskrit" lang="sa">{sanskrit}</p> : null}
                        {transliteration ? (
                          <p><strong>Transliteration:</strong> {transliteration}</p>
                        ) : null}
                        {wordForWord ? (
                          <p><strong>Word-for-word:</strong> {wordForWord}</p>
                        ) : null}
                        {translation ? (
                          <p><strong>Translation:</strong> {translation}</p>
                        ) : null}
                        {(reviewer || reviewedDate || note || provenance) ? (
                          <p className="hint" style={{ marginTop: "0.75rem" }}>
                            {[
                              reviewer ? `Reviewer: ${reviewer}` : null,
                              reviewedDate ? `Reviewed: ${reviewedDate}` : null,
                              provenance ? `Provenance: ${provenance}` : null,
                              note || null,
                            ]
                              .filter(Boolean)
                              .join(" · ")}
                          </p>
                        ) : null}
                      </article>
                    );
                  })
                ) : (
                  <p className="hint">
                    {shlokaPayload?.note ??
                      "Reviewed companion references appear when web assets are built. We will not invent verses."}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </Tabs>

      {/* Image / coloring modal viewer (portaled) */}
      {portalReady && carouselOpen && coloring.length > 0
        ? createPortal(
            <div
              className="bhava-dialog-backdrop carousel-backdrop"
              role="presentation"
              onMouseDown={() => setCarouselOpen(false)}
            >
              <div
                ref={carouselDialogRef}
                className="bhava-dialog carousel-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby={dialogTitleId}
                onMouseDown={(e) => e.stopPropagation()}
                onTouchStart={(e) => {
                  touchStartRef.current = e.touches[0].clientX;
                }}
                onTouchEnd={(e) => {
                  const diff = e.changedTouches[0].clientX - touchStartRef.current;
                  if (diff > 50) setCarouselIndex((i) => Math.max(0, i - 1));
                  else if (diff < -50) setCarouselIndex((i) => Math.min(coloring.length - 1, i + 1));
                }}
              >
                <div className="carousel-dialog-header">
                  <h2 id={dialogTitleId}>{coloring[carouselIndex]?.label}</h2>
                  <button
                    ref={carouselCloseRef}
                    type="button"
                    className="carousel-close-top"
                    aria-label="Close image viewer"
                    onClick={() => setCarouselOpen(false)}
                  >
                    <span aria-hidden="true">&times;</span>
                  </button>
                </div>
                <p className="visually-hidden" aria-live="polite">
                  Showing {coloring[carouselIndex]?.label}, image {carouselIndex + 1} of {coloring.length}
                </p>
                <div className="carousel-viewport">
                  <button
                    type="button"
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
                    type="button"
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
                {coloring.map((item, i) =>
                  Math.abs(i - carouselIndex) === 1 ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img key={`preload-${item.url}`} src={item.url} alt="" hidden aria-hidden="true" />
                  ) : null,
                )}
                <div className="carousel-position" aria-label={`Image ${carouselIndex + 1} of ${coloring.length}`}>
                  {coloring.map((item, i) => (
                    <button
                      key={item.label}
                      type="button"
                      className={`carousel-dot${i === carouselIndex ? " active" : ""}`}
                      onClick={() => setCarouselIndex(i)}
                      aria-label={`Go to ${item.label}`}
                      aria-current={i === carouselIndex ? "true" : undefined}
                    />
                  ))}
                </div>
                <div className="actions carousel-actions" style={{ marginTop: "1rem" }}>
                  <a className="bhava-button bhava-button--quiet" href={coloring[carouselIndex]?.url} download>
                    Download
                  </a>
                  <Button variant="quiet" onClick={() => void printCarouselImage()}>
                    Print
                  </Button>
                  <Button variant="quiet" onClick={() => setCarouselOpen(false)}>
                    Close
                  </Button>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      <Toast message={message} />
    </>
  );
}
