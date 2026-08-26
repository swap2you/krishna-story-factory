"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  VANI_COLLECTION_PATH,
  VANI_STORAGE_PREFIX,
  filterVaniTracks,
  formatVaniDuration,
  type VaniCollection,
  type VaniFilter,
  type VaniProgress,
} from "@/lib/vani";

const FILTERS: { value: VaniFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "available", label: "Available" },
  { value: "unavailable", label: "Unavailable" },
  { value: "bookmarked", label: "Bookmarked" },
  { value: "completed", label: "Completed" },
];

function storedSet(key: string): Set<string> {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || "[]");
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
}

function storedProgress(id: string): VaniProgress | null {
  try {
    const value = JSON.parse(localStorage.getItem(`${VANI_STORAGE_PREFIX}:progress:${id}`) || "null");
    return value && Number.isFinite(value.position) ? value : null;
  } catch {
    return null;
  }
}

export function VaniCatalog({ collection }: { collection: VaniCollection }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<VaniFilter>("all");
  const [bookmarked, setBookmarked] = useState<Set<string>>(new Set());
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  const [progress, setProgress] = useState<Record<string, VaniProgress>>({});
  const [lastTrack, setLastTrack] = useState<string | null>(null);

  useEffect(() => {
    const refresh = () => {
      setBookmarked(storedSet(`${VANI_STORAGE_PREFIX}:bookmarks`));
      setCompleted(storedSet(`${VANI_STORAGE_PREFIX}:completed`));
      setLastTrack(localStorage.getItem(`${VANI_STORAGE_PREFIX}:last-track`));
      setProgress(Object.fromEntries(collection.tracks.flatMap((track) => {
        const value = storedProgress(track.id);
        return value ? [[track.id, value]] : [];
      })));
    };
    refresh();
    window.addEventListener("bhava:vani-state", refresh);
    window.addEventListener("storage", refresh);
    return () => {
      window.removeEventListener("bhava:vani-state", refresh);
      window.removeEventListener("storage", refresh);
    };
  }, [collection.tracks]);

  const filtered = useMemo(
    () => filterVaniTracks(collection.tracks, query, filter, bookmarked, completed),
    [bookmarked, collection.tracks, completed, filter, query],
  );
  const available = collection.tracks.filter((track) => track.availability === "available").length;
  const totalSeconds = collection.tracks.reduce((sum, track) => sum + (track.durationSeconds ?? 0), 0);
  const continueTrack = collection.tracks.find((track) => track.id === lastTrack && track.availability === "available");

  return (
    <>
      <div className="vani-catalog-summary">
        <div><strong>{available}</strong><span> recordings available</span></div>
        <div><strong>{collection.tracks.length - available}</strong><span> honestly unavailable</span></div>
        <div><strong>{formatVaniDuration(totalSeconds)}</strong><span> available listening</span></div>
        <div><strong>{completed.size}</strong><span> completed on this device</span></div>
      </div>
      {continueTrack ? (
        <Link className="bhava-button bhava-button--accent vani-continue" href={`${VANI_COLLECTION_PATH}/${continueTrack.id}`}>
          Continue listening: {continueTrack.title}
        </Link>
      ) : null}
      <div className="vani-catalog-tools">
        <label className="vani-search">
          <span>Search chapters and titles</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Chapter number or title"
          />
        </label>
        <div className="vani-filters" role="group" aria-label="Filter recordings">
          {FILTERS.map((item) => (
            <button
              type="button"
              key={item.value}
              aria-pressed={filter === item.value}
              onClick={() => setFilter(item.value)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <p className="hint" aria-live="polite">{filtered.length} of {collection.tracks.length} chapters shown</p>
      <div className="vani-track-grid">
        {filtered.map((track) => {
          const itemProgress = progress[track.id];
          const denominator = itemProgress?.duration || track.durationSeconds || 0;
          const percent = denominator ? Math.min(100, Math.round(((itemProgress?.position ?? 0) / denominator) * 100)) : 0;
          return (
            <article className="vani-track-card" key={track.id} data-availability={track.availability}>
              <div className="vani-track-heading">
                <span className="vani-chapter">{track.id === "00" ? "Introduction · 00" : `Chapter ${track.chapterStart ?? track.id}`}</span>
                <span className={`vani-status vani-status--${track.availability}`}>
                  {track.availability === "available" ? "Available" : "Recording unavailable"}
                </span>
              </div>
              <h2>{track.title}</h2>
              <p>{formatVaniDuration(track.durationSeconds)}{track.restored ? " · Restored listening edition" : ""}</p>
              {track.relatedStoryId ? <p className="vani-related-badge">Related Bhāva story</p> : null}
              {track.availability === "available" ? (
                <>
                  <div className="vani-progress" aria-label={`${percent}% listened`}><span style={{ width: `${percent}%` }} /></div>
                  <div className="vani-card-actions">
                    <Link href={`${VANI_COLLECTION_PATH}/${track.id}`}>{percent > 0 ? "Continue listening" : "Listen"}</Link>
                    {bookmarked.has(track.id) ? <span>Bookmarked</span> : null}
                    {completed.has(track.id) ? <span>Completed</span> : null}
                  </div>
                </>
              ) : (
                <p className="vani-unavailable-note">No play control is shown because no verified recording is available.</p>
              )}
            </article>
          );
        })}
      </div>
      {filtered.length === 0 ? <div className="coming">No chapters match this search and filter.</div> : null}
    </>
  );
}
