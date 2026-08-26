"use client";

import Link from "next/link";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { VANI_COLLECTION_PATH, VANI_STORAGE_PREFIX, type VaniTrack } from "@/lib/vani";

type PlayerTrack = VaniTrack & { previousId?: string | null; nextId?: string | null };

type PlayerValue = {
  active: PlayerTrack | null;
  playing: boolean;
  current: number;
  duration: number;
  speed: number;
  volume: number;
  muted: boolean;
  bookmarked: boolean;
  completed: boolean;
  sleepMinutes: number | null;
  setActive: (track: PlayerTrack) => void;
  toggle: () => void;
  seekBy: (seconds: number) => void;
  seekTo: (seconds: number) => void;
  setSpeed: (speed: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  toggleBookmark: () => void;
  toggleCompleted: () => void;
  setSleepMinutes: (minutes: number | null) => void;
};

const PlayerContext = createContext<PlayerValue | null>(null);
const SPEEDS = [0.75, 1, 1.25, 1.5, 2];

function time(value: number) {
  if (!Number.isFinite(value) || value < 0) return "0:00";
  return `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, "0")}`;
}

function readSet(key: string): Set<string> {
  try {
    const value = JSON.parse(localStorage.getItem(key) || "[]");
    return new Set(Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []);
  } catch {
    return new Set();
  }
}

function updateSet(key: string, id: string, enabled: boolean) {
  const values = readSet(key);
  if (enabled) values.add(id);
  else values.delete(id);
  localStorage.setItem(key, JSON.stringify([...values]));
  window.dispatchEvent(new CustomEvent("bhava:vani-state"));
}

export function VaniPlayerProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [active, setActiveState] = useState<PlayerTrack | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeedState] = useState(1);
  const [volume, setVolumeState] = useState(1);
  const [muted, setMuted] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [sleepMinutes, setSleepMinutes] = useState<number | null>(null);
  const activeId = active?.id;
  const activeAudioUrl = active?.audioUrl;
  const activeDuration = active?.durationSeconds;

  const setActive = useCallback((track: PlayerTrack) => {
    setActiveState((previous) => {
      if (previous?.id === track.id) return { ...previous, ...track };
      const audio = audioRef.current;
      audio?.pause();
      setPlaying(false);
      setCurrent(0);
      setDuration(track.durationSeconds ?? 0);
      setSleepMinutes(null);
      return track;
    });
  }, []);

  useEffect(() => {
    if (!activeId) return;
    setBookmarked(readSet(`${VANI_STORAGE_PREFIX}:bookmarks`).has(activeId));
    setCompleted(readSet(`${VANI_STORAGE_PREFIX}:completed`).has(activeId));
    localStorage.setItem(`${VANI_STORAGE_PREFIX}:last-track`, activeId);
    const audio = audioRef.current;
    if (!audio || !activeAudioUrl) return;
    audio.pause();
    audio.src = activeAudioUrl;
    audio.preload = "metadata";
    const saved = Number(localStorage.getItem(`${VANI_STORAGE_PREFIX}:resume:${activeId}`) || "0");
    const restore = () => {
      if (saved > 0 && Number.isFinite(saved) && saved < audio.duration) audio.currentTime = saved;
    };
    audio.addEventListener("loadedmetadata", restore, { once: true });
    return () => audio.removeEventListener("loadedmetadata", restore);
  }, [activeAudioUrl, activeId]);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) audio.playbackRate = speed;
  }, [speed]);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = volume;
      audio.muted = muted;
    }
  }, [volume, muted]);

  useEffect(() => {
    if (sleepMinutes == null) return;
    const timer = window.setTimeout(() => {
      audioRef.current?.pause();
      setPlaying(false);
      setSleepMinutes(null);
    }, sleepMinutes * 60_000);
    return () => window.clearTimeout(timer);
  }, [sleepMinutes]);

  const seekBy = useCallback((seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(audio.duration || Infinity, audio.currentTime + seconds));
  }, []);

  const seekTo = useCallback((seconds: number) => {
    const audio = audioRef.current;
    if (audio) audio.currentTime = Math.max(0, Math.min(audio.duration || Infinity, seconds));
  }, []);

  const toggle = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || !active?.audioUrl) return;
    if (audio.paused) void audio.play().catch(() => setPlaying(false));
    else audio.pause();
  }, [active]);

  useEffect(() => {
    if (!active || !("mediaSession" in navigator)) return;
    navigator.mediaSession.metadata = new MediaMetadata({
      title: active.title,
      artist: "Śrīla Prabhupāda",
      album: "Krishna Book Dictation Archive",
    });
    navigator.mediaSession.setActionHandler("play", toggle);
    navigator.mediaSession.setActionHandler("pause", toggle);
    navigator.mediaSession.setActionHandler("seekbackward", () => seekBy(-10));
    navigator.mediaSession.setActionHandler("seekforward", () => seekBy(10));
    navigator.mediaSession.setActionHandler("seekto", (details) => {
      if (typeof details.seekTime === "number") seekTo(details.seekTime);
    });
    return () => {
      for (const action of ["play", "pause", "seekbackward", "seekforward", "seekto"] as MediaSessionAction[]) {
        try { navigator.mediaSession.setActionHandler(action, null); } catch { /* unsupported action */ }
      }
    };
  }, [active, seekBy, seekTo, toggle]);

  const value = useMemo<PlayerValue>(() => ({
    active, playing, current, duration, speed, volume, muted, bookmarked, completed, sleepMinutes,
    setActive,
    toggle,
    seekBy,
    seekTo,
    setSpeed: (next) => setSpeedState(next),
    setVolume: (next) => setVolumeState(next),
    toggleMute: () => setMuted((value) => !value),
    toggleBookmark: () => {
      if (!active) return;
      const next = !bookmarked;
      setBookmarked(next);
      updateSet(`${VANI_STORAGE_PREFIX}:bookmarks`, active.id, next);
    },
    toggleCompleted: () => {
      if (!active) return;
      const next = !completed;
      setCompleted(next);
      updateSet(`${VANI_STORAGE_PREFIX}:completed`, active.id, next);
    },
    setSleepMinutes,
  }), [active, bookmarked, completed, current, duration, muted, playing, seekBy, seekTo, setActive, sleepMinutes, speed, toggle, volume]);

  return (
    <PlayerContext.Provider value={value}>
      {children}
      <audio
        ref={audioRef}
        preload="metadata"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || activeDuration || 0)}
        onTimeUpdate={(event) => {
          const next = event.currentTarget.currentTime;
          setCurrent(next);
          if (!active) return;
          localStorage.setItem(`${VANI_STORAGE_PREFIX}:resume:${active.id}`, String(next));
          localStorage.setItem(`${VANI_STORAGE_PREFIX}:progress:${active.id}`, JSON.stringify({
            position: next,
            duration: event.currentTarget.duration || duration,
            updatedAt: Date.now(),
          }));
          if (event.currentTarget.duration > 0 && next / event.currentTarget.duration >= 0.95 && !completed) {
            setCompleted(true);
            updateSet(`${VANI_STORAGE_PREFIX}:completed`, active.id, true);
          }
        }}
        onEnded={() => {
          setPlaying(false);
          if (active) {
            setCompleted(true);
            updateSet(`${VANI_STORAGE_PREFIX}:completed`, active.id, true);
          }
        }}
      />
      {active ? <VaniMiniPlayer /> : null}
    </PlayerContext.Provider>
  );
}

