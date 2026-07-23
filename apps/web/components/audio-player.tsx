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

const SPEEDS = [0.75, 1, 1.25, 1.5, 2] as const;

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
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (target.closest("input, textarea, select, [contenteditable='true'], [role='dialog'], [aria-modal='true']")) {
    return true;
  }
  return false;
}

export function AudioPlayer({ src, title, storyNo, posterUrl, onAudioMount, peaksUrl }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [volume, setVolume] = useState(1);
  const [peaks, setPeaks] = useState<number[]>(() =>
    Array.from({ length: 64 }, (_, i) => 0.25 + ((i * 17) % 40) / 100),
  );
  const [sleepMinutes, setSleepMinutes] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resumeKey = `bhava:resume:${storyNo}`;
  const bookmarkKey = `bhava:bookmark:${storyNo}`;

  useEffect(() => {
    if (audioRef.current && onAudioMount) onAudioMount(audioRef.current);
  }, [onAudioMount]);

  // Server/cached peaks only — never full-fetch the MP3 on the client for waveform.
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

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const saved = Number(localStorage.getItem(resumeKey) || "0");
    if (saved > 0 && Number.isFinite(saved)) {
      const apply = () => {
        if (audio.duration && saved < audio.duration) audio.currentTime = saved;
      };
      if (audio.readyState >= 1) apply();
      else audio.addEventListener("loadedmetadata", apply, { once: true });
    }
  }, [resumeKey, src]);

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

  const toggle = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    setError(null);
    if (audio.paused) {
      // Preserve user-activation: call play() synchronously from the click path.
      const playPromise = audio.play();
      setPlaying(true);
      if (playPromise !== undefined) {
        void playPromise.catch((err: unknown) => {
          setPlaying(false);
          const message = err instanceof Error ? err.message : "Playback failed";
          setError(`Could not start audio: ${message}`);
        });
      }
    } else {
      audio.pause();
      setPlaying(false);
    }
  }, []);

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

  return (
    <div className="audio-player" aria-label={`Audio player for ${title}`}>
      <audio
        ref={audioRef}
        src={src}
        preload="metadata"
        onTimeUpdate={(event) => {
          const value = event.currentTarget.currentTime;
          setCurrent(value);
          localStorage.setItem(resumeKey, String(value));
        }}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || 0)}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
        onError={() => {
          setPlaying(false);
          setError("Audio could not be loaded for this story.");
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
        <Button variant="accent" aria-label={playing ? "Pause" : "Play"} onClick={toggle}>
          {playing ? "Pause" : "Play"}
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
      </p>
      {error ? (
        <p role="alert" className="hint" style={{ color: "var(--bhava-saffron)" }}>{error}</p>
      ) : null}
      <p className="hint">Keyboard: Space play/pause · ← −15s · → +15s (disabled while a dialog is open). Progress resumes on this device.</p>
    </div>
  );
}
