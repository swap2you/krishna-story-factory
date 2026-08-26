"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  VANI_COLLECTION_PATH,
  VANI_STORAGE_PREFIX,
  formatVaniDuration,
  type VaniCollection,
} from "@/lib/vani";

export function VaniCollectionCard({ collection }: { collection: VaniCollection }) {
  const [lastTrack, setLastTrack] = useState<string | null>(null);
  useEffect(() => setLastTrack(localStorage.getItem(`${VANI_STORAGE_PREFIX}:last-track`)), []);
  const available = collection.tracks.filter((track) => track.availability === "available");
  const duration = available.reduce((total, track) => total + (track.durationSeconds ?? 0), 0);
  const resume = available.find((track) => track.id === lastTrack);
  return (
    <article className="vani-feature-card">
      <div className="vani-feature-art" aria-hidden="true" />
      <div>
        <p className="eyebrow">Available collection</p>
        <h2>{collection.title}</h2>
        <p>
          Hear the Krishna Book dictations in canonical chapter order. Gaps remain visible and honest;
          available recordings are presented as restored listening editions.
        </p>
        <div className="vani-feature-meta">
          <span><strong>{available.length}</strong> available</span>
          <span><strong>{formatVaniDuration(duration)}</strong> listening</span>
        </div>
        <div className="actions">
          <Link className="bhava-button bhava-button--accent" href={VANI_COLLECTION_PATH}>Browse the archive</Link>
          {resume ? (
            <Link className="bhava-button bhava-button--quiet" href={`${VANI_COLLECTION_PATH}/${resume.id}`}>
              Continue: {resume.title}
            </Link>
          ) : null}
        </div>
      </div>
    </article>
  );
}
