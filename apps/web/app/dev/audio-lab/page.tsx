"use client";

import { useEffect, useRef, useState } from "react";

type Probe = {
  label: string;
  src: string;
  readyState: number;
  networkState: number;
  currentSrc: string;
  currentTime: number;
  duration: number;
  paused: boolean;
  error: string | null;
};

/**
 * Local diagnostic lab for DEF-06. Excluded from primary nav and sitemap.
 * Compare A: FastAPI B: Next proxy C: native controls D: blob object URL.
 */
export default function AudioLabPage() {
  const [story, setStory] = useState("001");
  const [log, setLog] = useState<string[]>([]);
  const [probes, setProbes] = useState<Probe[]>([]);
  const blobUrl = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (blobUrl.current) URL.revokeObjectURL(blobUrl.current);
    };
  }, []);

  function push(msg: string) {
    setLog((prev) => [`${new Date().toISOString()} ${msg}`, ...prev].slice(0, 40));
  }

  async function run() {
    const api = process.env.NEXT_PUBLIC_BHAVA_API_ORIGIN || "http://127.0.0.1:8000";
    const nextSrc = `/api/v1/stories/${story}/assets/narration.mp3`;
    const apiSrc = `${api}/api/v1/stories/${story}/assets/narration.mp3`;
    push(`Probing story ${story}`);

    const head = await fetch(nextSrc, { method: "HEAD" });
    push(`HEAD next ${head.status} ct=${head.headers.get("content-type")} cl=${head.headers.get("content-length")}`);
    const ranged = await fetch(nextSrc, { headers: { Range: "bytes=0-1023" } });
    push(`Range next ${ranged.status} cr=${ranged.headers.get("content-range")}`);

    if (blobUrl.current) URL.revokeObjectURL(blobUrl.current);
    const full = await fetch(nextSrc);
    const blob = await full.blob();
    blobUrl.current = URL.createObjectURL(blob);
    push(`Blob bytes=${blob.size}`);

    const cases = [
      { label: "A FastAPI direct", src: apiSrc },
      { label: "B Next media route", src: nextSrc },
      { label: "C Native controls (Next)", src: nextSrc },
      { label: "D Blob object URL", src: blobUrl.current },
    ];

    const nextProbes: Probe[] = [];
    for (const item of cases) {
      const audio = new Audio();
      audio.preload = "auto";
      audio.src = item.src;
      try {
        await audio.play();
        await new Promise((r) => setTimeout(r, 1200));
      } catch (err) {
        push(`${item.label} play error: ${err instanceof Error ? err.message : String(err)}`);
      }
      nextProbes.push({
        label: item.label,
        src: item.src,
        readyState: audio.readyState,
        networkState: audio.networkState,
        currentSrc: audio.currentSrc,
        currentTime: audio.currentTime,
        duration: audio.duration || 0,
        paused: audio.paused,
        error: audio.error ? String(audio.error.code) : null,
      });
      audio.pause();
    }
    setProbes(nextProbes);
  }

  return (
    <main className="container" style={{ padding: "2rem 0 4rem" }}>
      <p className="eyebrow">Local diagnostic · not in nav</p>
      <h1>Audio laboratory</h1>
      <p>Compare FastAPI, Next proxy, native controls, and blob fallback for narration playback.</p>
      <label>
        Story{" "}
        <select value={story} onChange={(e) => setStory(e.target.value)}>
          {["001", "002", "003", "004", "005", "006", "007"].map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </label>{" "}
      <button type="button" onClick={() => void run()}>Run probes</button>
      <section style={{ marginTop: "1.5rem" }}>
        <h2>Results</h2>
        <pre style={{ whiteSpace: "pre-wrap", background: "#0b1a2b", color: "#f4efe6", padding: "1rem" }}>
          {JSON.stringify(probes, null, 2)}
        </pre>
      </section>
      <section>
        <h2>C · Native controls</h2>
        {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
        <audio controls preload="metadata" src={`/api/v1/stories/${story}/assets/narration.mp3`} />
      </section>
      <section>
        <h2>Log</h2>
        <ul>{log.map((line) => <li key={line}><code>{line}</code></li>)}</ul>
      </section>
    </main>
  );
}
