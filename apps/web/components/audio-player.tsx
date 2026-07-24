"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@bhava/ui";

type Props = {
  src: string;
  title: string;
  storyNo: string;
  posterUrl?: string | null;
  onAudioMount?: (el: HTMLAudioElement) => void;
  peaksUrl?: string | null;
};

/** Observable playback path for diagnostics and UAT (local UI only). */
export type PlaybackPath =
  | "idle"
  | "native_starting"
  | "native_playing"
  | "native_failed"
  | "blob_fetching"
  | "blob_ready"
  | "blob_playing"
  | "failed";

const SPEEDS = [0.75, 1, 1.25, 1.5, 2] as const;
const BLOB_CACHE = new Map<string, string>();
const NATIVE_PROBE_MS = 900;

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  if (target.isContentEditable) return true;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || tag === "BUTTON" || tag === "A") {
    return true;
  }
  if (
    target.closest(
      "input, textarea, select, button, a, [role='button'], [contenteditable='true'], [role='dialog'], [aria-modal='true']",
    )
  ) {
    return true;
  }
  return false;
}

function absoluteUrl(src: string): string {
  if (typeof window === "undefined") return src;
  try {
    return new URL(src, window.location.origin).href;
  } catch {
    return src;
  }
}

function isAllowlistedAudioUrl(url: string): boolean {
  try {
    const parsed = new URL(url, typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1");
    if (typeof window !== "undefined" && parsed.origin !== window.location.origin) return false;
    return /narration\.mp3$/i.test(parsed.pathname);
  } catch {
    return false;
  }
}

async function waitForAdvancement(audio: HTMLAudioElement, minTime = 0.05, timeoutMs = 2500): Promise<boolean> {
  const start = performance.now();
  const baseline = audio.currentTime;
  while (performance.now() - start < timeoutMs) {
    if (audio.error) return false;
    if (!audio.paused && audio.readyState >= 2 && audio.currentTime > Math.max(minTime, baseline + 0.02)) {
      return true;
    }
    await new Promise((r) => setTimeout(r, 80));
  }
  return !audio.paused && audio.readyState >= 2 && audio.currentTime > Math.max(minTime, baseline + 0.02);
}

export function AudioPlayer({ src, title, storyNo, posterUrl, onAudioMount, peaksUrl }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const activeSrcRef = useRef<string>(src);
  const fetchInFlight = useRef<Promise<string> | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [volume, setVolume] = useState(1);
  const [path, setPath] = useState<PlaybackPath>("idle");
  const [status, setStatus] = useState<string | null>(null);
  const [peaks, setPeaks] = useState<number[]>(() =>
    Array.from({ length: 64 }, (_, i) => 0.25 + ((i * 17) % 40) / 100),
  );
  const [sleepMinutes, setSleepMinutes] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resumeKey = `bhava:resume:${storyNo}`;
  const bookmarkKey = `bhava:bookmark:${storyNo}`;

  const revokeObjectUrl = useCallback(() => {
    if (objectUrlRef.current) {
      // Keep shared story cache; only clear the element-local ref pointer.
      objectUrlRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (audioRef.current && onAudioMount) onAudioMount(audioRef.current);
  }, [onAudioMount]);

  useEffect(() => {
    let cancelled = false;
    async function loadPeaks() {
      const url = peaksUrl ?? `/api/v1/stories/${storyNo}/waveform`;
      try {
        const response = await fetch(url);
        if (!response.ok) return;
        const data = (await response.json()) as { peaks?: number[] };
        if (!cancelled && Array.isArray(data.peaks) && data.peaks.length > 0) {
          setPeaks(data.peaks);
        }
      } catch {
        /* keep decorative peaks */
      }
    }
    void loadPeaks();
    return () => {
      cancelled = true;
    };
  }, [peaksUrl, storyNo]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || peaks.length === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);
    const progress = duration ? current / duration : 0;
    const barWidth = width / peaks.length;
    peaks.forEach((peak, index) => {
      const barHeight = Math.max(4, peak * height * 0.9);
      const x = index * barWidth;
      const y = (height - barHeight) / 2;
      ctx.fillStyle = index / peaks.length <= progress ? "#e7b550" : "rgba(255,250,240,0.35)";
      ctx.fillRect(x + 1, y, Math.max(2, barWidth - 2), barHeight);
    });
  }, [peaks, current, duration]);

  // Story change: reset UI. Do not call load() (DEF-06 native stall class).
  useEffect(() => {
    const audio = audioRef.current;
    activeSrcRef.current = src;
    setPlaying(false);
    setCurrent(0);
    setDuration(0);
    setError(null);
    setStatus(null);
    setPath("idle");
    revokeObjectUrl();
    fetchInFlight.current = null;
    if (!audio || !src) return;
    audio.pause();
    audio.removeAttribute("src");
    // Prefer cached blob if present; otherwise leave src unset until Play (blob-first).
    const cached = BLOB_CACHE.get(absoluteUrl(src));
    if (cached) {
      audio.src = cached;
      objectUrlRef.current = cached;
      setPath("blob_ready");
    }
  }, [src, revokeObjectUrl]);

  useEffect(() => () => {
    revokeObjectUrl();
    fetchInFlight.current = null;
  }, [revokeObjectUrl]);

  useEffect(() => {
    if (sleepMinutes == null) return;
    const timer = window.setTimeout(() => {
      const audio = audioRef.current;
      if (audio) {
        audio.pause();
        setPlaying(false);
      }
      setSleepMinutes(null);
    }, sleepMinutes * 60_000);
    return () => window.clearTimeout(timer);
  }, [sleepMinutes]);

  const remaining = useMemo(() => Math.max(0, duration - current), [duration, current]);

  const skip = useCallback((delta: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.min(duration || audio.duration || 0, Math.max(0, audio.currentTime + delta));
  }, [duration]);

  const ensureBlobUrl = useCallback(async (mediaSrc: string): Promise<string> => {
    if (!isAllowlistedAudioUrl(mediaSrc)) {
      throw new Error("Audio URL is not an allowlisted story narration endpoint");
    }
    const cached = BLOB_CACHE.get(mediaSrc);
    if (cached) return cached;
    if (fetchInFlight.current) return fetchInFlight.current;
    const pending = (async () => {
      setPath("blob_fetching");
      setStatus("Loading narration…");
      const response = await fetch(mediaSrc, { cache: "force-cache" });
      if (!response.ok) throw new Error(`Audio fetch failed (${response.status})`);
      const contentType = (response.headers.get("content-type") || "").toLowerCase();
      if (contentType && !contentType.includes("audio") && !contentType.includes("mpeg") && !contentType.includes("octet-stream")) {
        throw new Error(`Unexpected audio content-type: ${contentType}`);
      }
      const blob = await response.blob();
      if (!blob.size) throw new Error("Audio response was empty");
      const typed = blob.type && blob.type.includes("audio") ? blob : new Blob([blob], { type: "audio/mpeg" });
      const objectUrl = URL.createObjectURL(typed);
      BLOB_CACHE.set(mediaSrc, objectUrl);
      return objectUrl;
    })();
    fetchInFlight.current = pending;
    try {
      return await pending;
    } finally {
      fetchInFlight.current = null;
    }
  }, []);

  // Prefetch allowlisted narration so Play can start synchronously (preserve user gesture).
  useEffect(() => {
    if (!src) return;
    const mediaSrc = absoluteUrl(src);
    let cancelled = false;
    void ensureBlobUrl(mediaSrc)
      .then((objectUrl) => {
        if (cancelled) return;
        objectUrlRef.current = objectUrl;
        setPath((prev) => (prev === "idle" ? "blob_ready" : prev));
      })
      .catch(() => {
        /* Play will surface the error */
      });
    return () => {
      cancelled = true;
    };
  }, [src, ensureBlobUrl]);

  const playViaBlob = useCallback(async (audio: HTMLAudioElement, mediaSrc: string) => {
    setStatus("Loading narration…");
    const objectUrl = await ensureBlobUrl(mediaSrc);
    objectUrlRef.current = objectUrl;
    setPath("blob_ready");
    const saved = Number(localStorage.getItem(resumeKey) || "0");
    audio.pause();
    if (!audio.src.startsWith("blob:") || audio.src !== objectUrl) {
      audio.src = objectUrl;
      audio.load();
    }
    await new Promise<void>((resolve, reject) => {
      const onReady = () => {
        cleanup();
        resolve();
      };
      const onErr = () => {
        cleanup();
        reject(new Error("Blob audio failed to load"));
      };
      const cleanup = () => {
        audio.removeEventListener("loadedmetadata", onReady);
        audio.removeEventListener("canplay", onReady);
        audio.removeEventListener("error", onErr);
      };
      if (audio.readyState >= 2) {
        resolve();
        return;
      }
      audio.addEventListener("loadedmetadata", onReady, { once: true });
      audio.addEventListener("canplay", onReady, { once: true });
      audio.addEventListener("error", onErr, { once: true });
    });
    if (saved > 0 && Number.isFinite(saved) && audio.duration && saved < audio.duration) {
      audio.currentTime = saved;
    }
    try {
      await audio.play();
    } catch (err: unknown) {
      const name = err instanceof DOMException ? err.name : "";
      if (name === "NotAllowedError") {
        setPath("blob_ready");
        setStatus("Narration ready — press Play");
        setPlaying(false);
        return;
      }
      throw err;
    }
    const ok = await waitForAdvancement(audio, 0.05, 4000);
    if (!ok) throw new Error("Compatible playback did not advance");
    setPath("blob_playing");
    setStatus(null);
    setPlaying(true);
  }, [ensureBlobUrl, resumeKey]);

  const toggle = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    setError(null);

    if (!audio.paused) {
      audio.pause();
      setPlaying(false);
      return;
    }

    const mediaSrc = absoluteUrl(activeSrcRef.current || src);
    const cached = BLOB_CACHE.get(mediaSrc) || objectUrlRef.current;

    // Synchronous gesture path when blob is already cached from prefetch.
    if (cached) {
      objectUrlRef.current = cached;
      if (audio.src !== cached) {
        audio.src = cached;
      }
      setPath("blob_fetching");
      setStatus("Loading narration…");
      const playPromise = audio.play();
      void (async () => {
        try {
          if (playPromise) await playPromise;
          const ok = await waitForAdvancement(audio, 0.05, 4000);
          if (!ok) {
            await playViaBlob(audio, mediaSrc);
            return;
          }
          setPath("blob_playing");
          setStatus(null);
          setPlaying(true);
        } catch (err: unknown) {
          try {
            await playViaBlob(audio, mediaSrc);
          } catch (fallbackErr: unknown) {
            setPlaying(false);
            setPath("failed");
            const message = fallbackErr instanceof Error ? fallbackErr.message : "Playback failed";
            setError(`Narration unavailable. Download audio or retry. (${message})`);
            setStatus(null);
          }
        }
      })();
      return;
    }

    void (async () => {
      try {
        setPath("blob_fetching");
        setStatus("Loading narration…");
        await playViaBlob(audio, mediaSrc);
      } catch (err: unknown) {
        setPlaying(false);
        setPath("failed");
        const message = err instanceof Error ? err.message : "Playback failed";
        setError(`Narration unavailable. Download audio or retry. (${message})`);
        setStatus(null);
      }
    })();
  }, [playViaBlob, src]);

  useEffect(() => {
    if (!("mediaSession" in navigator) || !audioRef.current) return;
    navigator.mediaSession.metadata = new MediaMetadata({
      title,
      artist: "Bhāva",
      album: "Krishna Book Stories",
      artwork: posterUrl ? [{ src: posterUrl, sizes: "512x512", type: "image/png" }] : [],
    });
    navigator.mediaSession.setActionHandler("play", () => toggle());
    navigator.mediaSession.setActionHandler("pause", () => toggle());
    navigator.mediaSession.setActionHandler("seekbackward", () => skip(-15));
    navigator.mediaSession.setActionHandler("seekforward", () => skip(15));
  }, [title, posterUrl, toggle, skip]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (isEditableTarget(event.target)) return;
      if (document.querySelector("[aria-modal='true'], [role='dialog']")) return;
      if (event.code === "Space") {
        event.preventDefault();
        toggle();
      } else if (event.key === "ArrowLeft") skip(-15);
      else if (event.key === "ArrowRight") skip(15);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [skip, toggle]);

  const showPause = playing && current > 0.02;

  return (
    <div className="audio-player" aria-label={`Audio player for ${title}`} data-playback-path={path}>
      <audio
        ref={audioRef}
        preload="none"
        onTimeUpdate={(event) => {
          const value = event.currentTarget.currentTime;
          setCurrent(value);
          localStorage.setItem(resumeKey, String(value));
          if (!event.currentTarget.paused && value > 0.02) {
            setPlaying(true);
          }
        }}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || 0)}
        onPlaying={() => {
          /* only mark playing after advancement via waitForAdvancement / timeupdate */
        }}
        onPlay={() => {
          /* do not set Pause from optimistic play events (DEF-06) */
        }}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
        onError={() => {
          setPlaying(false);
          setPath("failed");
          setError("Narration unavailable. Download audio or retry.");
        }}
      />
      <canvas
        ref={canvasRef}
        className="waveform-canvas"
        width={640}
        height={72}
        role="img"
        aria-label="Narration waveform preview"
        onClick={(event) => {
          const audio = audioRef.current;
          if (!audio || !duration) return;
          const rect = event.currentTarget.getBoundingClientRect();
          const ratio = (event.clientX - rect.left) / rect.width;
          audio.currentTime = ratio * duration;
        }}
      />
      <div className="audio-controls">
        <Button variant="accent" aria-label={showPause ? "Pause" : "Play"} onClick={toggle}>
          {showPause ? "Pause" : path === "blob_fetching" || path === "native_starting" ? "Loading…" : "Play"}
        </Button>
        <Button variant="quiet" aria-label="Back 15 seconds" onClick={() => skip(-15)}>−15s</Button>
        <Button variant="quiet" aria-label="Forward 15 seconds" onClick={() => skip(15)}>+15s</Button>
        <label>
          Speed
          <select
            aria-label="Playback speed"
            value={speed}
            onChange={(event) => {
              const next = Number(event.target.value) as (typeof SPEEDS)[number];
              setSpeed(next);
              if (audioRef.current) audioRef.current.playbackRate = next;
            }}
          >
            {SPEEDS.map((value) => (
              <option key={value} value={value}>{value}×</option>
            ))}
          </select>
        </label>
        <label>
          Volume
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={volume}
            aria-label="Volume"
            onChange={(event) => {
              const next = Number(event.target.value);
              setVolume(next);
              if (audioRef.current) audioRef.current.volume = next;
            }}
          />
        </label>
        <label>
          Sleep
          <select
            aria-label="Sleep timer"
            value={sleepMinutes ?? ""}
            onChange={(event) => {
              const raw = event.target.value;
              setSleepMinutes(raw ? Number(raw) : null);
            }}
          >
            <option value="">Off</option>
            <option value="15">15 min</option>
            <option value="30">30 min</option>
            <option value="45">45 min</option>
          </select>
        </label>
        <Button
          variant="quiet"
          onClick={() => {
            localStorage.setItem(bookmarkKey, String(current));
          }}
        >
          Bookmark
        </Button>
        <a className="bhava-button bhava-button--quiet" href={src} download>
          Download
        </a>
      </div>
      <p className="hint" aria-live="polite">
        {formatTime(current)} / {formatTime(duration)} · remaining {formatTime(remaining)}
        {status ? ` · ${status}` : ""}
      </p>
      {error ? (
        <div role="alert" className="hint" style={{ color: "var(--bhava-saffron)" }}>
          <p>{error}</p>
          <Button
            variant="quiet"
            onClick={() => {
              setError(null);
              setPath("idle");
              toggle();
            }}
          >
            Retry
          </Button>
        </div>
      ) : null}
      <p className="hint">Keyboard: Space play/pause · ← −15s · → +15s (disabled while a dialog is open). Progress resumes on this device.</p>
    </div>
  );
}