function useVaniPlayer() {
  const value = useContext(PlayerContext);
  if (!value) throw new Error("Vani player must be inside VaniPlayerProvider");
  return value;
}

function PlayerButtons({ compact = false }: { compact?: boolean }) {
  const player = useVaniPlayer();
  return (
    <div className={compact ? "vani-mini-controls" : "vani-player-controls"}>
      <button type="button" onClick={() => player.seekBy(-10)} aria-label="Back 10 seconds">−10s</button>
      <button className="vani-play-button" type="button" onClick={player.toggle} aria-label={player.playing ? "Pause" : "Play"}>
        {player.playing ? "Pause" : "Play"}
      </button>
      <button type="button" onClick={() => player.seekBy(10)} aria-label="Forward 10 seconds">+10s</button>
    </div>
  );
}

export function VaniTrackPlayer({ track }: { track: PlayerTrack }) {
  const player = useVaniPlayer();
  const setActive = player.setActive;
  useEffect(() => setActive(track), [setActive, track]);
  if (track.availability !== "available" || !track.audioUrl) {
    return <div className="vani-unavailable" role="status">No recording is currently available for this chapter.</div>;
  }
  const shownCurrent = player.active?.id === track.id ? player.current : 0;
  const shownDuration = player.active?.id === track.id ? player.duration : (track.durationSeconds ?? 0);
  return (
    <section className="vani-player-panel" aria-label={`Audio player for ${track.title}`}>
      <PlayerButtons />
      <label className="vani-seek">
        <span className="sr-only">Seek through recording</span>
        <input
          type="range"
          min={0}
          max={Math.max(1, shownDuration)}
          step={1}
          value={Math.min(shownCurrent, Math.max(1, shownDuration))}
          onChange={(event) => player.seekTo(Number(event.target.value))}
        />
        <span aria-live="off">{time(shownCurrent)} / {time(shownDuration)}</span>
      </label>
      <div className="vani-player-options">
        <label>Speed
          <select value={player.speed} onChange={(event) => player.setSpeed(Number(event.target.value))} aria-label="Playback speed">
            {SPEEDS.map((rate) => <option key={rate} value={rate}>{rate}×</option>)}
          </select>
        </label>
        <button type="button" onClick={player.toggleMute}>{player.muted ? "Unmute" : "Mute"}</button>
        <label>Volume
          <input type="range" min={0} max={1} step={0.05} value={player.volume} onChange={(event) => player.setVolume(Number(event.target.value))} aria-label="Volume" />
        </label>
        <label>Sleep
          <select value={player.sleepMinutes ?? ""} onChange={(event) => player.setSleepMinutes(event.target.value ? Number(event.target.value) : null)} aria-label="Sleep timer">
            <option value="">Off</option><option value="15">15 min</option><option value="30">30 min</option><option value="45">45 min</option>
          </select>
        </label>
        <button type="button" aria-pressed={player.bookmarked} onClick={player.toggleBookmark}>
          {player.bookmarked ? "Bookmarked" : "Bookmark"}
        </button>
        <button type="button" aria-pressed={player.completed} onClick={player.toggleCompleted}>
          {player.completed ? "Completed" : "Mark completed"}
        </button>
      </div>
      <div className="vani-player-navigation" aria-label="Available recording navigation">
        {track.previousId ? <Link href={`${VANI_COLLECTION_PATH}/${track.previousId}`}>← Previous available</Link> : <span />}
        {track.nextId ? <Link href={`${VANI_COLLECTION_PATH}/${track.nextId}`}>Next available →</Link> : null}
      </div>
      <p className="hint">No autoplay. Progress, bookmarks, and completion are stored only on this device.</p>
    </section>
  );
}

function VaniMiniPlayer() {
  const player = useVaniPlayer();
  if (!player.active) return null;
  return (
    <aside className="vani-mini-player" aria-label="Now listening">
      <Link href={`${VANI_COLLECTION_PATH}/${player.active.id}`} className="vani-mini-title">
        <span>Now listening</span>
        <strong>{player.active.title}</strong>
      </Link>
      <span className="vani-mini-time">{time(player.current)}</span>
      <PlayerButtons compact />
    </aside>
  );
}
