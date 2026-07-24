"use client";

import { useEffect, useMemo, useState } from "react";
import { Button, Toast, useToast } from "@bhava/ui";
import { PageIntro } from "@/components/page-intro";

type AgeMode = "bal-gopal" | "damodara" | "mixed";

type PlaylistEntry = {
  id: string;
  storyLabel: string;
  mode: AgeMode;
  minutes: number;
  selected: string[];
  notes: string;
  at: string;
};

const PACK_OPTIONS = [
  { id: "story", label: "Story reading", tip: "Shared reading time" },
  { id: "audio", label: "Audio listening", tip: "Narration circle" },
  { id: "coloring", label: "Coloring pages", tip: "Quiet hands" },
  { id: "activity", label: "Activity sheet", tip: "Guided worksheet" },
  { id: "shloka", label: "Śloka card", tip: "When curated" },
];

const PLAYLIST_KEY = "bhava:classroom-playlist";

function modeLabel(mode: AgeMode): string {
  if (mode === "bal-gopal") return "Bal Gopal";
  if (mode === "damodara") return "Dāmodara";
  return "Mixed age";
}

export default function TeachersPage() {
  const [mode, setMode] = useState<AgeMode>("mixed");
  const [selected, setSelected] = useState<string[]>(["story", "audio", "coloring"]);
  const [minutes, setMinutes] = useState(30);
  const [showAnswers, setShowAnswers] = useState(false);
  const [storyLabel, setStoryLabel] = useState("Selected Krishna Book story");
  const [teacherNotes, setTeacherNotes] = useState("");
  const [playlist, setPlaylist] = useState<PlaylistEntry[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const { message, showToast } = useToast();

  useEffect(() => {
    try {
      const raw = JSON.parse(localStorage.getItem(PLAYLIST_KEY) || "[]");
      if (Array.isArray(raw)) setPlaylist(raw);
    } catch {
      setPlaylist([]);
    }
  }, []);

  const guidance = useMemo(() => {
    if (mode === "bal-gopal") {
      return "Ages ~5–8: shorter listen, simple coloring, one gentle activity. Keep answer keys for adults only.";
    }
    if (mode === "damodara") {
      return "Ages ~9–13: full narration, detailed coloring, activity with discussion prompts.";
    }
    return "Mixed class: offer both simple and detailed paths; let children choose coloring depth.";
  }, [mode]);

  const selectedLabels = selected
    .map((id) => PACK_OPTIONS.find((option) => option.id === id)?.label ?? id)
    .join(", ");

  const previewText = useMemo(() => {
    return [
      "Bhāva class-pack preview",
      "Steward: Svarna Gauranga Das",
      `Story: ${storyLabel}`,
      `Class group: ${modeLabel(mode)}`,
      `Lesson duration: ${minutes} minutes`,
      `Selected assets: ${selectedLabels || "none"}`,
      "",
      "Teacher notes:",
      teacherNotes.trim() || "(none)",
      "",
      "Print this page for a classroom handout. This is a printable HTML/text preview — not a PDF export.",
    ].join("\n");
  }, [mode, minutes, selectedLabels, storyLabel, teacherNotes]);

  const persistPlaylist = (next: PlaylistEntry[]) => {
    setPlaylist(next);
    localStorage.setItem(PLAYLIST_KEY, JSON.stringify(next));
  };

  return (
    <>
      <PageIntro
        eyebrow="For teachers"
        title="Age-aware class packs with calm clarity."
        body="Compose a printable plan for Bal Gopal, Dāmodara, or mixed-age groups. Answer keys stay separated from the child view."
      />
      <section className="section">
        <div className="container teacher-stack">
          <section className="teacher-panel no-print">
            <h2>1 · Choose an age mode</h2>
            <div className="mode-grid">
              {([
                ["bal-gopal", "Bal Gopal", "Younger children"],
                ["damodara", "Dāmodara", "Older children"],
                ["mixed", "Mixed age", "Whole class"],
              ] as const).map(([value, label, tip]) => (
                <button
                  key={value}
                  type="button"
                  className={`mode-card${mode === value ? " is-active" : ""}`}
                  onClick={() => setMode(value)}
                >
                  <strong>{label}</strong>
                  <span>{tip}</span>
                </button>
              ))}
            </div>
            <p className="hint">{guidance}</p>
            <label style={{ display: "grid", gap: ".35rem", marginTop: "1rem", maxWidth: 420 }}>
              Story for this plan
              <input
                value={storyLabel}
                onChange={(event) => setStoryLabel(event.target.value)}
                style={{ minHeight: 44, borderRadius: 12, border: "1px solid var(--bhava-border)", padding: "0 .75rem" }}
              />
            </label>
            <label style={{ display: "inline-flex", gap: ".75rem", alignItems: "center", marginTop: "1rem" }}>
              Lesson timing (minutes)
              <input
                type="number"
                min={10}
                max={90}
                value={minutes}
                onChange={(event) => setMinutes(Number(event.target.value))}
                style={{ minHeight: 44, width: 88, borderRadius: 12, border: "1px solid var(--bhava-border)", padding: "0 .6rem" }}
              />
            </label>
          </section>

          <section className="teacher-panel no-print">
            <h2>2 · Compose the class pack</h2>
            <p className="hint">Tap cards to include them. Selected items become your printable plan.</p>
            <div className="pack-grid">
              {PACK_OPTIONS.map((option) => {
                const on = selected.includes(option.id);
                return (
                  <button
                    key={option.id}
                    type="button"
                    className={`pack-option${on ? " is-on" : ""}`}
                    onClick={() =>
                      setSelected((current) =>
                        on ? current.filter((id) => id !== option.id) : [...current, option.id],
                      )
                    }
                  >
                    {option.label}
                    <span style={{ display: "block", marginTop: ".35rem", fontWeight: 500, color: "var(--bhava-muted)", fontSize: ".85rem" }}>
                      {option.tip}
                    </span>
                  </button>
                );
              })}
            </div>
            <label style={{ display: "grid", gap: ".35rem", marginTop: "1rem" }}>
              Teacher notes
              <textarea
                value={teacherNotes}
                onChange={(event) => setTeacherNotes(event.target.value)}
                rows={4}
                style={{ borderRadius: 12, border: "1px solid var(--bhava-border)", padding: ".75rem", font: "inherit" }}
                placeholder="Timing cues, discussion prompts, or classroom reminders"
              />
            </label>
            <p><strong>Selected:</strong> {selectedLabels || "none yet"}</p>
            <div className="actions" style={{ marginTop: "1rem" }}>
              <Button
                onClick={() => {
                  setShowPreview(true);
                  window.setTimeout(() => window.print(), 50);
                }}
              >
                Print class-pack preview
              </Button>
              <Button
                variant="quiet"
                onClick={() => {
                  const blob = new Blob([previewText], { type: "text/plain;charset=utf-8" });
                  const url = URL.createObjectURL(blob);
                  const anchor = document.createElement("a");
                  anchor.href = url;
                  anchor.download = "bhava-class-pack.txt";
                  anchor.click();
                  URL.revokeObjectURL(url);
                  showToast("Class-pack text exported on this device.");
                }}
              >
                Export as text
              </Button>
              <Button
                variant="quiet"
                onClick={() => {
                  const entry: PlaylistEntry = {
                    id: `${Date.now()}`,
                    storyLabel,
                    mode,
                    minutes,
                    selected: [...selected],
                    notes: teacherNotes,
                    at: new Date().toISOString(),
                  };
                  persistPlaylist([entry, ...playlist]);
                  showToast("Saved to My Classroom Playlist.");
                }}
              >
                Save to classroom playlist
              </Button>
            </div>
          </section>

          <section className={`teacher-panel class-pack-preview${showPreview ? " is-visible" : ""}`}>
            <h2>Class-pack preview</h2>
            <p className="hint no-print">Printable HTML summary for the classroom. This is not a PDF file.</p>
            <dl className="class-pack-dl">
              <div><dt>Story</dt><dd>{storyLabel}</dd></div>
              <div><dt>Class group</dt><dd>{modeLabel(mode)}</dd></div>
              <div><dt>Selected assets</dt><dd>{selectedLabels || "none"}</dd></div>
              <div><dt>Lesson duration</dt><dd>{minutes} minutes</dd></div>
              <div><dt>Teacher notes</dt><dd>{teacherNotes.trim() || "—"}</dd></div>
            </dl>
          </section>

          <section className="teacher-panel no-print">
            <h2>My Classroom Playlist</h2>
            <p className="hint">Saved on this device only. Remove entries anytime.</p>
            {playlist.length === 0 ? (
              <p className="hint">No playlist entries yet.</p>
            ) : (
              <ul className="playlist-list">
                {playlist.map((entry) => (
                  <li key={entry.id}>
                    <div>
                      <strong>{entry.storyLabel}</strong>
                      <span className="hint" style={{ display: "block" }}>
                        {modeLabel(entry.mode)} · {entry.minutes} min · {entry.selected.join(", ") || "no assets"}
                      </span>
                    </div>
                    <Button
                      variant="quiet"
                      onClick={() => {
                        persistPlaylist(playlist.filter((item) => item.id !== entry.id));
                        showToast("Removed playlist entry.");
                      }}
                    >
                      Remove
                    </Button>
                  </li>
                ))}
              </ul>
            )}
            {playlist.length ? (
              <Button
                variant="quiet"
                onClick={() => {
                  persistPlaylist([]);
                  showToast("Classroom playlist cleared.");
                }}
              >
                Clear playlist
              </Button>
            ) : null}
          </section>

          <section className="teacher-panel no-print">
            <h2>3 · Answer key (adults only)</h2>
            <p className="hint">Child-facing activity pages never show this block by default.</p>
            <Button variant="quiet" onClick={() => setShowAnswers((value) => !value)}>
              {showAnswers ? "Hide answer key" : "Reveal answer key"}
            </Button>
            {showAnswers ? (
              <div className="source-boundary" style={{ marginTop: "1rem" }}>
                Use the package <code>manifest.json</code> parent answer key when present. Do not invent answers for missing keys.
              </div>
            ) : null}
          </section>
        </div>
      </section>
      <Toast message={message} />
    </>
  );
}
