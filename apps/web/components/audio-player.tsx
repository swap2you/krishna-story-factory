"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@bhava/ui";

type Props = {
  src: string;
  title: string;
  storyNo: string;
  posterUrl?: string | null;
  onAudioMount?: (el: HTMLAudioElement) => void;
};

const SPEEDS = [0.75, 1, 1.25, 1.5, 2] as const;

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function AudioPlayer({ src, title, storyNo, posterUrl, onAudioMount }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [volume, setVolume] = useState(1);
  const [peaks, setPeaks] = useState<number[]>([]);
  const [sleepMinutes, setSleepMinutes] = useState<number | null>(null);
  const resumeKey = `bhava:resume:${storyNo}`;
  const bookmarkKey = `bhava:bookmark:${storyNo}`;

  useEffect(() => {
    if (audioRef.current && onAudioMount) onAudioMount(audioRef.current);
  }, [onAudioMount]);

  useEffect(() => {
    let cancelled = false;
    async function loadWaveform() {
      let ctx: AudioContext | null = null;
      try {
        const response = await fetch(src);
        if (!response.ok) throw new Error(`audio ${response.status}`);
        const buffer = await response.arrayBuffer();
        ctx = new AudioContext();
        const decoded = await ctx.decodeAudioData(buffer.slice(0));
        const channel = decoded.getChannelData(0);
        const bars = 96;
        const block = Math.floor(channel.length / bars);
        const next: number[] = [];
        for (let i = 0; i < bars; i += 1) {
          let sum = 0;
          const start = i * block;
          for (let j = 0; j < block; j += 1) sum += Math.abs(channel[start + j] || 0);
          next.push(sum / block);
        }
        const max = Math.max(...next, 0.0001);
        if (!cancelled) setPeaks(next.map((value) => value / max));
      } catch {
        if (!cancelled) setPeaks(Array.from({ length: 64 }, (_, i) => 0.25 + ((i * 17) % 40) / 100));
      } finally {
        if (ctx) {
          try {
            await ctx.close();
          } catch {
            /* already closed or unsupported */
          }
        }
      }
    }
    void loadWaveform();
    return () => {
      cancelled = true;
    };
  }, [src]);

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
    if (saved > 0) audio.currentTime = saved;
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

  useEffect(() => {
    if (!("mediaSession" in navigator) || !audioRef.current) return;
    navigator.mediaSession.metadata = new MediaMetadata({
      title,
      artist: "Bhāva",
      album: "Krishna Book Stories",
      artwork: posterUrl ? [{ src: posterUrl, sizes: "512x512", type: "image/png" }] : [],
    });
    navigator.mediaSession.setActionHandler("play", () => void toggle());
    navigator.mediaSession.setActionHandler("pause", () => void toggle());
    navigator.mediaSession.setActionHandler("seekbackward", () => skip(-15));
    navigator.mediaSession.setActionHandler("seekforward", () => skip(15));
  });

  const remaining = useMemo(() => Math.max(0, duration - current), [duration, current]);

  const toggle = useCallback(async () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      await audio.play();
      setPlaying(true);
    } else {
      audio.pause();
      setPlaying(false);
    }
  }, []);

  const skip = useCallback((delta: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.min(duration || audio.duration || 0, Math.max(0, audio.currentTime + delta));
  }, [duration]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      if (event.code === "Space") {
        event.preventDefault();
        void toggle();
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
      />
      <canvas
        ref={canvasRef}
        className="waveform-canvas"
        width={640}
        height={72}
        role="img"
        aria-label="Narration waveform"
        onClick={(event) => {
          const audio = audioRef.current;
          if (!audio || !duration) return;
          const rect = event.currentTarget.getBoundingClientRect();
          const ratio = (event.clientX - rect.left) / rect.width;
          audio.currentTime = ratio * duration;
        }}
      />
      <div className="audio-controls">
        <Button variant="accent" aria-label={playing ? "Pause" : "Play"} onClick={() => void toggle()}>
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
        <span aria-live="polite">{formatTime(current)} / −{formatTime(remaining)}</span>
      </div>
      <div className="audio-controls">
        <Button
          variant="quiet"
          onClick={() => {
            localStorage.setItem(bookmarkKey, String(current));
          }}
        >
          Bookmark position
        </Button>
        <Button
          variant="quiet"
          onClick={() => {
            const saved = Number(localStorage.getItem(bookmarkKey) || "0");
            if (audioRef.current) audioRef.current.currentTime = saved;
          }}
        >
          Jump to bookmark
        </Button>
        <label>
          Sleep timer
          <select
            aria-label="Sleep timer"
            value={sleepMinutes ?? ""}
            onChange={(event) => setSleepMinutes(event.target.value ? Number(event.target.value) : null)}
          >
            <option value="">Off</option>
            <option value="5">5 min</option>
            <option value="15">15 min</option>
            <option value="30">30 min</option>
          </select>
        </label>
        <a className="bhava-button bhava-button--quiet" href={src} download>
          Download audio
        </a>
      </div>
      <p className="hint">Keyboard: Space play/pause · ← −15s · → +15s. Progress resumes on this device.</p>
    </div>
  );
}
